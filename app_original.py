import streamlit as st
import os
from models.llm import AzureOpenAIModel
from utils.memory import ChatMemory
from utils.rag import RAGSystem
from utils.web_search import WebSearchTool
from config.config import config
import uuid

# Page configuration
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔬",
    layout="wide"
)

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'memory' not in st.session_state:
    st.session_state.memory = ChatMemory(st.session_state.session_id)
if 'llm_model' not in st.session_state:
    st.session_state.llm_model = AzureOpenAIModel()
if 'rag_system' not in st.session_state:
    st.session_state.rag_system = RAGSystem()
if 'web_search' not in st.session_state:
    st.session_state.web_search = WebSearchTool()

def main():
    st.title("🔬 AI Research Assistant")
    st.subheader("Your intelligent companion for research, document analysis, and knowledge discovery")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Validate API keys
        if not config.validate():
            st.error("⚠️ Please set your API keys in environment variables:")
            st.code("""
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_key
TAVILY_API_KEY=your_key
            """)
            st.stop()
        
        st.success("✅ API keys configured")
        
        # Response mode
        response_mode = st.selectbox(
            "Response Mode",
            ["Detailed", "Concise"],
            help="Choose between detailed explanations or concise answers"
        )
        
        # Tools configuration
        st.header("Tools")
        use_rag = st.checkbox("Use Document Knowledge", value=True)
        use_web_search = st.checkbox("Enable Web Search", value=True)
        
        # Document upload
        if use_rag:
            st.header("📚 Document Upload")
            st.info("Default document: Amazon 2023 Annual Report is always available")
            uploaded_files = st.file_uploader(
                "Upload additional documents (PDF, DOCX, TXT)",
                type=['pdf', 'docx', 'txt'],
                accept_multiple_files=True
            )
            
            if uploaded_files:
                if st.button("Process Documents"):
                    with st.spinner("Processing documents..."):
                        # Save uploaded files temporarily
                        temp_paths = []
                        for uploaded_file in uploaded_files:
                            temp_path = f"./temp/{uploaded_file.name}"
                            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            temp_paths.append(temp_path)
                        
                        # Process documents
                        doc_count = st.session_state.rag_system.process_and_store_documents(temp_paths)
                        st.success(f"✅ Processed {doc_count} document chunks from uploaded files")
                        
                        # Clean up temp files
                        for path in temp_paths:
                            try:
                                os.remove(path)
                            except:
                                pass
        
        # Chat management
        st.header("Chat Management")
        if st.button("Clear Chat History"):
            st.session_state.memory.clear_memory()
            st.rerun()
    
    # Main chat interface
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        messages = st.session_state.memory.get_messages(include_metadata=True)
        for message in messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if message.get("metadata", {}).get("sources"):
                    with st.expander("Sources"):
                        st.write(message["metadata"]["sources"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about research, documents, or any topic..."):
        # Add user message to memory
        st.session_state.memory.add_message("user", prompt)
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response, sources = generate_response(
                    prompt, 
                    response_mode, 
                    use_rag, 
                    use_web_search
                )
            
            st.write(response)
            
            if sources:
                with st.expander("Sources"):
                    st.write(sources)
        
        # Add assistant response to memory
        metadata = {"sources": sources} if sources else {}
        st.session_state.memory.add_message("assistant", response, metadata)

def generate_response(prompt: str, response_mode: str, use_rag: bool, use_web_search: bool) -> tuple:
    """Generate response using available tools"""
    context = ""
    sources = []
    needs_web_search = False
    
    # Get RAG context
    if use_rag:
        rag_context, is_financial = st.session_state.rag_system.retrieve_relevant_context(prompt)
        if rag_context:
            context += rag_context
            # Check if the response is coming from default document
            if "Amazon-com-Inc-2023-Annual-Report.pdf" in rag_context:
                sources.append("📄 Amazon 2023 Annual Report")
            else:
                sources.append("📄 Uploaded Documents")
        
        # If it's a financial query but we didn't find good context, flag for web search
        if is_financial and not rag_context:
            needs_web_search = True
    
    # Get web search context if enabled and needed
    if use_web_search and (needs_web_search or should_use_web_search(prompt)):
        search_results = st.session_state.web_search.search(prompt)
        web_context = st.session_state.web_search.format_search_results(search_results)
        context += "\n" + web_context
        if search_results.get("results"):
            sources.extend([f"🌐 {result.get('title', 'Financial Source')}" for result in search_results["results"][:3]])
    
    # Prepare specialized system prompt for financial queries
    system_prompt = f"""You are an AI Financial Research Assistant specializing in Amazon investor relations and financial analysis.

When answering financial questions:
1. Be precise with numbers and metrics
2. Compare year-over-year changes when relevant
3. Explain financial terms if needed
4. Highlight important trends
5. Always cite your sources

Response Mode: {response_mode}
- Concise: Focus on key numbers and brief explanations
- Detailed: Include full context, comparisons, and analysis

Available Context:
{context if context else "No specific context available. I'll answer based on general knowledge."}
"""


    
    # Get chat history
    messages = st.session_state.memory.get_messages()
    messages.append({"role": "user", "content": prompt})
    
    # Set max tokens based on response mode
    max_tokens = config.CONCISE_MAX_TOKENS if response_mode == "Concise" else config.DETAILED_MAX_TOKENS
    
    # Generate response
    response = st.session_state.llm_model.generate_response(
        messages=messages,
        system_prompt=system_prompt,
        max_tokens=max_tokens,
        temperature=0.7
    )
    
    return response, sources

def should_use_web_search(prompt: str) -> bool:
    """Determine if web search should be used for this prompt"""
    web_search_indicators = [
        "latest", "recent", "current", "news", "today", "2024", "2025",
        "what's happening", "breaking", "update", "trend", "stock price",
        "analyst", "rating", "target price", "Q1", "Q2", "Q3", "Q4"
    ]
    return any(indicator in prompt.lower() for indicator in web_search_indicators)

if __name__ == "__main__":
    main()