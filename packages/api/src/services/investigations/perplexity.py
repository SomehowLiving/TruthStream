import httpx
from typing import List, Dict
from src.core.config import get_settings

class PerplexityClient:
    def __init__(self):
        self.api_key = get_settings().PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai"
        
    async def search(self, query: str) -> Dict:
        """
        Search for real-time information
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": "llama-3.1-sonar-small-128k-online",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a fact-checking assistant. Search the web and provide concise, sourced information."
                            },
                            {
                                "role": "user",
                                "content": query
                            }
                        ]
                    },
                    timeout=10.0
                )
                
                data = response.json()
                return {
                    "answer": data["choices"][0]["message"]["content"],
                    "sources": [citation for citation in data.get("citations", [])],
                    "success": True
                }
        except Exception as e:
            return {"answer": "", "sources": [], "success": False, "error": str(e)}
    
    async def fact_check_claims(self, claims: List[str]) -> List[Dict]:
        """Batch fact check multiple claims"""
        results = []
        for claim in claims:
            result = await self.search(f"Fact check: {claim}")
            results.append({
                "claim": claim,
                "verification": result
            })
        return results