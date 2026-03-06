import sys
from api.server import start_server

if __name__ == "__main__":
    print("==============================================")
    print("🧠 OFFLINE ATTENTION MAPPING TOOL: WEB MODE")
    print("==============================================")
    print("1. Open your browser to: http://127.0.0.1:5000")
    print("2. Click 'START SESSION' on the website.")
    print("3. Use your computer normally to see the data.")
    print("----------------------------------------------")
    
    try:
        # Start the Flask server (this is your backend)
        start_server()
    except KeyboardInterrupt:
        print("\n[!] Shutting down mapping engine...")
        sys.exit(0)