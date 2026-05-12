import os
import json
import re
import google.generativeai as genai

_model = None

def _get_model():
    global _model
    if _model is None:
        genai.configure(api_key=os.environ['GEMINI_API_KEY'])
        _model = genai.GenerativeModel('gemini-2.0-flash')
    return _model

def analyze_text(transcript: str) -> dict:
    """
    반환: {
        'discount_appeal': 'O(초반)' | 'O(중반)' | 'O(후반)' | 'X',
        'problem_timing': 'O(초반)' | 'O(중반)' | 'X',
        'content_tone': str,
    }
    """
    model = _get_model()
    prompt = f"""다음 인플루언서 영상 스크립트를 분석하세요.

스크립트:
{transcript}

JSON 형식으로만 답하세요 (다른 텍스트 없이):
{{
  "discount": "O(초반)|O(중반)|O(후반)|X",
  "problem": "O(초반)|O(중반)|X",
  "tone": "콘텐츠 톤을 한국어 짧은 키워드로"
}}

- discount: 할인/프로모션/특가 소구 여부 및 등장 타이밍 (초반=앞 1/3, 중반=가운데, 후반=뒤 1/3)
- problem: 시청자 피부 고민/문제 제시 여부 및 타이밍
- tone: 콘텐츠 전체 톤 (예: 뷰티 노하우, BnA 강조, ASMR형, 대세감 강조, 2-in-1 제품설명)"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # JSON 파싱 (마크다운 코드블록 제거)
    raw = re.sub(r'```json\n?|\n?```', '', raw).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {'discount': 'X', 'problem': 'X', 'tone': '분석 실패'}

    return {
        'discount_appeal': data.get('discount', 'X'),
        'problem_timing': data.get('problem', 'X'),
        'content_tone': data.get('tone', ''),
    }
