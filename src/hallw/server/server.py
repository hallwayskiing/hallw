import socketio
import uvicorn

from hallw.server.socket_routes import sio


# --- Main ---
def main():
    """Main entry point for the Uvicorn server."""
    app = socketio.ASGIApp(sio)
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
