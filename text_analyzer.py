import os
import json
import re
import time
from google import genai
from google.genai import types

_client = None

MODELS = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest"]


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def _generate(contents, retries=3):
    client = _get_client()
    for model in MODELS:
        for attempt in range(retries):
            try:
                return client.models.generate_content(model=model, contents=contents)
            except Exception as e:
                msg = str(e)
                if any(x in msg for x in ("503", "500", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "INTERNAL")):
                    if attempt < retries - 1:
                        time.sleep(3)
                        continue
                    break
                raise
    raise RuntimeError("모든 모델 응답 실패")


def analyze_text(transcript: str) -> dict:
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

    response = _generate(prompt)
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
