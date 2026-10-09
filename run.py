import sys
import os
import subprocess
import venv
import shutil
from pathlib import Path
import time
import socket

PROJECT_ROOT = Path(__file__).resolve().parent

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def check_python_version():
    if sys.version_info < (3, 11):
        print("\033[91mError: Python 3.11-3.13 is required.\033[0m")
        sys.exit(1)
    if sys.version_info >= (3, 14):
        print("\033[91mError: Python 3.11-3.13 is required; Python 3.14 is not supported yet.\033[0m")
        sys.exit(1)

def setup_venv():
    venv_dir = PROJECT_ROOT / "venv"
    if not venv_dir.exists():
        print("Creating virtual environment...")
        venv.create(venv_dir, with_pip=True)
    
    # Check if we are inside venv
    if sys.prefix == sys.base_prefix:
        print("Restarting inside venv...")
        if os.name == 'nt':
            python_exec = str(venv_dir / "Scripts" / "python.exe")
        else:
            python_exec = str(venv_dir / "bin" / "python")
        subprocess.check_call([python_exec] + sys.argv)
        sys.exit(0)

def install_deps():
    req_file = "requirements.txt"
    hash_file = Path("venv") / ".req_hash"
    
    with open(req_file, "rb") as f:
        current_hash = __import__("hashlib").sha256(f.read()).hexdigest()
        
    if hash_file.exists():
        with open(hash_file, "r") as f:
            if f.read().strip() == current_hash:
                print("Dependencies up to date.")
                return

    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
    
    with open(hash_file, "w") as f:
        f.write(current_hash)

def setup_env():
    if not os.path.exists(".env"):
        if not os.path.exists(".env.example"):
            print("\033[91mError: .env.example is missing from the project root.\033[0m")
            sys.exit(1)
        print("Creating .env from .env.example...")
        shutil.copy(".env.example", ".env")
        print("\033[93mPlease configure API keys in .env\033[0m")

def ensure_dirs():
    dirs = ["data/chroma", "data/cache", "data/logs", "data/jira"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def run():
    os.chdir(PROJECT_ROOT)
    check_python_version()
    setup_venv()
    
    if "--skip-install" not in sys.argv:
        install_deps()
        
    setup_env()
    ensure_dirs()
    
    if "--check" in sys.argv:
        print("\033[92mSetup valid.\033[0m")
        sys.exit(0)
        
    port = 8000
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
        
    while is_port_in_use(port):
        print(f"Port {port} in use, trying {port+1}")
        port += 1

    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Ingest
        from app.ingestion.indexer import Indexer
        force = "--rebuild" in sys.argv
        idx = Indexer()
        idx.rebuild(force=force)

        # Run backend and frontend
        print(f"\033[92mStarting Backend on {port}...\033[0m")
        backend = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(port)])
        
        # Wait for health
        print("\033[94mWaiting for backend to be ready...\033[0m")
        import urllib.request
        import urllib.error
        health_url = f"http://127.0.0.1:{port}/api/health"
        for _ in range(60):
            if backend.poll() is not None:
                print("\033[91mBackend process exited unexpectedly.\033[0m")
                break
            try:
                with urllib.request.urlopen(health_url) as response:
                    if response.status == 200:
                        break
            except urllib.error.URLError:
                pass
            time.sleep(1)
        
        # We need streamlit on a different port, defaults to 8501
        print("\033[92mStarting Streamlit Frontend...\033[0m")
        env = os.environ.copy()
        env["API_PORT"] = str(port)
        frontend = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"], env=env)

        backend.wait()
        frontend.wait()

    except KeyboardInterrupt:
        print("Shutting down...")
        if 'backend' in locals(): backend.kill()
        if 'frontend' in locals(): frontend.kill()

if __name__ == "__main__":
    run()
