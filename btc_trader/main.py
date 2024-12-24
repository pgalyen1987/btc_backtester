from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from btc_trader.routes import api_router

app = FastAPI(title="BTC Backtester API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "BTC Backtester API"} 