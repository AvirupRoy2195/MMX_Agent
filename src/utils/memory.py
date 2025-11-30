import os
from typing import List, Dict

class ConversationMemory:
    """
    Manages conversation history and context for the agent.
    Tracks previous queries, responses, and extracted entities.
    """
    
    def __init__(self, max_history=10):
        self.max_history = max_history
        self.conversation_history = []
        self.context = {
            'last_query_type': None,
            'last_mentioned_channels': [],
            'last_mentioned_metrics': [],
            'user_preferences': {}
        }
    
    def add_message(self, role, content, metadata=None):
        """Add a message to conversation history."""
        message = {
            'role': role,
            'content': content,
            'metadata': metadata or {}
        }
        self.conversation_history.append(message)
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_history * 2:  # *2 for user+assistant pairs
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
    
    def get_recent_context(self, n=3):
        """Get recent conversation for context."""
        return self.conversation_history[-n*2:] if len(self.conversation_history) >= n*2 else self.conversation_history
    
    def update_context(self, query_type=None, channels=None, metrics=None):
        """Update conversation context."""
        if query_type:
            self.context['last_query_type'] = query_type
        if channels:
            self.context['last_mentioned_channels'] = channels
        if metrics:
            self.context['last_mentioned_metrics'] = metrics
    
    def get_context_summary(self):
        """Get a summary of current context."""
        summary = []
        if self.context['last_query_type']:
            summary.append(f"Last query type: {self.context['last_query_type']}")
        if self.context['last_mentioned_channels']:
            summary.append(f"Channels discussed: {', '.join(self.context['last_mentioned_channels'])}")
        return " | ".join(summary) if summary else "No prior context"
    
    def resolve_reference(self, query):
        """
        Resolve pronouns and references using context.
        E.g., "What about Digital?" after asking about TV
        """
        query_lower = query.lower()
        
        # Handle "it", "that", "this"
        if any(word in query_lower for word in ['it', 'that', 'this', 'same']):
            if self.context['last_mentioned_channels']:
                # Replace reference with actual channel
                for channel in self.context['last_mentioned_channels']:
                    if channel.lower() not in query_lower:
                        query = query + f" for {channel}"
        
        # Handle "also", "too"
        if any(word in query_lower for word in ['also', 'too', 'as well']):
            if self.context['last_query_type']:
                # Infer they want the same type of analysis
                query = f"{self.context['last_query_type']} {query}"
        
        return query
