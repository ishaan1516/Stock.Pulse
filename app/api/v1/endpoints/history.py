from fastapi import APIRouter, HTTPException
from app.repositories.stock_repository import StockRepository
import logging

router = APIRouter(prefix="/history", tags=["History"])
logger = logging.getLogger(__name__)


@router.get("/{ticker}")
async def get_history(ticker: str):
    try:
        repo = StockRepository()
        history = await repo.get_history(ticker.upper())
        return {
            "ticker": ticker.upper(),
            "count": len(history),
            "records": history
        }
    except Exception as e:
        logger.error(f"History failed for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")