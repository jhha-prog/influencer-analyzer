import os
from google import genai
from google.genai import types

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(
            api_key=os.environ["GEMINI_API_KEY"],
            http_options={"api_version": "v1"},
        )
    return _client


def _image_part(path: str):
    with open(path, "rb") as f:
        return types.Part.from_bytes(data=f.read(), mime_type="image/jpeg")


def analyze_frames(frames: dict) -> dict:
    client = _get_client()
    result = {"has_subtitle": "X", "has_3s_hook": "X", "product_timing": ""}

    if not frames:
        return result

    all_parts = [_image_part(p) for p in frames.values()]
    subtitle_resp = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=all_parts + ["이 영상 프레임들 중 자막이나 텍스트 오버레이가 있으면 O, 없으면 X만 답하세요."]
    )
    result["has_subtitle"] = "O" if "O" in subtitle_resp.text.strip() else "X"

    frame_3s_path = frames.get(3) or frames.get(min(frames.keys()))
    hook_resp = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[
            _image_part(frame_3s_path),
            "이 프레임은 영상 초반 3초입니다. 강한 훅(질문, 충격, 강한 텍스트)이 있으면 O, 없으면 X만 답하세요."
        ]
    )
    result["has_3s_hook"] = "O" if "O" in hook_resp.text.strip() else "X"

    for ts in sorted(frames.keys()):
        prod_resp = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                _image_part(frames[ts]),
                f"이 프레임({ts}초)에 스킨케어 제품(패드/세럼/아이패치 등 용기/패키지)이 보이면 예, 없으면 아니오만 답하세요."
            ]
        )
        if "예" in prod_resp.text or "yes" in prod_resp.text.lower():
            result["product_timing"] = f"{ts}초"
            break

    return result


def extract_subtitle_text(frames: dict) -> str:
    client = _get_client()
    if not frames:
        return ""

    texts = []
    prev_text = ""
    for ts in sorted(frames.keys()):
        resp = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                _image_part(frames[ts]),
                "이 프레임에 보이는 자막이나 텍스트를 그대로 출력하세요. 없으면 빈 문자열."
            ]
        )
        text = resp.text.strip()
        if text and text != prev_text:
            texts.append(text)
            prev_text = text

    return "\n".join(texts)
