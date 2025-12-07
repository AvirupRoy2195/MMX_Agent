"""
LLM Council Agent - Enhanced with Premium Models & Reasoning
Implements Karpathy's LLM Council pattern with:
- Premium models: Claude Opus 4.5, GPT-5, Grok 4.1
- Reasoning stage before opinions
- Planning/Strategy integration
- Robust error handling with retries

The council works in 4 stages:
1. Reasoning: Analyze the query and determine approach
2. First Opinions: Multiple premium LLMs respond independently
3. Peer Review: Each LLM reviews and ranks others' responses
4. Chairman Synthesizes: Best model produces the final answer
"""

import os
import json
import time
import httpx
from typing import List, Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class CouncilAgent:
    """
    Premium LLM Council with reasoning, planning, and robust error handling.
    Uses OpenRouter for access to GPT-5, Claude Opus, Grok, and more.
    """

    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds

    def __init__(self, council_models: List[str] = None, chairman_model: str = None):
        """Initialize the premium council."""
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        
        self.use_openrouter = bool(self.openrouter_key)
        
        if self.use_openrouter:
            # Premium council: Exact models specified
            self.council_models = council_models or [
                "anthropic/claude-opus-4.5",   # Claude Opus 4.5
                "openai/gpt-5",                 # GPT-5
                "x-ai/grok-4.1-fast",           # Grok 4.1 Fast
            ]
            self.chairman_model = chairman_model or "anthropic/claude-opus-4.5"
            self.reasoning_model = "openai/gpt-5"  # Use GPT-5 for reasoning
            print(f"✅ Premium Council: {len(self.council_models)} top-tier models")
            print(f"   Models: {', '.join(self.council_models)}")
        elif self.gemini_key:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_key)
            self.council_models = ["gemini-flash-latest", "gemini-pro-latest"]
            self.chairman_model = "gemini-flash-latest"
            self.reasoning_model = "gemini-flash-latest"
            self.genai = genai
            print(f"✅ Council (Gemini fallback): {len(self.council_models)} models")
        else:
            raise ValueError("Either OPENROUTER_API_KEY or GEMINI_API_KEY required")
        
        # Conversation memory
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 10
        
        # Reasoning cache
        self.last_reasoning: Optional[str] = None

    def _call_openrouter(self, model: str, prompt: str, system_prompt: str = None) -> str:
        """Call OpenRouter API with retries."""
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/AvirupRoy2195/MMX_Agent",
            "X-Title": "MMX Agent Premium Council"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        for attempt in range(self.MAX_RETRIES):
            try:
                with httpx.Client(timeout=90.0) as client:
                    response = client.post(self.OPENROUTER_URL, headers=headers, json=payload)
                    response.raise_for_status()
                    return response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                if attempt < self.MAX_RETRIES - 1:
                    print(f"  ⚠️ Retry {attempt + 1}/{self.MAX_RETRIES} for {model}: {e}")
                    time.sleep(self.RETRY_DELAY)
                else:
                    raise

    def analyze_query(self, query: str, context: str = "") -> Dict[str, Any]:
        """Stage 0: Reasoning - Analyze the query to determine best approach."""
        print("🧠 Stage 0: Reasoning & Analysis...")
        
        reasoning_prompt = f"""You are an expert query analyzer for a Marketing Mix Modeling system.

Analyze this query and determine:
1. Query Type: (data_query, analysis, comparison, recommendation, complex_multi_step)
2. Required Data: What data points are needed?
3. Approach: How should this be answered?
4. Complexity: (simple, moderate, complex)

Query: "{query}"
Context: {context if context else "No additional context"}

Respond in JSON format:
{{
    "query_type": "...",
    "requires_data": ["list", "of", "data"],
    "approach": "brief description of approach",
    "complexity": "...",
    "key_focus": "main thing to focus on"
}}"""

        try:
            if self.use_openrouter:
                response = self._call_openrouter(self.reasoning_model, reasoning_prompt)
            else:
                model = self.genai.GenerativeModel(self.reasoning_model)
                response = model.generate_content(reasoning_prompt).text
            
            # Parse JSON
            clean = response.strip().replace('```json', '').replace('```', '')
            reasoning = json.loads(clean)
            self.last_reasoning = reasoning
            print(f"  ✓ Query type: {reasoning.get('query_type', 'unknown')}")
            print(f"  ✓ Complexity: {reasoning.get('complexity', 'unknown')}")
            return reasoning
        except Exception as e:
            print(f"  ⚠️ Reasoning failed: {e}")
            return {"query_type": "general", "complexity": "moderate", "approach": "standard"}

    def get_first_opinions(self, query: str, context: str = "", reasoning: Dict = None) -> List[Dict[str, Any]]:
        """Stage 1: Get independent opinions from all premium council members."""
        print("🏛️ Stage 1: Gathering expert opinions...")
        
        system_prompt = """You are an expert Marketing Mix Modeling (MMM) analyst with deep expertise in:
- ROI analysis and budget optimization
- Media channel attribution (TV, Digital, Print, Social)
- Brand health metrics (NPS) and their impact on sales
- Adstock effects and marketing carryover
- Statistical modeling and data interpretation

Provide clear, data-driven, actionable insights. Be specific with numbers and recommendations."""

        approach_context = ""
        if reasoning:
            approach_context = f"\n\nAnalysis Approach: {reasoning.get('approach', '')}\nFocus on: {reasoning.get('key_focus', '')}"
        
        prompt = f"""Context: DT Mart retail data with monthly sales, media spend (TV, Digital, Print), and NPS.
{context}
{approach_context}

Question: {query}

Provide a comprehensive, expert analysis."""

        opinions = []
        for model_name in self.council_models:
            try:
                if self.use_openrouter:
                    response_text = self._call_openrouter(model_name, prompt, system_prompt)
                else:
                    model = self.genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    response_text = response.text
                
                opinions.append({
                    "model": model_name,
                    "response": response_text,
                    "error": None
                })
                print(f"  ✓ {model_name.split('/')[-1]}")
            except Exception as e:
                opinions.append({
                    "model": model_name,
                    "response": None,
                    "error": str(e)
                })
                print(f"  ✗ {model_name.split('/')[-1]}: {e}")
        
        return opinions

    def get_peer_reviews(self, query: str, opinions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Stage 2: Rigorous peer review with ranking and critique."""
        print("🔍 Stage 2: Peer review & ranking...")
        
        valid_opinions = [o for o in opinions if o["response"]]
        if len(valid_opinions) < 2:
            print("  ⚠️ Not enough opinions for review")
            return []
        
        anonymized = "\n\n".join([
            f"=== Response {chr(65+i)} ===\n{o['response']}"
            for i, o in enumerate(valid_opinions)
        ])
        
        review_prompt = f"""You are a senior marketing analytics reviewer. Evaluate these responses:

Question: {query}

Responses:
{anonymized}

Rank from best to worst based on:
1. Accuracy & correctness
2. Actionable insights
3. Data-driven reasoning
4. Clarity & completeness

Respond in JSON:
{{
    "ranking": ["A", "B", "C"],
    "best_response": "letter",
    "reasoning": "why this ranking",
    "key_insights_to_keep": ["list", "of", "insights"],
    "issues_found": ["any", "problems", "spotted"]
}}"""

        reviews = []
        for model_name in self.council_models[:2]:
            try:
                if self.use_openrouter:
                    text = self._call_openrouter(model_name, review_prompt)
                else:
                    model = self.genai.GenerativeModel(model_name)
                    text = model.generate_content(review_prompt).text
                
                clean = text.strip().replace('```json', '').replace('```', '')
                try:
                    review_data = json.loads(clean)
                except:
                    review_data = {"raw": clean}
                
                reviews.append({"reviewer": model_name, "review": review_data, "error": None})
                print(f"  ✓ {model_name.split('/')[-1]} reviewed")
            except Exception as e:
                reviews.append({"reviewer": model_name, "review": None, "error": str(e)})
                print(f"  ✗ {model_name.split('/')[-1]}: {e}")
        
        return reviews

    def synthesize_final(self, query: str, opinions: List[Dict], reviews: List[Dict], 
                         context: str = "", reasoning: Dict = None) -> str:
        """Stage 3: Chairman synthesizes the definitive response."""
        print("👑 Stage 3: Chairman synthesizing final answer...")
        
        opinions_text = "\n\n".join([
            f"=== {o['model'].split('/')[-1]} ===\n{o['response']}"
            for o in opinions if o["response"]
        ])
        
        reviews_summary = ""
        for r in reviews:
            if r["review"]:
                review = r["review"]
                if isinstance(review, dict):
                    reviews_summary += f"\nReviewer notes: {review.get('reasoning', '')}\n"
                    reviews_summary += f"Key insights: {review.get('key_insights_to_keep', [])}\n"
        
        chairman_prompt = f"""You are the Chairman of a premium LLM Council. Your task is to synthesize the BEST possible answer.

Original Question: {query}

{f"Analysis Approach: {reasoning.get('approach', '')}" if reasoning else ""}

Council Expert Responses:
{opinions_text}

Peer Review Summary:
{reviews_summary if reviews_summary else "No reviews available"}

SYNTHESIZE a definitive, comprehensive answer that:
1. Takes the BEST insights from each response
2. Corrects any errors identified in reviews
3. Provides clear, actionable recommendations
4. Uses specific data points where available
5. Is well-structured with headers and bullet points

Your synthesized answer:"""

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
            # Fallback to best individual response
            for o in opinions:
                if o["response"]:
                    return f"[Best Individual Response]\n\n{o['response']}"
            return "Council was unable to generate a response."

    def ask(self, query: str, context: str = "") -> Dict[str, Any]:
        """Full council pipeline with reasoning, opinions, review, and synthesis."""
        print(f"\n{'='*50}")
        print(f"🏛️ PREMIUM LLM COUNCIL CONVENED")
        print(f"{'='*50}")
        print(f"Query: {query[:80]}...")
        
        # Build context with conversation history
        history_context = ""
        if self.conversation_history:
            history_context = "\n\nPrevious conversation:\n"
            for exchange in self.conversation_history[-3:]:
                history_context += f"Q: {exchange['user'][:100]}...\n"
                history_context += f"A: {exchange['response'][:150]}...\n\n"
        
        full_context = f"{context}\n{history_context}" if history_context else context
        
        # Stage 0: Reasoning
        reasoning = self.analyze_query(query, full_context)
        
        # Stage 1: First Opinions
        opinions = self.get_first_opinions(query, full_context, reasoning)
        
        # Stage 2: Peer Review
        reviews = self.get_peer_reviews(query, opinions)
        
        # Stage 3: Synthesis
        final = self.synthesize_final(query, opinions, reviews, full_context, reasoning)
        
        # Store in memory
        self.conversation_history.append({"user": query, "response": final})
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        print(f"{'='*50}")
        print(f"✅ Council complete (Memory: {len(self.conversation_history)} exchanges)")
        print(f"{'='*50}\n")
        
        return {
            "reasoning": reasoning,
            "opinions": opinions,
            "reviews": reviews,
            "final_response": final
        }
    
    def clear_memory(self):
        """Clear conversation history."""
        self.conversation_history = []
        self.last_reasoning = None
        print("🧹 Council memory cleared")
    
    def get_status(self) -> Dict[str, Any]:
        """Get council status and configuration."""
        return {
            "mode": "OpenRouter (Premium)" if self.use_openrouter else "Gemini",
            "models": self.council_models,
            "chairman": self.chairman_model,
            "memory_size": len(self.conversation_history),
            "last_reasoning": self.last_reasoning
        }
