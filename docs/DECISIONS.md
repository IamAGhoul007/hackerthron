# Decisions

1. **Streamlit Frontend vs HTML/JS**: Per user request, the application was changed from HTML/JS to Streamlit for simplicity and a Python-only stack.
2. **Auth & SSO Removed**: Per user request, mock Auth and SSO features were removed from the `sample_app` to focus purely on core logic.
3. **Embeddings**: By default, `sentence-transformers` is used locally to remove API key requirements.
4. **LLM**: Gemini is used by default with `google-genai` SDK.
