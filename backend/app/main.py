from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import document, ocr, verification, dashboard, address, verification_logs

app = FastAPI(
    title="KYC Verification Setup G13-M10",
    description="AI-Powered KYC Verification System with Document Detection, OCR, and Face Verification",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Since you are opening index.html this will prevent CORS blocks
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(document.router, prefix="/api/v1")
app.include_router(ocr.router, prefix="/api/v1")
app.include_router(verification.router, prefix="/api/v1")
app.include_router(address.router, prefix="/api/v1")
app.include_router(verification_logs.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1/dashboard")


@app.get("/health")
def health():
    return {"status": "ok"}
