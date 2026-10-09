# ReleaseIQ

An AI Release Knowledge and Troubleshooting Assistant.

## Quick Start
1. Ensure Python 3.11+ is installed.
2. Run `python run.py` (it will create a `.env` and prompt you for keys).
3. Fill in your `GROQ_API_KEY` in `.env`.
4. Run `python run.py` again. It will:
   - Create a virtual environment
   - Install dependencies
   - Ingest the Jira and Code corpora
   - Start the FastAPI backend and Streamlit frontend.

## Architecture
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Decisions
See [docs/DECISIONS.md](docs/DECISIONS.md)
