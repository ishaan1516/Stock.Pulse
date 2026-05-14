import logging
from supabase import create_client
from app.config import get_settings
from app.core.exceptions import VectorStoreException
from datetime import date

logger = logging.getLogger(__name__)


class StockRepository:
    def __init__(self):
        s = get_settings()
        self.client = create_client(s.SUPABASE_URL, s.SUPABASE_SERVICE_KEY)

    async def store(
        self,
        ticker: str,
        company: str,
        summary: str,
        direction: str,
        score: int,
        embedding: list[float]
    ):
        try:
            self.client.table("stock_summaries").insert({
                "ticker": ticker,
                "company": company,
                "summary": summary,
                "direction": direction,
                "score": score,
                "period_end": date.today().isoformat(),
                "embedding": embedding
            }).execute()
            logger.info(f"Stored summary for {ticker}")
        except Exception as e:
            raise VectorStoreException("store", str(e))

    async def similarity_search(
        self,
        ticker: str,
        embedding: list[float],
        limit: int = 3
    ) -> list:
        try:
            result = self.client.rpc(
                "match_stock_summaries",
                {
                    "query_embedding": embedding,
                    "ticker_filter": ticker,
                    "match_count": limit
                }
            ).execute()
            return result.data or []
        except Exception as e:
            logger.warning(f"Similarity search failed for {ticker}: {e}")
            return []

    async def get_history(
        self,
        ticker: str,
        limit: int = 10
    ) -> list:
        try:
            result = self.client.table("stock_summaries")\
                .select("*")\
                .eq("ticker", ticker)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            return result.data or []
        except Exception as e:
            logger.warning(f"Get history failed for {ticker}: {e}")
            return []