import os
from groq import Groq

_client = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ['GROQ_API_KEY'])
    return _client

def transcribe(audio_path: str) -> str:
    """
    오디오 파일을 텍스트로 변환.
    언어 자동 감지 (EN/JP/TH 등).
    반환: 텍스트 문자열
    """
    client = _get_client()
    with open(audio_path, 'rb') as f:
        response = client.audio.transcriptions.create(
            model='whisper-large-v3',
            file=f,
            response_format='text',
        )
    return response.strip()
