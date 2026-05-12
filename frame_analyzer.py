import os
import base64
import google.generativeai as genai

_model = None

def _get_model():
    global _model
    if _model is None:
        genai.configure(api_key=os.environ['GEMINI_API_KEY'])
        _model = genai.GenerativeModel('gemini-2.0-flash')
    return _model

def _image_part(path: str) -> dict:
    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode()
    return {'mime_type': 'image/jpeg', 'data': data}

def analyze_frames(frames: dict) -> dict:
    """
    frames: {timestamp_sec: image_path}
    ë°˜í™˜: {
        'has_subtitle': 'O' | 'X',
        'has_3s_hook': 'O' | 'X',
        'product_timing': '5ì´? | '?†ìŒ',
    }
    """
    model = _get_model()
    result = {'has_subtitle': 'X', 'has_3s_hook': 'X', 'product_timing': '?†ìŒ'}

    if not frames:
        return result

    # ?ë§‰ ? ë¬´: ?¬ëŸ¬ ?„ë ˆ??ì¤??˜ë‚˜?¼ë„ ?ë§‰ ?ˆìœ¼ë©?O
    all_parts = [_image_part(p) for p in frames.values()]
    subtitle_resp = model.generate_content([
        '???ìƒ ?„ë ˆ?„ë“¤??ë³´ì„¸?? ?”ë©´???ë§‰?´ë‚˜ ?ìŠ¤???¤ë²„?ˆì´ê°€ ?ˆë‚˜?? '
        '???„ë ˆ?„ì´?¼ë„ ?ˆìœ¼ë©?"O", ?„í? ?†ìœ¼ë©?"X"ë§??µí•˜?¸ìš”.',
        *all_parts
    ])
    result['has_subtitle'] = 'O' if 'O' in subtitle_resp.text.strip() else 'X'

    # 3ì´??? 3ì´??„ë ˆ??ë¶„ì„ (?†ìœ¼ë©?ê°€???´ë¥¸ ?„ë ˆ??
    frame_3s = frames.get(3) or frames.get(min(frames.keys()))
    hook_resp = model.generate_content([
        '???„ë ˆ?„ì? ?ìƒ??ì´ˆë°˜ 3ì´ˆì…?ˆë‹¤. ?œì²­?ì˜ ?œì„ ??ì¦‰ì‹œ ?„ëŠ” ê°•í•œ ??ì§ˆë¬¸, ì¶©ê²©???¥ë©´, ê°•í•œ ?ìŠ¤???????ˆë‚˜?? '
        '"O" ?ëŠ” "X"ë§??µí•˜?¸ìš”.',
        _image_part(frame_3s)
    ])
    result['has_3s_hook'] = 'O' if 'O' in hook_resp.text.strip() else 'X'

    # ?œí’ˆ ?±ì¥ ?€?´ë°: ?¤í‚¨ì¼€???œí’ˆ??ì²˜ìŒ ?±ì¥?˜ëŠ” ?„ë ˆ??ì°¾ê¸°
    sorted_ts = sorted(frames.keys())
    for ts in sorted_ts:
        prod_resp = model.generate_content([
            f'???„ë ˆ??{ts}ì´????¤í‚¨ì¼€???œí’ˆ(?¨ë“œ, ?¸ëŸ¼, ?„ì´?¨ì¹˜ ???©ê¸°/?¨í‚¤ì§€)??ë³´ì´?˜ìš”? '
            '"?? ?ëŠ” "?„ë‹ˆ??ë§??µí•˜?¸ìš”.',
            _image_part(frames[ts])
        ])
        if '?? in prod_resp.text or 'yes' in prod_resp.text.lower():
            result['product_timing'] = f'{ts}ì´?
            break

    return result

def extract_subtitle_text(frames: dict) -> str:
    """
    ?¤ë””???†ëŠ” ?ìƒ?ì„œ ?„ë ˆ?„ì˜ ?ë§‰ ?ìŠ¤?¸ë? ?œì„œ?€ë¡?ì¶”ì¶œ.
    ì¤‘ë³µ ?œê±°?˜ì—¬ ?ë¦„ ?œì„œ ? ì?.
    ë°˜í™˜: ?„ì²´ ?ìŠ¤??(ë¹?ë¬¸ì??ê°€??
    """
    model = _get_model()
    if not frames:
        return ''

    texts = []
    prev_text = ''
    for ts in sorted(frames.keys()):
        resp = model.generate_content([
            '???„ë ˆ?„ì— ë³´ì´???ë§‰?´ë‚˜ ?ìŠ¤?¸ë? ?•í™•???½ì–´??ê·¸ë?ë¡œë§Œ ì¶œë ¥?˜ì„¸?? '
            '?ìŠ¤?¸ê? ?†ìœ¼ë©?ë¹?ë¬¸ì?´ì„ ë°˜í™˜?˜ì„¸??',
            _image_part(frames[ts])
        ])
        text = resp.text.strip()
        if text and text != prev_text:
            texts.append(text)
            prev_text = text

    return '\n'.join(texts)
