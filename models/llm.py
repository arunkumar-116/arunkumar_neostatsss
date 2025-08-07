from openai import AzureOpenAI
from typing import List, Dict, Any, Optional
from config.config import config
import logging

class AzureOpenAIModel:
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version=config.AZURE_OPENAI_API_VERSION
        )
        self.deployment_name = config.AZURE_OPENAI_DEPLOYMENT_NAME
        
    def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        try:
            # Add system prompt if provided
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=max_tokens or config.DETAILED_MAX_TOKENS,
                temperature=temperature,
                stream=False
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logging.error(f"Error generating response: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def generate_stream_response(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ):
        try:
            # Add system prompt if provided
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=max_tokens or config.DETAILED_MAX_TOKENS,
                temperature=temperature,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            logging.error(f"Error generating stream response: {str(e)}")
            yield f"Sorry, I encountered an error: {str(e)}"