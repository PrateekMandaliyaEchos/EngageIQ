"""FastAPI application setup."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.core.config import get_settings
from src.api.routes import health, campaigns, analytics

# Load settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["campaigns"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

# Serve static files (React frontend)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the React frontend."""
        return FileResponse("static/index.html")
    
    @app.get("/{path:path}")
    async def serve_frontend_routes(path: str):
        """Serve React frontend for all other routes (SPA routing)."""
        # Check if it's an API route
        if path.startswith("api/"):
            return {"error": "API route not found"}
        
        # Check if the file exists in static directory
        static_path = f"static/{path}"
        if os.path.exists(static_path) and os.path.isfile(static_path):
            return FileResponse(static_path)
        
        # For SPA routing, serve index.html
        return FileResponse("static/index.html")

