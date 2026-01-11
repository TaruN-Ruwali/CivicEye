from backend.server import create_app
import sys

print("Initializing run.py...")
if __name__ == "__main__":
    print("Starting server in main block...")
    try:
        print("Creating Flask app...")
        app = create_app()
        print("Calling app.run()...")
        app.run(port=5000, debug=False)
        print("app.run() returned.")
    except Exception as e:
        print(f"Error starting server: {e}")
    print("End of script.")
