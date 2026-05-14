import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from app.config import get_settings
from app.models.schemas import StockRatingResponse
from app.core.exceptions import LLMServiceException

logger = logging.getLogger(__name__)

SEARCH_QUERIES_PROMPT = """
Generate exactly 4 specific search queries to find relevant news
for {ticker} ({company}) from the last 7 days.

Cover these angles:
1. Company specific announcements and earnings
2. Sector and industry developments
3. Regulatory or government actions affecting the company
4. Macroeconomic factors relevant to this business

Return only 4 numbered queries. No explanations. No extra text.
"""

WEEKLY_SUMMARY_PROMPT = """
You are a senior equity research analyst.

Analyse these news articles about {company} ({ticker})
and write a factual weekly summary of the most important
developments from the last 7 days.

Focus on: earnings, product launches, regulatory decisions,
leadership changes, partnerships, macro factors.

News articles:
{news_content}

Historical context:
{monthly_context}

Write 3-4 paragraphs. Be specific. No generic statements.
"""

RATING_PROMPT = """
You are a senior equity analyst. Analyse {company} ({ticker}) based on the weekly summary below.

Weekly summary: {weekly_summary}

Historical context: {monthly_context}

SCORING RULES — be specific and decisive:
- Score 9-10: ONLY if there is a major earnings surprise, M&A announcement, CEO resignation, bankruptcy filing, or major regulatory action THIS WEEK
- Score 7-8: Clear positive or negative catalyst — beat/miss expectations, new product launch, significant contract win/loss, major lawsuit
- Score 5-6: Moderate news — routine business updates, minor partnerships, sector news with indirect impact
- Score 3-4: Mostly quiet week — no significant company-specific news, general market noise only
- Score 1-2: Completely routine — no news of any significance whatsoever

Direction rules:
- POSITIVE: News is net favourable for stock price
- NEGATIVE: News is net unfavourable for stock price  
- MIXED: Genuinely conflicting signals of similar magnitude
- NEUTRAL: No meaningful directional signal

Do NOT default to score 6. Be honest about what the news actually says.
If it was a big week give a high score. If it was a quiet week give a low score.

{format_instructions}

Return ONLY valid JSON. No explanation before or after.
"""

class LLMService:
    def __init__(self):
        s = get_settings()
        self.llm = ChatOpenAI(
            model=s.LLM_MODEL,
            openai_api_key=s.OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=s.LLM_TEMPERATURE,
            default_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "StockPulse"
            }
        )

    async def generate_search_queries(
        self,
        ticker: str,
        company: str
    ) -> list[str]:
        try:
            chain = (
                ChatPromptTemplate.from_template(SEARCH_QUERIES_PROMPT)
                | self.llm
                | StrOutputParser()
            )
            result = chain.invoke({"ticker": ticker, "company": company})
            lines = result.strip().split("\n")
            queries = []
            for line in lines:
                line = line.strip()
                if line and line[0].isdigit():
                    query = line.split(".", 1)[-1].strip()
                    if query:
                        queries.append(query)
            logger.info(f"Generated {len(queries)} queries for {ticker}")
            return queries[:4]
        except Exception as e:
            raise LLMServiceException("generate_search_queries", str(e))

    async def generate_summary(
        self,
        ticker: str,
        company: str,
        news_content: str,
        monthly_context: str
    ) -> str:
        try:
            chain = (
                ChatPromptTemplate.from_template(WEEKLY_SUMMARY_PROMPT)
                | self.llm
                | StrOutputParser()
            )
            result = chain.invoke({
                "ticker": ticker,
                "company": company,
                "news_content": news_content[:8000],
                "monthly_context": monthly_context
            })
            logger.info(f"Generated summary for {ticker}")
            return result
        except Exception as e:
            raise LLMServiceException("generate_summary", str(e))

    async def generate_rating(
        self,
        ticker: str,
        company: str,
        weekly_summary: str,
        monthly_context: str
    ) -> StockRatingResponse:
        try:
            parser = PydanticOutputParser(pydantic_object=StockRatingResponse)
            prompt = ChatPromptTemplate.from_template(RATING_PROMPT)
            prompt = prompt.partial(
                format_instructions=parser.get_format_instructions()
            )
            chain = prompt | self.llm | parser
            result = chain.invoke({
                "ticker": ticker,
                "company": company,
                "weekly_summary": weekly_summary,
                "monthly_context": monthly_context
            })
            logger.info(f"Generated rating for {ticker}: score={result.reaction_score}")
            return result
        except Exception as e:
            raise LLMServiceException("generate_rating", str(e))