from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app.include_router(logs_router, prefix="/api/logs", tags=["logs"])

@app.get("/health")
def health():
    return {"status": "ok"}