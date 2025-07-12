import streamlit as st
import requests
import json
from typing import List, Dict, Any

# Page configuration
st.set_page_config(
    page_title="Sales/CS PTB Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .example-prompt {
        background-color: #f0f2f6;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.25rem 0;
        font-size: 0.9rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    .user-message {
        background-color: #1f77b4;
        color: white;
        margin-left: auto;
        text-align: right;
    }
    .agent-message {
        background-color: #f0f2f6;
        color: black;
        margin-right: auto;
    }
    .stButton > button {
        width: 100%;
        border-radius: 0.5rem;
    }
    .error-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #c62828;
    }
</style>
""", unsafe_allow_html=True)

# Example prompts
EXAMPLE_PROMPTS = [
    'Show me my top 5 cross-sell opportunities and why.',
    'Which accounts are most likely to buy Product X and why?',
    'Why is Account Y a good upsell target for Product Z?',
    'What are the top cross-sell opportunities in my territory?',
    'Which accounts are at risk of churn and why?',
    'What should I do next for Account Z?',
    'Generate a personalized pitch for Acme Corp for Product Y.',
    'Why did the model score Account X low for Product Y?',
    'What features are driving the upsell score for Account A?',
    'Show me all accounts with high cross-sell potential for Product Z in the healthcare segment.',
    'Summarize my top opportunities and risks for this quarter.'
]

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hi! Ask me anything about your sales and customer success opportunities."
            }
        ]
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'chat_initialized' not in st.session_state:
        st.session_state.chat_initialized = False

def check_backend_health():
    """Check if the backend is running"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_message(message: str, user_id: str) -> str:
    """Send message to backend API"""
    try:
        # Prepare history for backend (last 10 messages)
        history = st.session_state.messages[-10:] if len(st.session_state.messages) > 1 else []
        
        payload = {
            "message": message,
            "user_id": user_id,
            "history": history
        }
        
        response = requests.post(
            "http://localhost:8000/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get("response", "Sorry, I could not get an answer.")
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ **Backend Connection Error**: The backend server is not running. Please start the backend server first using `uvicorn backend.main:app --reload`"
    except requests.exceptions.Timeout:
        return "⏰ **Timeout Error**: The request took too long. Please try again."
    except requests.exceptions.RequestException as e:
        return f"🌐 **Network Error**: {str(e)}"
    except Exception as e:
        return f"❌ **Error**: {str(e)}"

def display_chat_interface():
    """Display the chat interface"""
    st.markdown('<h1 class="main-header">Sales/CS PTB Agent</h1>', unsafe_allow_html=True)
    
    # Check backend health
    if not check_backend_health():
        st.markdown("""
        <div class="error-message">
            <strong>⚠️ Backend Not Running</strong><br>
            The backend server is not running. Please start it first:<br>
            <code>uvicorn backend.main:app --reload</code>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message agent-message">
                    <strong>Agent:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Input area
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_area(
                "Type your question...",
                key="user_input",
                height=100,
                placeholder="Ask me about opportunities, churn risk, or personalized pitches..."
            )
        
        with col2:
            send_button = st.button("Send", type="primary", use_container_width=True)
    
    # Handle send button click
    if send_button and user_input.strip():
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        
        # Show loading spinner
        with st.spinner("Getting response..."):
            # Get response from backend
            response = send_message(user_input.strip(), st.session_state.user_id)
            
            # Add agent response to chat
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Clear input
        st.session_state.user_input = ""
        
        # Rerun to update the display
        st.rerun()

def display_example_prompts():
    """Display example prompts in sidebar"""
    st.sidebar.markdown("### Example Questions")
    st.sidebar.markdown("You can ask questions like:")
    
    for prompt in EXAMPLE_PROMPTS:
        st.sidebar.markdown(f'<div class="example-prompt">💡 {prompt}</div>', unsafe_allow_html=True)

def main():
    """Main application function"""
    initialize_session_state()
    
    # Sidebar for user ID input and examples
    with st.sidebar:
        st.markdown("## Setup")
        
        if not st.session_state.user_id:
            user_id_input = st.text_input("Enter your User ID", key="user_id_input")
            if st.button("Start Chat", type="primary"):
                if user_id_input.strip():
                    st.session_state.user_id = user_id_input.strip()
                    st.session_state.chat_initialized = True
                    st.rerun()
                else:
                    st.error("Please enter a User ID")
        else:
            st.success(f"Logged in as: {st.session_state.user_id}")
            if st.button("Change User ID"):
                st.session_state.user_id = None
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": "Hi! Ask me anything about your sales and customer success opportunities."
                    }
                ]
                st.session_state.chat_initialized = False
                st.rerun()
        
        st.markdown("---")
        display_example_prompts()
    
    # Main content area
    if st.session_state.user_id:
        display_chat_interface()
    else:
        # Welcome screen
        st.markdown('<h1 class="main-header">Sales/CS PTB Agent</h1>', unsafe_allow_html=True)
        
        st.markdown("""
        ### Welcome to the Sales and Customer Success AI Agent!
        
        This intelligent assistant helps you discover opportunities, understand customer behavior, 
        and generate personalized recommendations using advanced machine learning models.
        
        **Features:**
        - 🔍 **Opportunity Discovery**: Find cross-sell, upsell, and prospect opportunities
        - 📊 **Risk Assessment**: Identify accounts at risk of churn
        - 💡 **Explainable AI**: Understand why accounts are recommended
        - 📧 **Personalized Pitches**: Generate tailored sales pitches
        - 📈 **Territory Insights**: Get segment and territory-specific recommendations
        
        **To get started:**
        1. Enter your User ID in the sidebar
        2. Click "Start Chat"
        3. Ask questions about your opportunities and customers
        """)
        
        # Display example prompts in main area as well
        st.markdown("### Example Questions You Can Ask:")
        for i, prompt in enumerate(EXAMPLE_PROMPTS):
            st.markdown(f"**{i+1}.** {prompt}")

if __name__ == "__main__":
    main() 