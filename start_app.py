import subprocess
import sys
import os

def main():
    """Start the Mind Mate AI Chatbot application"""
    print("Starting Mind Mate AI Chatbot...")
    print("Initializing backend server...")
    
    # Change to the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Add the current directory to Python path
    sys.path.append(project_dir)
    
    # Start the backend server
    try:
        # Run the FastAPI application
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.app:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], env={**os.environ, "PYTHONPATH": project_dir}, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting the application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down the application...")
        sys.exit(0)

if __name__ == "__main__":
    main()