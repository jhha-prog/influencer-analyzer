import subprocess
import os


def has_audio_stream(video_path: str) -> bool:
    """오디오 스트림 존재 여부 확인"""
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'a',
         '-show_entries', 'stream=codec_type', '-of', 'default=nw=1',
         video_path],
        capture_output=True, text=True
    )
    return 'audio' in result.stdout


def extract_audio(video_path: str, output_path: str) -> bool:
    """오디오 추출. 성공 시 True 반환."""
    result = subprocess.run(
        ['ffmpeg', '-y', '-loglevel', 'error', '-i', video_path,
         '-q:a', '0', '-map', 'a', output_path],
        capture_output=True
    )
    return result.returncode == 0 and os.path.getsize(output_path) > 0


def extract_frames_at_timestamps(video_path: str, timestamps: list, output_dir: str) -> dict:
    """
    timestamps: [3, 10, 30, ...] (초 단위)
    반환: {3: '/tmp/frame_3s.jpg', 10: '/tmp/frame_10s.jpg', ...}
    존재하지 않는 타임스탬프(영상 길이 초과)는 딕셔너리에서 제외
    """
    result = {}
    for ts in timestamps:
        output_path = os.path.join(output_dir, f'frame_{ts}s.jpg')
        proc = subprocess.run(
            ['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(ts),
             '-i', video_path, '-vframes', '1', '-q:v', '2', output_path],
            capture_output=True
        )
        if proc.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            result[ts] = output_path
    return result


def get_video_duration(video_path: str) -> float:
    """영상 길이(초) 반환. 실패 시 0.0"""
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
        capture_output=True, text=True
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0
