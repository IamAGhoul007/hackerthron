# ReleaseIQ

An AI Release Knowledge and Troubleshooting Assistant.

## Quick Start
1. Install Python 3.11, 3.12, or 3.13 and ensure it is available as `python` on your PATH.
2. From the project root, run `python run.py`. The script creates a virtual environment and installs dependencies.
3. Fill in your `GROQ_API_KEY` in the generated `.env` file.
4. Run `python run.py` again. It will:
   - Create a virtual environment
   - Install dependencies
   - Ingest the Jira and Code corpora
   - Start the FastAPI backend and Streamlit frontend.

Python 3.14 is not supported by the current Chroma and NumPy combination. The first run also downloads the `all-MiniLM-L6-v2` embedding model, so internet access is required during setup.

## Architecture
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Decisions
See [docs/DECISIONS.md](docs/DECISIONS.md)
