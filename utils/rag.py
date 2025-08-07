# utils/rag.py
import os
import pickle
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from models.embeddings import AzureEmbeddingModel
import PyPDF2
import docx
import logging
import requests
from io import BytesIO

class DocumentProcessor:
    def __init__(self):
        self.embedding_model = AzureEmbeddingModel()
        self.default_pdf_url = "https://s2.q4cdn.com/299287126/files/doc_financials/2023/ar/Amazon-com-Inc-2023-Annual-Report.pdf"
    
    def load_default_pdf(self) -> str:
        """Load the default Amazon annual report PDF"""
        try:
            response = requests.get(self.default_pdf_url)
            response.raise_for_status()
            
            text = ""
            with BytesIO(response.content) as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logging.error(f"Error loading default PDF: {e}")
            return ""
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logging.error(f"Error extracting PDF text: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logging.error(f"Error extracting DOCX text: {e}")
            return ""
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logging.error(f"Error extracting TXT text: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks with overlap"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks

class VectorStore:
    def __init__(self, store_path: str = "./vector_store"):
        self.store_path = store_path
        self.embedding_model = AzureEmbeddingModel()
        self.documents = []
        self.embeddings = []
        self.load_store()
        
        # Initialize with default document if store is empty
        if not self.documents:
            self.initialize_with_default()
    
    def initialize_with_default(self):
        """Initialize the vector store with the default Amazon report"""
        processor = DocumentProcessor()
        default_text = processor.load_default_pdf()
        if default_text:
            chunks = processor.chunk_text(default_text)
            documents = [{
                'content': chunk,
                'source': 'Amazon-com-Inc-2023-Annual-Report.pdf',
                'chunk_id': i,
                'metadata': {'file_type': 'pdf', 'is_default': True}
            } for i, chunk in enumerate(chunks)]
            self.add_documents(documents)
    
    def load_store(self):
        """Load existing vector store"""
        try:
            if os.path.exists(f"{self.store_path}/documents.pkl"):
                with open(f"{self.store_path}/documents.pkl", 'rb') as f:
                    self.documents = pickle.load(f)
                with open(f"{self.store_path}/embeddings.pkl", 'rb') as f:
                    self.embeddings = pickle.load(f)
        except Exception as e:
            logging.error(f"Error loading vector store: {e}")
    
    def save_store(self):
        """Save vector store"""
        try:
            os.makedirs(self.store_path, exist_ok=True)
            with open(f"{self.store_path}/documents.pkl", 'wb') as f:
                pickle.dump(self.documents, f)
            with open(f"{self.store_path}/embeddings.pkl", 'wb') as f:
                pickle.dump(self.embeddings, f)
        except Exception as e:
            logging.error(f"Error saving vector store: {e}")
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to vector store"""
        texts = [doc['content'] for doc in documents]
        embeddings = self.embedding_model.get_embeddings(texts)
        
        for doc, embedding in zip(documents, embeddings):
            self.documents.append(doc)
            self.embeddings.append(embedding)
        
        self.save_store()
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if not self.documents:
            return []
        
        query_embedding = self.embedding_model.get_single_embedding(query)
        if not query_embedding:
            return []
        
        similarities = cosine_similarity([query_embedding], self.embeddings)[0]
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                **self.documents[idx],
                'similarity': similarities[idx]
            })
        
        return results

class RAGSystem:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStore()
        self.financial_keywords = [
            "revenue", "income", "profit", "AWS", "segment", "growth",
            "earnings", "EBITDA", "cash flow", "operating", "margin",
            "investment", "shareholder", "dividend", "stock", "forecast",
            "guidance", "financial", "metrics", "quarterly", "annual"
        ]

    
    def process_and_store_documents(self, file_paths: List[str]):
        """Process and store documents in vector store"""
        documents = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                continue
            
            # Extract text based on file type
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext == '.pdf':
                text = self.document_processor.extract_text_from_pdf(file_path)
            elif file_ext == '.docx':
                text = self.document_processor.extract_text_from_docx(file_path)
            elif file_ext == '.txt':
                text = self.document_processor.extract_text_from_txt(file_path)
            else:
                continue
            
            # Chunk the text
            chunks = self.document_processor.chunk_text(text)
            
            # Create document objects
            for i, chunk in enumerate(chunks):
                documents.append({
                    'content': chunk,
                    'source': file_path,
                    'chunk_id': i,
                    'metadata': {'file_type': file_ext, 'is_default': False}
                })
        
        # Add to vector store
        self.vector_store.add_documents(documents)
        return len(documents)
    
    def retrieve_relevant_context(self, query: str, top_k: int = 3) -> Tuple[str, bool]:
        """Retrieve relevant context for RAG, return context and whether it's financial"""
        results = self.vector_store.search(query, top_k)
        
        if not results:
            return "", False
        
        is_financial = any(keyword in query.lower() for keyword in self.financial_keywords)
        
        context = "Relevant information from documents:\n\n"
        for i, result in enumerate(results, 1):
            source_name = os.path.basename(result['source'])
            context += f"Source {i} (from {source_name}):\n"
            context += f"{result['content']}\n\n"
        
        return context, is_financial