"""
LLM Council Agent - Implements Karpathy's LLM Council pattern.
Now with OpenRouter support for diverse models (GPT, Claude, Gemini, etc.)

The council works in 3 stages:
1. First Opinions: Multiple LLMs respond independently
2. Peer Review: Each LLM reviews and ranks others' responses
3. Chairman Synthesizes: A Chairman LLM produces the final answer
"""

import os
import json
import httpx
from typing import List, Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class CouncilAgent:
    """
    LLM Council that queries multiple models via OpenRouter and synthesizes their responses.
    Falls back to Gemini-only if OpenRouter is not available.
    """

    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, council_models: List[str] = None, chairman_model: str = None):
        """
        Initialize the council with OpenRouter or Gemini fallback.
        """
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        
        self.use_openrouter = bool(self.openrouter_key)
        
        if self.use_openrouter:
            # Default council: Diverse models via OpenRouter
            self.council_models = council_models or [
                "openai/gpt-4o-mini",
                "anthropic/claude-3-haiku",
                "google/gemini-flash-1.5",
            ]
            self.chairman_model = chairman_model or "openai/gpt-4o"
            print(f"✅ Council initialized with OpenRouter ({len(self.council_models)} diverse models)")
        elif self.gemini_key:
            # Fallback to Gemini-only
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_key)
            self.council_models = council_models or [
                "gemini-flash-latest",
                "gemini-pro-latest",
            ]
            self.chairman_model = chairman_model or "gemini-flash-latest"
            self.genai = genai
            print(f"✅ Council initialized with Gemini ({len(self.council_models)} models)")
        else:
            raise ValueError("Either OPENROUTER_API_KEY or GEMINI_API_KEY required")
        
        # Conversation memory
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 10  # Keep last 10 exchanges

    def _call_openrouter(self, model: str, prompt: str) -> str:
        """Call OpenRouter API."""
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/AvirupRoy2195/MMX_Agent",
            "X-Title": "MMX Agent Council"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
        
        with httpx.Client(timeout=60.0) as client:
            response = client.post(self.OPENROUTER_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    def _get_opinion(self, model_name: str, query: str, context: str = "") -> Dict[str, Any]:
        """Get a single model's opinion with marketing context."""
        prompt = f"""You are an expert Marketing Mix Modeling (MMM) analyst specializing in:
- ROI analysis and budget optimization
- Media channel attribution (TV, Digital, Print)
- Brand health metrics (NPS) and their impact on sales
- Adstock effects and marketing carryover

You have access to data from DT Mart, a retail company. The data includes:
- Monthly sales figures
- Media spend across channels (TV, Digital, Print)
- Net Promoter Score (NPS) for brand health
- 12 months of historical data

{f"Additional Context: {context}" if context else ""}

User Question: {query}

Provide a clear, data-driven, actionable response. Reference specific metrics where relevant."""
        
        try:
            if self.use_openrouter:
                response_text = self._call_openrouter(model_name, prompt)
            else:
                model = self.genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                response_text = response.text
            
            return {
                "model": model_name,
                "response": response_text,
                "error": None
            }
        except Exception as e:
            return {
                "model": model_name,
                "response": None,
                "error": str(e)
            }

    def get_first_opinions(self, query: str, context: str = "") -> List[Dict[str, Any]]:
        """Stage 1: Get independent opinions from all council members."""
        print("🏛️ Stage 1: Gathering first opinions...")
        opinions = []
        
        for model_name in self.council_models:
            opinion = self._get_opinion(model_name, query, context)
            opinions.append(opinion)
            status = "✓" if opinion["response"] else "✗"
            print(f"  {status} {model_name}")
        
        return opinions

    def get_peer_reviews(self, query: str, opinions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Stage 2: Each model reviews and ranks the other models' responses."""
        print("🔍 Stage 2: Peer review...")
        reviews = []
        
        valid_opinions = [o for o in opinions if o["response"]]
        if len(valid_opinions) < 2:
            print("  ⚠️ Not enough valid opinions for peer review")
            return []
        
        anonymized = "\n\n".join([
            f"=== Response {chr(65+i)} ===\n{o['response']}"
            for i, o in enumerate(valid_opinions)
        ])
        
        review_prompt = f"""You are evaluating multiple AI responses to a user question.

User Question: {query}

Here are the anonymized responses:

{anonymized}

Rank these responses from best to worst based on accuracy, clarity, and insights.
Respond in JSON format:
{{"ranking": ["A", "B", "C"], "reasoning": "Brief explanation"}}
"""
        
        # Use first 2 council members as reviewers
        for model_name in self.council_models[:2]:
            try:
                if self.use_openrouter:
                    text = self._call_openrouter(model_name, review_prompt)
                else:
                    model = self.genai.GenerativeModel(model_name)
                    text = model.generate_content(review_prompt).text
                
                text = text.strip().replace('```json', '').replace('```', '')
                try:
                    review_data = json.loads(text)
                except:
                    review_data = {"raw": text}
                
                reviews.append({"reviewer": model_name, "review": review_data, "error": None})
                print(f"  ✓ {model_name} reviewed")
            except Exception as e:
                reviews.append({"reviewer": model_name, "review": None, "error": str(e)})
                print(f"  ✗ {model_name}: {e}")
        
        return reviews

    def synthesize_final(self, query: str, opinions: List[Dict[str, Any]], 
                         reviews: List[Dict[str, Any]], context: str = "") -> str:
        """Stage 3: Chairman synthesizes the final response."""
        print("👑 Stage 3: Chairman synthesizing...")
        
        opinions_text = "\n\n".join([
            f"=== {o['model']} ===\n{o['response']}"
            for o in opinions if o["response"]
        ])
        
        reviews_text = "\n\n".join([
            f"=== {r['reviewer']} ===\n{json.dumps(r['review'], indent=2)}"
            for r in reviews if r["review"]
        ]) if reviews else "No peer reviews."
        
        chairman_prompt = f"""You are the Chairman of an LLM Council. Synthesize the best answer from these responses.

User Question: {query}

Council Responses:
{opinions_text}

Peer Reviews:
{reviews_text}

Provide a definitive, synthesized answer taking the best insights and correcting any errors."""
        
        try:
            if self.use_openrouter:
                result = self._call_openrouter(self.chairman_model, chairman_prompt)
            else:
                model = self.genai.GenerativeModel(self.chairman_model)
                result = model.generate_content(chairman_prompt).text
            
            print("  ✓ Chairman synthesized")
            return result
        except Exception as e:
            print(f"  ✗ Chairman failed: {e}")
            for o in opinions:
                if o["response"]:
                    return f"[Fallback] {o['response']}"
            return "Council unable to respond."

    def ask(self, query: str, context: str = "") -> Dict[str, Any]:
        """Full council pipeline with conversation memory."""
        print(f"\n🏛️ LLM COUNCIL CONVENED 🏛️")
        print(f"Mode: {'OpenRouter (diverse)' if self.use_openrouter else 'Gemini'}")
        
        # Build context with conversation history
        history_context = ""
        if self.conversation_history:
            history_context = "\n\nPrevious conversation:\n"
            for exchange in self.conversation_history[-5:]:  # Last 5 exchanges
                history_context += f"User: {exchange['user']}\n"
                history_context += f"Council: {exchange['response'][:200]}...\n\n"
        
        full_context = f"{context}\n{history_context}" if history_context else context
        
        opinions = self.get_first_opinions(query, full_context)
        reviews = self.get_peer_reviews(query, opinions)
        final = self.synthesize_final(query, opinions, reviews, full_context)
        
        # Store in memory
        self.conversation_history.append({
            "user": query,
            "response": final
        })
        
        # Trim history if needed
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        print(f"✅ Council complete (Memory: {len(self.conversation_history)} exchanges)\n")
        return {"opinions": opinions, "reviews": reviews, "final_response": final}
    
    def clear_memory(self):
        """Clear conversation history."""
        self.conversation_history = []
        print("🧹 Council memory cleared")
    
    def get_memory_summary(self) -> str:
        """Get a summary of conversation history."""
        if not self.conversation_history:
            return "No conversation history."
        return f"{len(self.conversation_history)} exchanges in memory."
