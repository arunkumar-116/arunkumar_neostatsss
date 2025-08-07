from typing import List, Dict, Any
import json
import os
from datetime import datetime

class ChatMemory:
    def __init__(self, session_id: str, max_length: int = 20):
        self.session_id = session_id
        self.max_length = max_length
        self.memory_file = f"./memory/chat_{session_id}.json"
        self.messages = self.load_memory()
    
    def load_memory(self) -> List[Dict[str, Any]]:
        """Load chat history from file"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading memory: {e}")
        return []
    
    def save_memory(self):
        """Save chat history to file"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to memory"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        
        # Keep only the last max_length messages
        if len(self.messages) > self.max_length:
            self.messages = self.messages[-self.max_length:]
        
        self.save_memory()
    
    def get_messages(self, include_metadata: bool = False) -> List[Dict[str, Any]]:
        """Get messages in OpenAI format"""
        if include_metadata:
            return self.messages
        return [{"role": msg["role"], "content": msg["content"]} for msg in self.messages]
    
    def clear_memory(self):
        """Clear all messages"""
        self.messages = []
        self.save_memory()
