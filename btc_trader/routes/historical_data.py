from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

router = APIRouter()

class HistoricalDataRequest(BaseModel):
    period_days: int = 365
    interval: str = "1d"

@router.post("/api/historical-data", response_model=dict)
async def get_historical_data(request: HistoricalDataRequest):
    try:
        print(f"Fetching historical data for {request.period_days} days with interval {request.interval}")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.period_days)
        
        print(f"Date range: {start_date} to {end_date}")
        
        # Fetch BTC-USD data from Yahoo Finance
        btc = yf.Ticker("BTC-USD")
        df = btc.history(
            start=start_date,
            end=end_date,
            interval=request.interval
        )
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found for the specified period")

        # Convert dates to ISO format strings
        dates = df.index.strftime('%Y-%m-%d').tolist()
        prices = df['Close'].tolist()
        volumes = df['Volume'].tolist()

        print(f"Fetched {len(dates)} data points")
        
        response_data = {
            "dates": dates,
            "prices": prices,
            "volumes": volumes
        }
        
        print("Response data sample:", {
            "dates": dates[:3],
            "prices": prices[:3],
            "volumes": volumes[:3]
        })
        
        return response_data

    except Exception as e:
        print(f"Error fetching historical data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch historical data: {str(e)}"
        ) 