# from tavily import TavilyClient
# from config.config import config
# import logging
# from typing import List, Dict, Any

# class WebSearchTool:
#     def __init__(self):
#         self.client = TavilyClient(api_key=config.TAVILY_API_KEY)
    
#     def search(self, query: str, max_results: int = 3) -> Dict[str, Any]:
#         """Perform web search using Tavily"""
#         try:
#             response = self.client.search(
#                 query=query,
#                 search_depth="advanced",
#                 max_results=max_results
#             )
#             return response
#         except Exception as e:
#             logging.error(f"Error performing web search: {e}")
#             return {"results": []}
    
#     def format_search_results(self, search_results: Dict[str, Any]) -> str:
#         """Format search results for context"""
#         if not search_results.get("results"):
#             return "No web search results found."
        
#         formatted_results = "Recent web search results:\n\n"
#         for i, result in enumerate(search_results["results"], 1):
#             formatted_results += f"Result {i}:\n"
#             formatted_results += f"Title: {result.get('title', 'N/A')}\n"
#             formatted_results += f"Content: {result.get('content', 'N/A')}\n"
#             formatted_results += f"URL: {result.get('url', 'N/A')}\n\n"
        
#         return formatted_results


# utils/web_search.py
from tavily import TavilyClient
from config.config import config
import logging
from typing import List, Dict, Any

class WebSearchTool:
    def __init__(self):
        self.client = TavilyClient(api_key=config.TAVILY_API_KEY)
        self.financial_sites = [
            "investor.amazon.com",
            "sec.gov",
            "finance.yahoo.com",
            "bloomberg.com",
            "reuters.com",
            "marketwatch.com",
            "wsj.com",
            "ft.com",
            "investopedia.com"
        ]
    
    def search(self, query: str, max_results: int = 3) -> Dict[str, Any]:
        """Perform web search using Tavily with focus on financial sites"""
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=self.financial_sites,
                include_answer=True,
                include_raw_content=True
            )
            return response
        except Exception as e:
            logging.error(f"Error performing web search: {e}")
            return {"results": []}
    
    def format_search_results(self, search_results: Dict[str, Any]) -> str:
        """Format search results for context"""
        if not search_results.get("results"):
            return "No relevant financial information found."
        
        formatted_results = "Financial web search results:\n\n"
        for i, result in enumerate(search_results["results"], 1):
            formatted_results += f"Source {i}:\n"
            formatted_results += f"Title: {result.get('title', 'N/A')}\n"
            formatted_results += f"URL: {result.get('url', 'N/A')}\n"
            formatted_results += f"Content: {result.get('content', 'N/A')[:500]}...\n\n"
        
        # Include Tavily's answer if available
        if search_results.get("answer"):
            formatted_results += f"Quick Answer: {search_results['answer']}\n"
        
        return formatted_results