class StockPulseException(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(message)


class NewsSearchException(StockPulseException):
    def __init__(self, ticker: str, detail: str = ""):
        super().__init__(
            message=f"News fetch failed for {ticker}. {detail}",
            code="NEWS_FAILED"
        )


class LLMServiceException(StockPulseException):
    def __init__(self, op: str, detail: str = ""):
        super().__init__(
            message=f"LLM failed: {op}. {detail}",
            code="LLM_FAILED"
        )


class VectorStoreException(StockPulseException):
    def __init__(self, op: str, detail: str = ""):
        super().__init__(
            message=f"Vector store failed: {op}. {detail}",
            code="VECTOR_FAILED"
        )


class TickerNotFoundException(StockPulseException):
    def __init__(self, ticker: str):
        super().__init__(
            message=f"No data found for ticker: {ticker}",
            code="TICKER_NOT_FOUND"
        )