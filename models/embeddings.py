import numpy as np
from typing import List, Any
from openai import AzureOpenAI
from config.config import config
import logging

class AzureEmbeddingModel:
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=config.AZURE_OPENAI_EMBEDDING_ENDPOINT,
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version=config.AZURE_OPENAI_EMBEDDING_API_VERSION
        )
        self.deployment_name = config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        try:
            response = self.client.embeddings.create(
                model=self.deployment_name,
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        
        except Exception as e:
            logging.error(f"Error generating embeddings: {str(e)}")
            return []
    
    def get_single_embedding(self, text: str) -> List[float]:
        embeddings = self.get_embeddings([text])
        return embeddings[0] if embeddings else []