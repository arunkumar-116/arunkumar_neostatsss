import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    # Azure OpenAI Config
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPENAI_DEPLOYMENT_NAME: str = ""

    # Azure Embedding Config  
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = "text-embedding-3-large-2"
    AZURE_OPENAI_EMBEDDING_ENDPOINT: str = ""
    AZURE_OPENAI_EMBEDDING_API_VERSION: str = "2024-02-01"

    # Tavily API
    TAVILY_API_KEY: str = ""

    # Application Paths
    MAX_HISTORY_LENGTH: int = 20
    VECTOR_DB_PATH: str = "./vector_db"
    DOCUMENTS_PATH: str = "./documents"

    # Token Settings
    CONCISE_MAX_TOKENS: int = 150
    DETAILED_MAX_TOKENS: int = 1000

    def __post_init__(self):
        """Initialize configuration from environment variables or Streamlit secrets"""
        # First try to load from environment variables
        self.AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self.AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
        self.AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
        
        self.AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large-2")
        self.AZURE_OPENAI_EMBEDDING_ENDPOINT = os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT", "")
        self.AZURE_OPENAI_EMBEDDING_API_VERSION = os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION", "2024-02-01")
        
        self.TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
        
        self.MAX_HISTORY_LENGTH = int(os.getenv("MAX_HISTORY_LENGTH", "20"))
        self.VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vector_db")
        self.DOCUMENTS_PATH = os.getenv("DOCUMENTS_PATH", "./documents")
        
        self.CONCISE_MAX_TOKENS = int(os.getenv("CONCISE_MAX_TOKENS", "150"))
        self.DETAILED_MAX_TOKENS = int(os.getenv("DETAILED_MAX_TOKENS", "1000"))
        
        # Try to get from Streamlit secrets if available (for Streamlit Cloud)
        try:
            import streamlit as st
            if hasattr(st, 'secrets'):
                # Azure OpenAI Config
                if "AZURE_OPENAI_ENDPOINT" in st.secrets:
                    self.AZURE_OPENAI_ENDPOINT = st.secrets["AZURE_OPENAI_ENDPOINT"]
                if "AZURE_OPENAI_API_KEY" in st.secrets:
                    self.AZURE_OPENAI_API_KEY = st.secrets["AZURE_OPENAI_API_KEY"]
                if "AZURE_OPENAI_API_VERSION" in st.secrets:
                    self.AZURE_OPENAI_API_VERSION = st.secrets["AZURE_OPENAI_API_VERSION"]
                if "AZURE_OPENAI_DEPLOYMENT_NAME" in st.secrets:
                    self.AZURE_OPENAI_DEPLOYMENT_NAME = st.secrets["AZURE_OPENAI_DEPLOYMENT_NAME"]
                
                # Azure Embedding Config
                if "AZURE_OPENAI_EMBEDDING_DEPLOYMENT" in st.secrets:
                    self.AZURE_OPENAI_EMBEDDING_DEPLOYMENT = st.secrets["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
                if "AZURE_OPENAI_EMBEDDING_ENDPOINT" in st.secrets:
                    self.AZURE_OPENAI_EMBEDDING_ENDPOINT = st.secrets["AZURE_OPENAI_EMBEDDING_ENDPOINT"]
                if "AZURE_OPENAI_EMBEDDING_API_VERSION" in st.secrets:
                    self.AZURE_OPENAI_EMBEDDING_API_VERSION = st.secrets["AZURE_OPENAI_EMBEDDING_API_VERSION"]
                
                # Tavily API
                if "TAVILY_API_KEY" in st.secrets:
                    self.TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
                
                # Application Settings
                if "MAX_HISTORY_LENGTH" in st.secrets:
                    self.MAX_HISTORY_LENGTH = int(st.secrets["MAX_HISTORY_LENGTH"])
                if "VECTOR_DB_PATH" in st.secrets:
                    self.VECTOR_DB_PATH = st.secrets["VECTOR_DB_PATH"]
                if "DOCUMENTS_PATH" in st.secrets:
                    self.DOCUMENTS_PATH = st.secrets["DOCUMENTS_PATH"]
                if "CONCISE_MAX_TOKENS" in st.secrets:
                    self.CONCISE_MAX_TOKENS = int(st.secrets["CONCISE_MAX_TOKENS"])
                if "DETAILED_MAX_TOKENS" in st.secrets:
                    self.DETAILED_MAX_TOKENS = int(st.secrets["DETAILED_MAX_TOKENS"])
                    
        except ImportError:
            # Streamlit not available, continue with environment variables
            pass
        except Exception as e:
            # Error accessing Streamlit secrets, continue with environment variables
            print(f"Warning: Could not access Streamlit secrets: {e}")
            pass

    def validate(self) -> bool:
        """Validate that required configuration is present"""
        required = [
            self.AZURE_OPENAI_ENDPOINT,
            self.AZURE_OPENAI_API_KEY,
            self.TAVILY_API_KEY
        ]
        return all(field.strip() for field in required if field)

    def get_missing_keys(self) -> list:
        """Get list of missing required configuration keys"""
        missing = []
        if not self.AZURE_OPENAI_ENDPOINT.strip():
            missing.append("AZURE_OPENAI_ENDPOINT")
        if not self.AZURE_OPENAI_API_KEY.strip():
            missing.append("AZURE_OPENAI_API_KEY")
        if not self.TAVILY_API_KEY.strip():
            missing.append("TAVILY_API_KEY")
        return missing

# Instantiate config
config = Config()

# Optional: Print configuration status for debugging (remove in production)
if __name__ == "__main__":
    print("Configuration Status:")
    print(f"AZURE_OPENAI_ENDPOINT: {'✓' if config.AZURE_OPENAI_ENDPOINT else '✗'}")
    print(f"AZURE_OPENAI_API_KEY: {'✓' if config.AZURE_OPENAI_API_KEY else '✗'}")
    print(f"TAVILY_API_KEY: {'✓' if config.TAVILY_API_KEY else '✗'}")
    print(f"Configuration valid: {config.validate()}")
    if not config.validate():
        print(f"Missing keys: {config.get_missing_keys()}")