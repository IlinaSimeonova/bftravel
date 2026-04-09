import logging

import anthropic
from decouple import config

logger = logging.getLogger(__name__)


def get_destination_info(destination: str) -> dict:
    """
    Generate travel info for a destination using Claude AI.
    Returns tips, visa requirements (Austrian + Bulgarian), and health info.
    """
    api_key = config('ANTHROPIC_API_KEY')
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are a travel expert. Provide practical travel information for {destination}.

Return the information as a JSON object with these exact keys. Keep each section concise.

{{
  "best_time": {{
    "summary": "[One line, e.g. 'March to May (Spring)']",
    "details": "[2-3 sentences about why this is the best time]"
  }},
  "travel_tips": {{
    "summary": "[One line, e.g. '5 essential tips']",
    "details": "[4-5 bullet points as a string with line breaks]"
  }},
  "visa": {{
    "summary": "[One line, e.g. 'Visa-free for both']",
    "austrian": "[Requirements for Austrian citizens]",
    "bulgarian": "[Requirements for Bulgarian citizens]"
  }},
  "health": {{
    "summary": "[One line, e.g. 'No special vaccines required']",
    "details": "[Vaccinations and health precautions]"
  }},
  "must_sees": {{
    "summary": "[One line, e.g. 'Top 5 unmissable spots']",
    "details": "[5 must-see places/experiences with brief descriptions]"
  }},
  "food": {{
    "summary": "[One line, e.g. 'Street food paradise']",
    "details": "[5 dishes/foods to try with descriptions]"
  }},
  "budget": {{
    "summary": "[One line, e.g. '€50-80 per day']",
    "details": "[Breakdown: accommodation range, food costs, transport, activities]"
  }}
}}

Return ONLY the JSON, no other text."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return {
            "success": True,
            "content": message.content[0].text,
            "destination": destination
        }
    except Exception as e:
        logger.error(f"Error getting destination info: {e}")
        return {
            "success": False,
            "error": str(e),
            "destination": destination
        }
