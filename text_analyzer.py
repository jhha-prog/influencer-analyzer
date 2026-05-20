import os
import json
import re
from google import genai
from google.genai import types

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def analyze_text(transcript: str) -> dict:
    client = _get_client()
    prompt = f"""다음 인플루언서 영상 스크립트를 분석하세요.

스크립트:
{transcript}

JSON 형식으로만 답하세요:
{{
  "discount": "O(초반)|O(중반)|O(후반)|X",
  "problem": "O(초반)|O(중반)|X",
  "tone": "콘텐츠 톤 한국어 짧은 키워드"
}}

- discount: 할인/프로모션 소구 여부와 타이밍
- problem: 피부 고민/문제 제시 여부와 타이밍
- tone: 전체 콘텐츠 톤 (예: 뷰티 노하우, BnA 강조, ASMR형)"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    raw = re.sub(r"```json\n?|\n?```", "", response.text.strip()).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"discount": "X", "problem": "X", "tone": "분석 실패"}

    return {
        "discount_appeal": data.get("discount", "X"),
        "problem_timing": data.get("problem", "X"),
        "content_tone": data.get("tone", ""),
    }
