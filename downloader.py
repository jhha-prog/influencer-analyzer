import yt_dlp
import os


def download_video(url: str, output_dir: str) -> tuple:
    """
    동영상을 다운로드합니다.

    Args:
        url: 동영상 URL (YouTube 등)
        output_dir: 다운로드할 디렉토리 경로

    Returns:
        (video_path, creator_name) 튜플

    Raises:
        예외 발생 시 호출자에게 전파
    """
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'format': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio/best',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if not filename.endswith('.mp4'):
            filename = os.path.splitext(filename)[0] + '.mp4'
        creator = info.get('uploader') or info.get('channel') or info.get('id', 'unknown')
    return filename, creator
