import uvicorn
from fastapi import FastAPI, Request, Response
from app.api.v1.api import api_router
from datetime import datetime
from app.core.config import settings
from app import __version__
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.rate_limit import limiter


app = FastAPI(title=settings.project_name, version=__version__, debug=settings.debug)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
@limiter.limit("60/minute", key_func=get_remote_address)
async def root(request: Request, response: Response):
    return {
        "message": "Welcome to Todo API",
        "version": __version__,
        "docs": "/docs",
    }


@app.get("/health")
@limiter.limit("60/minute", key_func=get_remote_address)
async def health(request: Request, response: Response):
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


app.include_router(
    api_router, prefix=settings.api_v1_str
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
