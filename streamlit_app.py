import streamlit as st
import requests
import uuid

import os

# Configuration
API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://localhost:{API_PORT}/api"

st.set_page_config(page_title="ReleaseIQ", page_icon="🧠", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
<style>
    .stChatFloatingInputContainer { padding-bottom: 20px; }
    .stChatMessage { border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .stChatMessage.user { background-color: #f0f2f6; }
    .stChatMessage.assistant { background-color: #ffffff; border: 1px solid #e0e0e0; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .quick-action-btn { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 15px; padding: 5px 15px; cursor: pointer; font-size: 0.9em; margin-right: 5px; }
    .quick-action-btn:hover { background-color: #e9ecef; }
</style>
""", unsafe_allow_html=True)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quick_action" not in st.session_state:
    st.session_state.quick_action = None

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8636/8636979.png", width=60) # Brain icon
    st.title("ReleaseIQ")
    st.markdown("Your AI assistant for **Release Knowledge** and **Troubleshooting**.")
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

st.title("🧠 ReleaseIQ Chat")
st.caption("Ask me about recent releases, bug tickets, or trace a code issue!")

for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🧠"
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

# Quick Actions
if not st.session_state.messages:
    st.markdown("### Suggested queries:")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Why did auth break?"):
            st.session_state.quick_action = "Why did auth break?"
    with col2:
        if st.button("Summarize NPAY-123"):
            st.session_state.quick_action = "Summarize NPAY-123"
    with col3:
        if st.button("Latest release blockers?"):
            st.session_state.quick_action = "What are the latest release blockers?"

# Input
prompt = st.chat_input("Describe the issue...")
if st.session_state.quick_action:
    prompt = st.session_state.quick_action
    st.session_state.quick_action = None

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🧠"):
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
