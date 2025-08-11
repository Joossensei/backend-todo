import uvicorn
from fastapi import FastAPI, Depends
from app.api.v1.api import api_router
from datetime import datetime
from app.core.config import settings
from app import __version__
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.project_name, version=__version__, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Todo API",
        "version": __version__,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


app.include_router(
    api_router, prefix=settings.api_v1_str
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
