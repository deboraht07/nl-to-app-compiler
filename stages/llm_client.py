import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.1-8b-instant"  # smaller model, separate/higher daily quota, still strong at structured JSON


def call_llm_json(system_prompt: str, user_prompt: str) -> dict:
    """
    Calls the LLM and forces JSON output.
    Returns a Python dict parsed from the model's JSON response.
    Raises json.JSONDecodeError if the model returns invalid JSON
    (this is intentional — the validator/repair layer will catch it).
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,  # low temperature = more deterministic, as the task asks for
    )
    raw_text = response.choices[0].message.content
    return json.loads(raw_text)