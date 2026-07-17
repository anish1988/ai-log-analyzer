from fastapi import FastAPI

app = FastAPI(title="AI Log Analyzer API")


@app.get("/health")
def health():
    return {"status": "ok"}