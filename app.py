
import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Nova AI",
    page_icon="✨",
    layout="centered"
)

# Custom styling

# Custom styling
st.markdown("""
<style>
    /* Main page */
    .stApp {
        background-color: #F5F7FC;
        color: #1E293B;
    }

    /* Main title */
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        color: #1D4ED8;
        margin-bottom: 0;
    }

    .subtitle {
        text-align: center;
        color: #475569;
        font-size: 16px;
        margin-bottom: 25px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #E8EEFA;
    }

    [data-testid="stSidebar"] * {
        color: #1E293B;
    }

    /* Main content text */
    .stApp p,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp label {
        color: #1E293B;
    }

    /* Chat message cards */
    [data-testid="stChatMessage"] {
        background-color: #FFFFFF;
        border: 1px solid #DCE4F2;
        border-radius: 14px;
        padding: 14px;
        color: #1E293B;
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
    }

    [data-testid="stChatInput"] textarea {
        color: #1E293B !important;
        background-color: #FFFFFF !important;
        -webkit-text-fill-color: #1E293B !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #64748B !important;
        -webkit-text-fill-color: #64748B !important;
    }

    /* Buttons */
    .stButton button {
        background-color: #2563EB;
        color: #FFFFFF !important;
        border: none;
        border-radius: 10px;
        padding: 8px 14px;
    }

    .stButton button p {
        color: #FFFFFF !important;
    }

    .stButton button:hover {
        background-color: #1D4ED8;
        border: 1px solid #1D4ED8;
    }

    /* Code blocks */
    .stApp pre,
    .stApp code {
        background-color: #E9EEF7;
        color: #1E293B;
    }

    /* Hide Streamlit branding */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# Read the API key
api_key = os.getenv("GROQ_API_KEY")

# Create Groq client only if a key exists
client = Groq(api_key=api_key) if api_key else None

# Initialize chat state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chats" not in st.session_state:
    st.session_state.chats = {}

if "chat_id" not in st.session_state:
    st.session_state.chat_id = 1

if "next_chat_id" not in st.session_state:
    st.session_state.next_chat_id = 2

# Sidebar
with st.sidebar:
    st.title("✨ Nova AI")
    st.caption("Your AI assistant")

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.chats[st.session_state.chat_id] = (
            st.session_state.messages
        )
        st.session_state.chat_id = st.session_state.next_chat_id
        st.session_state.next_chat_id += 1
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("Recent Chats")

    # Display previous conversations
    for chat_id in sorted(st.session_state.chats.keys(), reverse=True):
        chat_messages = st.session_state.chats[chat_id]
        first_user_message = next(
            (
                msg["content"]
                for msg in chat_messages
                if msg["role"] == "user"
            ),
            "New conversation"
        )

        label = first_user_message[:25]
        if len(first_user_message) > 25:
            label += "..."

        if st.button(
            label,
            key=f"chat_{chat_id}",
            use_container_width=True
        ):
            st.session_state.chats[st.session_state.chat_id] = (
                st.session_state.messages
            )
            st.session_state.chat_id = chat_id
            st.session_state.messages = (
                st.session_state.chats[chat_id].copy()
            )
            st.rerun()

    st.divider()
    st.caption("Powered by Groq")

# Main interface
st.markdown('<div class="main-title">✨ Nova AI</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Ask anything. Learn anything.</div>',
    unsafe_allow_html=True
)

# Show a helpful message if the key is missing
if not api_key:
    st.error(
        "GROQ_API_KEY was not found. Add it to your .env file "
        "in the same folder as app.py, then restart the app."
    )
    st.stop()

# Welcome screen
if not st.session_state.messages:
    st.markdown("### How can I help you today?")
    st.write("Ask a question, learn a concept, or brainstorm an idea.")

    cols = st.columns(2)

    if cols[0].button("💻 Explain a coding concept", use_container_width=True):
        st.session_state.pending_prompt = (
            "Explain a programming concept for a beginner."
        )
        st.rerun()

    if cols[1].button("📚 Help me study", use_container_width=True):
        st.session_state.pending_prompt = (
            "Help me study a difficult topic step by step."
        )
        st.rerun()

# Display existing conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle suggested prompts
prompt = st.session_state.pop("pending_prompt", None)

# Chat input
user_prompt = st.chat_input("Message Nova AI...")

if user_prompt:
    prompt = user_prompt

# Process a new message
if prompt:
    # Save and display the user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Nova is thinking..."):
                # Send the conversation history to Groq
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are Nova AI, a helpful, friendly "
                                "and accurate AI assistant. Explain "
                                "difficult topics clearly and step by step."
                            )
                        },
                        *[
                            {
                                "role": message["role"],
                                "content": message["content"]
                            }
                            for message in st.session_state.messages
                        ]
                    ],
                    temperature=0.7,
                    max_completion_tokens=2048
                )

                answer = response.choices[0].message.content

                if not answer:
                    answer = "I couldn't generate a response. Please try again."

                st.markdown(answer)

                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

        except Exception as e:
            st.error(
                "Nova AI couldn't generate a response. "
                "Please check your API key, model availability, "
                "internet connection, and Groq usage limits."
            )
            st.caption(f"Technical details: {e}")

    # Save the current conversation
    st.session_state.chats[st.session_state.chat_id] = (
        st.session_state.messages.copy()
    )
