from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import List, Optional
import snowflake.connector
import openai
import os
import json

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")

def get_snowflake_connection():
    return snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
        warehouse=SNOWFLAKE_WAREHOUSE
    )

def fetch_opportunities(user_id: str, opportunity_type: str, top_n: int, product_id: Optional[str]=None, segment: Optional[str]=None, territory: Optional[str]=None, account_id: Optional[str]=None):
    conn = get_snowflake_connection()
    cur = conn.cursor()
    query = """
        SELECT account_id, account_name, product_id, product_name, score, opportunity_type, segment, territory
        FROM model_scores
        WHERE user_id = %s AND opportunity_type = %s
    """
    params = [user_id, opportunity_type]
    if product_id:
        query += " AND product_id = %s"
        params.append(product_id)
    if segment:
        query += " AND segment = %s"
        params.append(segment)
    if territory:
        query += " AND territory = %s"
        params.append(territory)
    if account_id:
        query += " AND account_id = %s"
        params.append(account_id)
    query += " ORDER BY score DESC LIMIT %s"
    params.append(top_n)
    cur.execute(query, tuple(params))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def fetch_shap_values(account_id, product_id):
    conn = get_snowflake_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT feature_name, shap_value
        FROM shap_values
        WHERE account_id = %s AND product_id = %s
        ORDER BY ABS(shap_value) DESC
        LIMIT 3
    """, (account_id, product_id))
    features = cur.fetchall()
    cur.close()
    conn.close()
    return features

def fetch_business_context(account_id, product_id):
    conn = get_snowflake_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT context_text
        FROM business_context
        WHERE account_id = %s AND product_id = %s
        LIMIT 1
    """, (account_id, product_id))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else ""

def generate_llm_explanation(account_name, product_name, opportunity_type, top_features, business_context):
    features_str = ", ".join([f"{name} ({value:+.2f})" for name, value in top_features])
    prompt = f"""
Given the following:
- Account: {account_name}
- Product: {product_name}
- Opportunity type: {opportunity_type}
- Top features driving the score: {features_str}
- Business context: {business_context}

Generate a concise, business-friendly explanation of why this account is a good {opportunity_type.replace('_', ' ')} opportunity for this product.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.7
    )
    return response.choices[0].message['content'].strip()

def generate_next_action(top_features, business_context, opportunity_type):
    features_str = ", ".join([f"{name} ({value:+.2f})" for name, value in top_features])
    prompt = f"""
Given the following:
- Opportunity type: {opportunity_type}
- Top features: {features_str}
- Business context: {business_context}

Suggest the next best sales action for the sales rep to take with this account and product. Be specific and actionable.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=60,
        temperature=0.7
    )
    return response.choices[0].message['content'].strip()

def generate_personalized_pitch(account_name, product_name, business_context):
    prompt = f"""
Given the following:
- Account: {account_name}
- Product: {product_name}
- Business context: {business_context}

Generate a personalized sales pitch email for this account and product. Make it relevant, concise, and actionable.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=120,
        temperature=0.7
    )
    return response.choices[0].message['content'].strip()

@app.get("/api/opportunities")
def opportunities(
    user_id: str,
    opportunity_type: str = Query(..., regex="^(cross_sell|upsell|prospect)$"),
    top_n: int = Query(5, ge=1, le=20),
    product_id: Optional[str] = None,
    segment: Optional[str] = None,
    territory: Optional[str] = None,
    account_id: Optional[str] = None
):
    """
    Get top N opportunities for a user, with optional filtering by product, segment, territory, or account.
    """
    results = fetch_opportunities(user_id, opportunity_type, top_n, product_id, segment, territory, account_id)
    if not results:
        raise HTTPException(status_code=404, detail="No opportunities found.")
    response = []
    for account_id, account_name, product_id, product_name, score, opp_type, seg, terr in results:
        top_features = fetch_shap_values(account_id, product_id)
        business_context = fetch_business_context(account_id, product_id)
        explanation = generate_llm_explanation(account_name, product_name, opp_type, top_features, business_context)
        next_action = generate_next_action(top_features, business_context, opp_type)
        response.append({
            "account": account_name,
            "product": product_name,
            "score": float(score),
            "opportunity_type": opp_type,
            "segment": seg,
            "territory": terr,
            "explanation": explanation,
            "next_action": next_action
        })
    return response

@app.get("/api/churn_risk")
def churn_risk(
    user_id: str,
    top_n: int = Query(5, ge=1, le=20),
    segment: Optional[str] = None,
    territory: Optional[str] = None
):
    """
    Get top N accounts at risk of churn for a user, with optional filtering by segment or territory.
    """
    results = fetch_opportunities(user_id, 'churn_risk', top_n, None, segment, territory)
    if not results:
        raise HTTPException(status_code=404, detail="No churn risk accounts found.")
    response = []
    for account_id, account_name, product_id, product_name, score, opp_type, seg, terr in results:
        top_features = fetch_shap_values(account_id, product_id)
        business_context = fetch_business_context(account_id, product_id)
        explanation = generate_llm_explanation(account_name, product_name, opp_type, top_features, business_context)
        response.append({
            "account": account_name,
            "product": product_name,
            "score": float(score),
            "segment": seg,
            "territory": terr,
            "explanation": explanation
        })
    return response

@app.get("/api/summary")
def summary(
    user_id: str
):
    """
    Get a summary of top 3 opportunities and top 2 risks for a user.
    """
    top_opps = fetch_opportunities(user_id, 'cross_sell', 3)
    top_risks = fetch_opportunities(user_id, 'churn_risk', 2)
    opps_response = []
    for account_id, account_name, product_id, product_name, score, opp_type, seg, terr in top_opps:
        top_features = fetch_shap_values(account_id, product_id)
        business_context = fetch_business_context(account_id, product_id)
        explanation = generate_llm_explanation(account_name, product_name, opp_type, top_features, business_context)
        opps_response.append({
            "account": account_name,
            "product": product_name,
            "score": float(score),
            "segment": seg,
            "territory": terr,
            "explanation": explanation
        })
    risks_response = []
    for account_id, account_name, product_id, product_name, score, opp_type, seg, terr in top_risks:
        top_features = fetch_shap_values(account_id, product_id)
        business_context = fetch_business_context(account_id, product_id)
        explanation = generate_llm_explanation(account_name, product_name, opp_type, top_features, business_context)
        risks_response.append({
            "account": account_name,
            "product": product_name,
            "score": float(score),
            "segment": seg,
            "territory": terr,
            "explanation": explanation
        })
    return {"top_opportunities": opps_response, "top_risks": risks_response}

@app.get("/api/pitch")
def personalized_pitch(
    account_id: str,
    product_id: str
):
    """
    Generate a personalized sales pitch for a given account and product.
    """
    conn = get_snowflake_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT account_name, product_name
        FROM model_scores
        WHERE account_id = %s AND product_id = %s
        LIMIT 1
    """, (account_id, product_id))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Account/Product not found.")
    account_name, product_name = row
    business_context = fetch_business_context(account_id, product_id)
    pitch = generate_personalized_pitch(account_name, product_name, business_context)
    return {"account": account_name, "product": product_name, "pitch": pitch}

@app.post("/api/chat")
async def chat(request: Request):
    """
    Conversational endpoint: accepts a user message, uses OpenAI to extract intent and entities,
    routes to the correct backend logic, and returns a conversational response.
    """
    data = await request.json()
    user_message = data.get("message")
    user_id = data.get("user_id")
    history = data.get("history", [])

    system_prompt = '''
You are a helpful sales and customer success assistant.
Given a user message, classify which of the following intents it matches, and extract any relevant parameters:
- top_opportunities (cross_sell, upsell, prospect)
- churn_risk
- summary
- personalized_pitch

Extract parameters such as product, account, segment, territory, top_n, etc.

Return a JSON object like:
{
  "intent": "top_opportunities",
  "opportunity_type": "cross_sell",
  "product": "Product X",
  "segment": "healthcare",
  "top_n": 5,
  "account": null
}
If the user asks for a personalized pitch, set intent to "personalized_pitch" and extract account and product.
If the user asks for churn risk, set intent to "churn_risk".
If the user asks for a summary, set intent to "summary".
'''

    # Build OpenAI messages array with context
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        if msg.get("role") in ("user", "assistant"):
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": f"User message: {user_message}"})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=300,
        temperature=0
    )
    try:
        import json
        intent_data = json.loads(response.choices[0].message['content'])
    except Exception:
        return JSONResponse({"response": "Sorry, I couldn't understand your request."})

    # 2. Route to the correct backend logic
    if intent_data.get("intent") == "top_opportunities":
        result = opportunities(
            user_id=user_id,
            opportunity_type=intent_data.get("opportunity_type", "cross_sell"),
            top_n=intent_data.get("top_n", 5),
            product_id=intent_data.get("product"),
            segment=intent_data.get("segment"),
            territory=intent_data.get("territory"),
            account_id=intent_data.get("account"),
        )
        # Format as conversational response
        if not result:
            return JSONResponse({"response": "No opportunities found for your query."})
        lines = []
        for opp in result:
            lines.append(
                f"• {opp['account']} ({opp['product']}, Score: {opp['score']:.2f}, Industry: {opp.get('industry','N/A')}, Region: {opp.get('territory','N/A')}): {opp['explanation']} Next: {opp['next_action']}"
            )
        return JSONResponse({"response": "\n".join(lines)})

    elif intent_data.get("intent") == "churn_risk":
        result = churn_risk(
            user_id=user_id,
            top_n=intent_data.get("top_n", 5),
            segment=intent_data.get("segment"),
            territory=intent_data.get("territory"),
        )
        if not result:
            return JSONResponse({"response": "No churn risk accounts found for your query."})
        lines = []
        for risk in result:
            lines.append(
                f"• {risk['account']} ({risk['product']}, Score: {risk['score']:.2f}, Industry: {risk.get('industry','N/A')}, Region: {risk.get('territory','N/A')}): {risk['explanation']}"
            )
        return JSONResponse({"response": "\n".join(lines)})

    elif intent_data.get("intent") == "summary":
        result = summary(user_id=user_id)
        if not result:
            return JSONResponse({"response": "No summary available."})
        opps = result.get("top_opportunities", [])
        risks = result.get("top_risks", [])
        lines = ["Top Opportunities:"]
        for opp in opps:
            lines.append(f"• {opp['account']} ({opp['product']}, Score: {opp['score']:.2f}): {opp['explanation']}")
        lines.append("Top Risks:")
        for risk in risks:
            lines.append(f"• {risk['account']} ({risk['product']}, Score: {risk['score']:.2f}): {risk['explanation']}")
        return JSONResponse({"response": "\n".join(lines)})

    elif intent_data.get("intent") == "personalized_pitch":
        result = personalized_pitch(
            account_id=intent_data.get("account"),
            product_id=intent_data.get("product"),
        )
        if not result:
            return JSONResponse({"response": "No pitch could be generated for your query."})
        return JSONResponse({"response": result.get("pitch")})

    else:
        return JSONResponse({"response": "Sorry, I couldn't understand your request."}) 