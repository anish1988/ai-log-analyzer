from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.ai_analysis import router as ai_analysis_router
from app.auth.dependencies import CurrentUser, get_current_user
from app.api.analysis_history import router as analysis_history_router

from app.api.saved_searches import router as saved_searches_router

app = FastAPI(title="AI Log Analyzer API")

# -------------------------------
# CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Routers
# -------------------------------
from app.api.logs import router as logs_router

@app.get("/api/auth/me")
async def get_me(
    current_user: CurrentUser = Depends(get_current_user),
):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "display_name": current_user.display_name,
        "role": current_user.role,
    }

app.include_router(logs_router, prefix="/api/logs", tags=["logs"],)

app.include_router(
    ai_analysis_router,
)

app.include_router(saved_searches_router,)

app.include_router(analysis_history_router)

@app.get("/health")
def health():
    return {"status": "ok"}