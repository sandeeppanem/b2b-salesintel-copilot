# Sales/CS PTB Agent

A conversational AI agent for sales and customer success teams. Ask natural language questions about upsell, cross-sell, prospecting, churn risk, and more. The agent uses LLMs, SHAP explanations, and business context to provide actionable, explainable insights.

---

## Features
- Conversational UI (chat) for natural language Q&A
- Handles 11+ sales/CS workflows (see example prompts below)
- Contextual memory for follow-up questions (per session)
- Explains recommendations with business context
- Uses OpenAI, FastAPI, Snowflake, and React + MUI

---

## Example Prompts
- Show me my top 5 cross-sell opportunities and why.
- Which accounts are most likely to buy Product X and why?
- Why is Account Y a good upsell target for Product Z?
- What are the top cross-sell opportunities in my territory?
- Which accounts are at risk of churn and why?
- What should I do next for Account Z?
- Generate a personalized pitch for Acme Corp for Product Y.
- Why did the model score Account X low for Product Y?
- What features are driving the upsell score for Account A?
- Show me all accounts with high cross-sell potential for Product Z in the healthcare segment.
- Summarize my top opportunities and risks for this quarter.

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <your-repo-directory>
```

### 2. Backend Setup (Python)

#### a. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

#### b. Install backend dependencies
```bash
pip install -r backend/requirements.txt
```

#### c. Set environment variables (Snowflake & OpenAI)
```bash
export SNOWFLAKE_USER=your_user
export SNOWFLAKE_PASSWORD=your_password
export SNOWFLAKE_ACCOUNT=your_account
export SNOWFLAKE_DATABASE=your_database
export SNOWFLAKE_SCHEMA=your_schema
export SNOWFLAKE_WAREHOUSE=your_warehouse
export OPENAI_API_KEY=your_openai_api_key
```

#### d. Run the backend server
```bash
uvicorn backend.main:app --reload
```

The backend will be available at [http://localhost:8000](http://localhost:8000)

---

### 3. Frontend Setup (React)

#### a. Install frontend dependencies
```bash
cd frontend
npm install
```

#### b. Start the frontend app
```bash
npm start
```

The frontend will be available at [http://localhost:3000](http://localhost:3000) (or another port if 3000 is in use).

---

## Usage
1. Open the frontend in your browser.
2. Enter your User ID to start a session.
3. Ask any of the example questions (or your own) in the chat.
4. The agent will respond with actionable, explainable insights, and you can ask follow-up questions naturally.

---

## Project Structure
```
backend/              # FastAPI backend
  main.py             # Main backend code
  requirements.txt    # Backend dependencies
frontend/             # React frontend
  src/                # Frontend source code
  package.json        # Frontend dependencies
README.md             # This file
```

---

## Notes
- The agent uses OpenAI's GPT-4 for intent/entity extraction and explanations.
- No chat history is stored in a database; context is per session/tab.
- Make sure your Snowflake and OpenAI credentials are correct and have access.

---

## License
MIT (or your chosen license) 