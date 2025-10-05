"""Run the FastAPI server with settings from config.yaml."""

import uvicorn
from src.core.config import get_settings


def run_fastapi_server():
    """Run FastAPI app with uvicorn ASGI server using config.yaml settings."""
    # Load settings from config.yaml
    app_config = get_settings()

    print(f"🚀 Starting {app_config.app_name} v{app_config.app_version}")
    print(f"📍 Server: http://{app_config.api_host}:{app_config.api_port}")
    print(f"📚 API Docs: http://{app_config.api_host}:{app_config.api_port}/docs")
    print(f"🔧 Environment: {app_config.environment}")

    uvicorn.run(
        "src.api.app:app",
        host=app_config.api_host,
        port=app_config.api_port,
        reload=app_config.debug,
        log_level="info"
    )


if __name__ == "__main__":
    run_fastapi_server()
