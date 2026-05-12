import os
import tempfile
import shutil

from downloader import download_video
from transcriber import transcribe
from frame_extractor import has_audio_stream, extract_audio, extract_frames_at_timestamps, get_video_duration
from frame_analyzer import analyze_frames, extract_subtitle_text
from text_analyzer import analyze_text

FRAME_TIMESTAMPS = [3, 6, 10, 20, 30, 45, 60, 90, 120]

def process_video(url: str, product_category: str = '') -> dict:
    """
    영상 URL 하나를 처리해 분석 결과 딕셔너리 반환.
    오류 발생 시 '오류' 키에 메시지 담아 반환.
    """
    tmpdir = tempfile.mkdtemp()
    try:
        video_path, creator = download_video(url, tmpdir)
        audio_exists = has_audio_stream(video_path)

        transcript = ''
        if audio_exists:
            audio_path = os.path.join(tmpdir, 'audio.mp3')
            if not extract_audio(video_path, audio_path):
                raise RuntimeError('오디오 추출 실패 — ffmpeg 오류')
            transcript = transcribe(audio_path)

        duration = get_video_duration(video_path)
        timestamps = [t for t in FRAME_TIMESTAMPS if t <= duration]
        if not timestamps:
            timestamps = [1]
        frames = extract_frames_at_timestamps(video_path, timestamps, tmpdir)

        if not audio_exists:
            transcript = extract_subtitle_text(frames)

        frame_result = analyze_frames(frames)
        text_result = analyze_text(transcript) if transcript else {
            'discount_appeal': 'X', 'problem_timing': 'X', 'content_tone': ''
        }

        return {
            '소재명': creator,
            '제품군': product_category,
            '보이스': 'O' if audio_exists else 'X',
            '자막/텍스트유무': frame_result['has_subtitle'],
            '3초훅': frame_result['has_3s_hook'],
            '할인소구': text_result['discount_appeal'],
            '초반문제제시': text_result['problem_timing'],
            '콘텐츠톤': text_result['content_tone'],
            '제품등장타이밍': frame_result['product_timing'],
            '전체플로우': transcript,
            '오류': '',
        }

    except Exception as e:
        return {
            '소재명': url.split('/')[-1][:20],
            '제품군': product_category,
            '보이스': '', '자막/텍스트유무': '', '3초훅': '',
            '할인소구': '', '초반문제제시': '', '콘텐츠톤': '',
            '제품등장타이밍': '', '전체플로우': '',
            '오류': str(e),
        }
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
