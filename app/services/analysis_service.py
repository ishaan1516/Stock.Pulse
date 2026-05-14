import logging
from app.services.search_service import SearchService
from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService
from app.repositories.stock_repository import StockRepository
from app.core.exceptions import NewsSearchException

logger = logging.getLogger(__name__)


class AnalysisService:
    def __init__(self):
        self.search = SearchService()
        self.llm = LLMService()
        self.embedding = EmbeddingService()
        self.repo = StockRepository()

    async def analyse(self, ticker: str, company: str):
        logger.info(f"Analysis started: {ticker}")

        # Step 1 — generate search queries
        queries = await self.llm.generate_search_queries(ticker, company)

        # Step 2 — fetch news in parallel
        news = await self.search.fetch_parallel(queries)
        if not news.strip():
            raise NewsSearchException(ticker)

        # Step 3 — get historical context from vector store
        preview_embedding = await self.embedding.embed(news[:500])
        history = await self.repo.similarity_search(ticker, preview_embedding)
        monthly_context = self._format_history(history)

        # Step 4 — generate weekly summary
        summary = await self.llm.generate_summary(
            ticker, company, news, monthly_context
        )

        # Step 5 — generate structured rating
        rating = await self.llm.generate_rating(
            ticker, company, summary, monthly_context
        )

        # Step 6 — store in vector database
        summary_embedding = await self.embedding.embed(summary)
        await self.repo.store(
            ticker=ticker,
            company=company,
            summary=summary,
            direction=rating.direction,
            score=rating.reaction_score,
            embedding=summary_embedding
        )

        logger.info(
            f"Analysis complete: {ticker} "
            f"score={rating.reaction_score} "
            f"direction={rating.direction}"
        )
        return rating

    def _format_history(self, items: list) -> str:
        if not items:
            return "No historical context available."
        return "\n\n".join([
            f"[{i.get('period_end')}] "
            f"Score:{i.get('score')} "
            f"{i.get('direction')}\n"
            f"{i.get('summary', '')[:300]}"
            for i in items
        ])