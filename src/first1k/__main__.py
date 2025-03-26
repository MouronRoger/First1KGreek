"""Main entry point for First1KGreek Browser."""

from .server.server import run_server
from .config import PORT

def main():
    """Main entry point."""
    try:
        run_server()
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Error: Port {PORT} is already in use.")
            print("Try closing any running instances or use the following command to force close:")
            print(f"lsof -i :{PORT} | grep Python | awk '{{print $2}}' | xargs kill -9")
        else:
            print(f"Error starting server: {str(e)}")
    except Exception as e:
        print(f"Error starting server: {str(e)}")

if __name__ == "__main__":
    main() 