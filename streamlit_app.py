import streamlit as st
import requests
import uuid

import os

# Configuration
API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://localhost:{API_PORT}/api"

st.set_page_config(page_title="ReleaseIQ | Enterprise AI", page_icon="✨", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main App Background - subtle gradient */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #e2e8f0 0%, #f8fafc 100%);
    }

    /* Sidebar glass effect */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Elegant headers */
    h1, h2, h3 {
        color: #1e293b !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px;
    }
    
    /* Modern Chat Bubbles */
    .stChatMessage {
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(255, 255, 255, 0.8);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(8px);
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    /* Floating Input container */
    .stChatFloatingInputContainer {
        padding-bottom: 30px;
        background: transparent;
    }
    
    /* Chat Input Box styling */
    [data-testid="stChatInput"] {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 24px;
        border: 1px solid rgba(203, 213, 225, 0.8);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    [data-testid="stChatInput"]:focus-within {
        border-color: #6366f1;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.2);
        transform: translateY(-2px);
    }
    
    /* Button enhancements */
    .stButton > button {
        border-radius: 12px;
        font-weight: 500;
        transition: all 0.2s ease;
        border: 1px solid #e2e8f0;
        background: white;
        color: #334155;
    }
    
    .stButton > button:hover {
        background: #f8fafc;
        border-color: #cbd5e1;
        transform: scale(1.02);
    }
    
    .stButton > button:active {
        transform: scale(0.98);
    }
    
    /* Quick Actions (columns buttons) styling */
    div[data-testid="stHorizontalBlock"] .stButton > button {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        color: #475569;
        width: 100%;
    }
    
    div[data-testid="stHorizontalBlock"] .stButton > button:hover {
        border-color: #6366f1;
        color: #4f46e5;
        box-shadow: 0 4px 6px rgba(99,102,241,0.1);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        border-radius: 12px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8636/8636979.png", width=60) # Brain icon
    st.title("ReleaseIQ")
    st.markdown("Your enterprise AI assistant for **Release Intelligence** and **Troubleshooting**.")
    st.divider()
    
    st.subheader("System Status")
    try:
        health = requests.get(f"{API_URL}/health").json()
        if health["status"] == "ok":
            st.success("🟢 API Connected")
        else:
            st.warning(f"🟡 {health.get('message', 'API degraded')}")
    except:
        st.error("🔴 API Offline")
        
    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

st.title("✨ ReleaseIQ Intelligence")
st.caption("Enterprise-grade insights into your releases, tickets, and code issues.")

for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if msg.get("route"):
                st.caption(f"Route: {msg['route']} | Confidence: {msg['confidence']:.2f}")
            if msg.get("mismatch") and msg["mismatch"]["detected"]:
                st.error(f"⚠️ **Possible release inconsistency detected!**\n\n{msg['mismatch'].get('explanation', '')}")
            if msg.get("sources"):
                with st.expander("Sources"):
                    for s in msg["sources"]:
                        if s["type"] == "jira":
                            st.markdown(f"**Jira {s['id']}** ({s['fix_version']}): {s['title']}")
                        else:
                            st.markdown(f"**Code** `{s['path']}` (Lines {s.get('lines')}):")
                        st.code(s['snippet'])
            if msg.get("escalation_note"):
                st.info(f"**Support Note:**\n\n{msg['escalation_note']}")

# Input
prompt = st.chat_input("Describe the issue...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="✨"):
        with st.spinner("Thinking..."):
            try:
                res = requests.post(f"{API_URL}/chat", json={
                    "session_id": st.session_state.session_id,
                    "message": prompt
                }).json()
                
                answer = res.get("answer", "Error retrieving answer")
                st.markdown(answer)
                
                msg_data = {
                    "role": "assistant",
                    "content": answer,
                    "route": res.get("route"),
                    "confidence": res.get("confidence", 0.0),
                    "sources": res.get("sources", []),
                    "mismatch": res.get("possible_mismatch"),
                    "escalation_note": res.get("escalation_note")
                }
                
                if msg_data["route"]:
                    st.caption(f"Route: {msg_data['route']} | Confidence: {msg_data['confidence']:.2f}")
                if msg_data["mismatch"] and msg_data["mismatch"].get("detected"):
                    st.error(f"⚠️ **Possible release inconsistency detected!**\n\n{msg_data['mismatch'].get('explanation', '')}")
                if msg_data["sources"]:
                    with st.expander("Sources"):
                        for s in msg_data["sources"]:
                            if s["type"] == "jira":
                                st.markdown(f"**Jira {s['id']}** ({s['fix_version']}): {s['title']}")
                            else:
                                st.markdown(f"**Code** `{s['path']}` (Lines {s.get('lines')}):")
                            st.code(s['snippet'])
                if msg_data["escalation_note"]:
                    st.info(f"**Support Note:**\n\n{msg_data['escalation_note']}")
                    
                st.session_state.messages.append(msg_data)
                
            except Exception as e:
                st.error(f"Error calling API: {e}")
