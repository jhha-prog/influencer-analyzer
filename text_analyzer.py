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
    ë°˜í™˜: {
        'discount_appeal': 'O(ì´ˆë°˜)' | 'O(ì¤‘ë°˜)' | 'O(?„ë°˜)' | 'X',
        'problem_timing': 'O(ì´ˆë°˜)' | 'O(ì¤‘ë°˜)' | 'X',
        'content_tone': str,
    }
    """
    model = _get_model()
    prompt = f"""?¤ìŒ ?¸í”Œë£¨ì–¸???ìƒ ?¤í¬ë¦½íŠ¸ë¥?ë¶„ì„?˜ì„¸??

?¤í¬ë¦½íŠ¸:
{transcript}

JSON ?•ì‹?¼ë¡œë§??µí•˜?¸ìš” (?¤ë¥¸ ?ìŠ¤???†ì´):
{{
  "discount": "O(ì´ˆë°˜)|O(ì¤‘ë°˜)|O(?„ë°˜)|X",
  "problem": "O(ì´ˆë°˜)|O(ì¤‘ë°˜)|X",
  "tone": "ì½˜í…ì¸??¤ì„ ?œêµ­??ì§§ì? ?¤ì›Œ?œë¡œ"
}}

- discount: ? ì¸/?„ë¡œëª¨ì…˜/?¹ê? ?Œêµ¬ ?¬ë? ë°??±ì¥ ?€?´ë° (ì´ˆë°˜=??1/3, ì¤‘ë°˜=ê°€?´ë°, ?„ë°˜=??1/3)
- problem: ?œì²­???¼ë? ê³ ë?/ë¬¸ì œ ?œì‹œ ?¬ë? ë°??€?´ë°
- tone: ì½˜í…ì¸??„ì²´ ??(?? ë·°í‹° ?¸í•˜?? BnA ê°•ì¡°, ASMR?? ?€?¸ê° ê°•ì¡°, 2-in-1 ?œí’ˆ?¤ëª…)"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # JSON ?Œì‹± (ë§ˆí¬?¤ìš´ ì½”ë“œë¸”ë¡ ?œê±°)
    raw = re.sub(r'```json\n?|\n?```', '', raw).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {'discount': 'X', 'problem': 'X', 'tone': 'ë¶„ì„ ?¤íŒ¨'}

    return {
        'discount_appeal': data.get('discount', 'X'),
        'problem_timing': data.get('problem', 'X'),
        'content_tone': data.get('tone', ''),
    }
