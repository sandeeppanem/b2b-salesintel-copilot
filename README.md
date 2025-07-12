# Sales/CS PTB Agent

A conversational AI agent for sales and customer success teams. Ask natural language questions about upsell, cross-sell, prospecting, churn risk, and more. The agent uses LLMs, SHAP explanations, and business context to provide actionable, explainable insights.

---

## Features
- Conversational UI (chat) for natural language Q&A
- Handles 11+ sales/CS workflows (see example prompts below)
- Contextual memory for follow-up questions (per session)
- Explains recommendations with business context
- Uses OpenAI, FastAPI, Snowflake, and Streamlit

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

## Quick Start

### 1. Test Your Setup
```bash
python test_setup.py
```

### 2. Easy Startup
```bash
python run_app.py
```

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <your-repo-directory>
```

### 2. Environment Setup

#### a. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

#### b. Install all dependencies
```bash
pip install -r requirements.txt
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

### 3. Running the Application

#### Option A: Using the startup script (Recommended)
```bash
python run_app.py
```

#### Option B: Manual startup

##### a. Start the backend server (Terminal 1)
```bash
uvicorn backend.main:app --reload
```

The backend will be available at [http://localhost:8000](http://localhost:8000)

##### b. Start the Streamlit frontend (Terminal 2)
```bash
streamlit run frontend/streamlit_app.py
```

The frontend will be available at [http://localhost:8501](http://localhost:8501)

---

## Usage
1. Open the Streamlit app in your browser (usually http://localhost:8501).
2. Enter your User ID in the sidebar to start a session.
3. Ask any of the example questions (or your own) in the chat.
4. The agent will respond with actionable, explainable insights, and you can ask follow-up questions naturally.

---

## Project Structure
```
backend/              # FastAPI backend
  main.py             # Main backend code
  requirements.txt    # Backend dependencies
frontend/             # Streamlit frontend
  streamlit_app.py    # Main Streamlit application
  .streamlit/         # Streamlit configuration
requirements.txt      # All Python dependencies
run_app.py           # Startup script
test_setup.py        # Setup verification script
README.md             # This file
```

---

## Troubleshooting

### Test Your Setup
Run the test script to verify everything is working:
```bash
python test_setup.py
```

### Common Issues
- **Backend not running**: Start with `uvicorn backend.main:app --reload`
- **Missing packages**: Install with `pip install -r requirements.txt`
- **Environment variables**: Make sure all Snowflake and OpenAI credentials are set

---

## Notes
- The agent uses OpenAI's GPT-4 for intent/entity extraction and explanations.
- No chat history is stored in a database; context is per session/tab.
- Make sure your Snowflake and OpenAI credentials are correct and have access.
- All dependencies are now Python packages, making setup simpler.

---

## License
MIT (or your chosen license) 