import os
import json
from typing import Optional

class LLMInterface:
    """
    Interface to LLM (Google Gemini) for natural language understanding.
    Helps parse user intent and extract entities from queries.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.use_llm = self.api_key is not None
        
        if self.use_llm:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                print("✅ LLM (Gemini) initialized successfully")
            except Exception as e:
                print(f"⚠️ Could not initialize LLM: {e}")
                self.use_llm = False
    
    def parse_intent(self, query, context=""):
        """
        Parse user query to understand intent and extract entities.
        
        Returns:
            dict with 'intent', 'entities', 'query_type'
        """
        if not self.use_llm:
            return self._fallback_parse(query)
        
        prompt = f"""You are a BI assistant. Analyze this user query and extract:
1. Intent (what they want to know)
2. Query type (roi, sales, correlation, contribution, brand, model, sql, visualization)
3. Entities (channels, metrics, time periods mentioned)

Context from previous conversation: {context}

User query: "{query}"

Respond in JSON format:
{{
    "intent": "brief description",
    "query_type": "one of: roi, sales, correlation, contribution, brand, model, sql, visualization, help",
    "entities": {{
        "channels": ["list of channels mentioned"],
        "metrics": ["list of metrics mentioned"],
        "time_period": "if mentioned"
    }},
    "needs_visualization": true/false
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
            return result
        except Exception as e:
            print(f"LLM parsing failed: {e}")
            return self._fallback_parse(query)
    
    def _fallback_parse(self, query):
        """Fallback parsing without LLM (keyword-based)."""
        query_lower = query.lower()
        
        # Determine query type
        if "roi" in query_lower:
            query_type = "roi"
        elif "sales" in query_lower or "revenue" in query_lower:
            query_type = "sales"
        elif "correlation" in query_lower:
            query_type = "correlation"
        elif "contribution" in query_lower or "impact" in query_lower:
            query_type = "contribution"
        elif "brand" in query_lower or "nps" in query_lower:
            query_type = "brand"
        elif "model" in query_lower or "accuracy" in query_lower:
            query_type = "model"
        elif any(kw in query_lower for kw in ['average', 'sum', 'count', 'max', 'min', 'top']):
            query_type = "sql"
        elif "show" in query_lower or "visualize" in query_lower or "chart" in query_lower:
            query_type = "visualization"
        else:
            query_type = "help"
        
        # Extract channels
        channels = []
        channel_keywords = ['tv', 'digital', 'radio', 'sem', 'sponsorship', 'affiliates']
        for ch in channel_keywords:
            if ch in query_lower:
                channels.append(ch.capitalize())
        
        return {
            "intent": query,
            "query_type": query_type,
            "entities": {
                "channels": channels,
                "metrics": [],
                "time_period": None
            },
            "needs_visualization": "show" in query_lower or "chart" in query_lower
        }
    
    def enhance_response(self, query, data_result, context=""):
        """
        Use LLM to generate a natural language response based on data.
        """
        if not self.use_llm:
            return None
        
        prompt = f"""You are a helpful BI assistant. The user asked: "{query}"

Context: {context}

Data result: {str(data_result)[:500]}

Generate a concise, insightful response (2-3 sentences) that:
1. Directly answers the question
2. Highlights key findings
3. Suggests next steps if relevant

Response:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return None
