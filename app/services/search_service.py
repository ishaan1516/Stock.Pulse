import asyncio
import logging
from tavily import TavilyClient
from app.config import get_settings

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self):
        self.client = TavilyClient(get_settings().TAVILY_API_KEY)

    async def fetch_parallel(self, queries: list[str]) -> str:
        async def search_one(query: str) -> str:
            try:
                results = self.client.search(
                    query,
                    max_results=4,
                    search_depth="basic"
                )
                return self._format(results.get("results", []))
            except Exception as e:
                logger.warning(f"Search failed for query '{query}': {e}")
                return ""

        tasks = [search_one(q) for q in queries]
        results = await asyncio.gather(*tasks)
        combined = "\n\n---\n\n".join(r for r in results if r)
        logger.info(f"Fetched news from {len(queries)} queries")
        return combined

    def _format(self, results: list) -> str:
        return "\n".join([
            f"Title: {r.get('title', '')}\n"
            f"Content: {r.get('content', '')}\n"
            f"URL: {r.get('url', '')}"
            for r in results
        ])