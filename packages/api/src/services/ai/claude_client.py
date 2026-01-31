import anthropic
from typing import Dict, List
from src.core.config import get_settings

class ClaudeClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=get_settings().ANTHROPIC_API_KEY)
        
    async def analyze_content(self, text_content: str, has_visual: bool = False) -> Dict:
        """
        Analyze text for claims, bias, and manipulation
        """
        try:
            prompt = f"""
            Analyze the following content for a fact-checking system.
            
            Content: {text_content[:4000]}  # Truncate if too long
            
            Provide a JSON response with:
            1. "claims": List of factual claims made (bullet points)
            2. "sentiment": Overall tone (negative/neutral/positive)
            3. "bias_indicators": List of political/emotional bias signals
            4. "manipulation_techniques": List of persuasion tactics used (fear, urgency, etc.)
            5. "confidence_score": 0-1 score of how factual it appears
            6. "summary": 2-sentence analysis
            
            Format as valid JSON only.
            """
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the JSON response (Claude should return valid JSON)
            import json
            content = message.content[0].text
            # Extract JSON if wrapped in markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            return json.loads(content)
            
        except Exception as e:
            print(f"Claude error: {e}")
            # Return fallback
            return {
                "claims": ["Unable to extract claims"],
                "sentiment": "unknown",
                "bias_indicators": [],
                "manipulation_techniques": [],
                "confidence_score": 0.5,
                "summary": "Analysis failed"
            }
    
    def synthesize_investigation(self, 
                                ai_analysis: Dict, 
                                web_results: List[Dict],
                                metadata: Dict) -> Dict:
        """
        Synthesize all evidence into a verdict
        """
        prompt = f"""
        Synthesize fact-check:
        
        AI Analysis: {ai_analysis}
        Web Verification: {web_results}
        File Metadata: {metadata}
        
        Determine:
        1. "verdict": One of [verified, partially_false, out_of_context, manipulated, unverified]
        2. "confidence": 0.0 to 1.0
        3. "explanation": Why this verdict
        4. "toma_transparency": Score 0-100 (how clear are the sources?)
        5. "toma_alignment": Score 0-100 (how neutral/biased?)
        
        Return as JSON.
        """
        
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            content = message.content[0].text
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            return json.loads(content)
        except:
            return {
                "verdict": "unverified",
                "confidence": 0.0,
                "explanation": "Synthesis failed",
                "toma_transparency": 50,
                "toma_alignment": 50
            }