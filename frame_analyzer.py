import os
import base64
import google.generativeai as genai

_model = None

def _get_model():
    global _model
    if _model is None:
        genai.configure(api_key=os.environ['GEMINI_API_KEY'])
        _model = genai.GenerativeModel('gemini-1.5-flash')
    return _model

def _image_part(path: str) -> dict:
    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode()
    return {'mime_type': 'image/jpeg', 'data': data}

def analyze_frames(frames: dict) -> dict:
    """
    frames: {timestamp_sec: image_path}
    반환: {
        'has_subtitle': 'O' | 'X',
        'has_3s_hook': 'O' | 'X',
        'product_timing': '5초' | '없음',
    }
    """
    model = _get_model()
    result = {'has_subtitle': 'X', 'has_3s_hook': 'X', 'product_timing': '없음'}

    if not frames:
        return result

    # 자막 유무: 여러 프레임 중 하나라도 자막 있으면 O
    all_parts = [_image_part(p) for p in frames.values()]
    subtitle_resp = model.generate_content([
        '이 영상 프레임들을 보세요. 화면에 자막이나 텍스트 오버레이가 있나요? '
        '한 프레임이라도 있으면 "O", 전혀 없으면 "X"만 답하세요.',
        *all_parts
    ])
    result['has_subtitle'] = 'O' if 'O' in subtitle_resp.text.strip() else 'X'

    # 3초 훅: 3초 프레임 분석 (없으면 가장 이른 프레임)
    frame_3s = frames.get(3) or frames.get(min(frames.keys()))
    hook_resp = model.generate_content([
        '이 프레임은 영상의 초반 3초입니다. 시청자의 시선을 즉시 끄는 강한 훅(질문, 충격적 장면, 강한 텍스트 등)이 있나요? '
        '"O" 또는 "X"만 답하세요.',
        _image_part(frame_3s)
    ])
    result['has_3s_hook'] = 'O' if 'O' in hook_resp.text.strip() else 'X'

    # 제품 등장 타이밍: 스킨케어 제품이 처음 등장하는 프레임 찾기
    sorted_ts = sorted(frames.keys())
    for ts in sorted_ts:
        prod_resp = model.generate_content([
            f'이 프레임({ts}초)에 스킨케어 제품(패드, 세럼, 아이패치 등 용기/패키지)이 보이나요? '
            '"예" 또는 "아니오"만 답하세요.',
            _image_part(frames[ts])
        ])
        if '예' in prod_resp.text or 'yes' in prod_resp.text.lower():
            result['product_timing'] = f'{ts}초'
            break

    return result

def extract_subtitle_text(frames: dict) -> str:
    """
    오디오 없는 영상에서 프레임의 자막 텍스트를 순서대로 추출.
    중복 제거하여 흐름 순서 유지.
    반환: 전체 텍스트 (빈 문자열 가능)
    """
    model = _get_model()
    if not frames:
        return ''

    texts = []
    prev_text = ''
    for ts in sorted(frames.keys()):
        resp = model.generate_content([
            '이 프레임에 보이는 자막이나 텍스트를 정확히 읽어서 그대로만 출력하세요. '
            '텍스트가 없으면 빈 문자열을 반환하세요.',
            _image_part(frames[ts])
        ])
        text = resp.text.strip()
        if text and text != prev_text:
            texts.append(text)
            prev_text = text

    return '\n'.join(texts)
