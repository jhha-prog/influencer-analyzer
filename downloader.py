import yt_dlp
import os
import tempfile


def download_video(url: str, output_dir: str) -> tuple:
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'format': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio/best',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }

    cookies_content = os.environ.get('INSTAGRAM_COOKIES', '')
    cookie_file = None
    if cookies_content.strip():
        cookie_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        cookie_file.write(cookies_content)
        cookie_file.flush()
        cookie_file.close()
        ydl_opts['cookiefile'] = cookie_file.name

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not filename.endswith('.mp4'):
                filename = os.path.splitext(filename)[0] + '.mp4'
            creator = info.get('uploader') or info.get('channel') or info.get('id', 'unknown')
        return filename, creator
    finally:
        if cookie_file:
            os.unlink(cookie_file.name)
