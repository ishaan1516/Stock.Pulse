import requests
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.settings = get_settings()

    async def embed(self, text: str) -> list[float]:
        try:
            headers = {
                "Authorization": f"Bearer {self.settings.HF_API_KEY}"
            }
            response = requests.post(
                self.settings.HF_MODEL_URL,
                headers=headers,
                json={"inputs": text[:512]},
                timeout=30
            )

            if response.status_code != 200:
                logger.warning(f"HF API returned {response.status_code}, using zero vector")
                return [0.0] * 384

            result = response.json()

            # Handle nested list output — average pooling
            if isinstance(result, list) and isinstance(result[0], list):
                import numpy as np
                return list(np.mean(result, axis=0))

            return result

        except Exception as e:
            logger.warning(f"Embedding failed, using zero vector: {e}")
            return [0.0] * 384