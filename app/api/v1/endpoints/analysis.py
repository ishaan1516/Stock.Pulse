from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.models.schemas import AnalysisRequest, StockRatingResponse
from app.services.analysis_service import AnalysisService
from app.core.exceptions import StockPulseException
from app.core.middleware import limiter
from app.dependencies import get_analysis_service
import logging

router = APIRouter(prefix="/analysis", tags=["Analysis"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=StockRatingResponse)
@limiter.limit("5/minute")
async def analyse_stock(
    request: Request,
    body: AnalysisRequest,
    service: AnalysisService = Depends(get_analysis_service)
):
    try:
        return await service.analyse(
            ticker=body.ticker.upper(),
            company=body.company
        )
    except StockPulseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"Unexpected error for {body.ticker}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Analysis failed"}
        )