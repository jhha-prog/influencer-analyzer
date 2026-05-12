from unittest.mock import patch, MagicMock
from pipeline import process_video

def test_process_video_returns_all_columns():
    with patch('pipeline.download_video') as mock_dl, \
         patch('pipeline.has_audio_stream') as mock_audio, \
         patch('pipeline.extract_audio') as mock_extract, \
         patch('pipeline.transcribe') as mock_transcribe, \
         patch('pipeline.extract_frames_at_timestamps') as mock_frames, \
         patch('pipeline.analyze_frames') as mock_fanalyze, \
         patch('pipeline.analyze_text') as mock_tanalyze, \
         patch('pipeline.tempfile.mkdtemp') as mock_tmp, \
         patch('pipeline.shutil.rmtree'):

        mock_tmp.return_value = '/tmp/fake'
        mock_dl.return_value = ('/tmp/fake/video.mp4', 'testcreator')
        mock_audio.return_value = True
        mock_extract.return_value = True
        mock_transcribe.return_value = 'Sample transcript text'
        mock_frames.return_value = {3: '/tmp/f3.jpg', 10: '/tmp/f10.jpg'}
        mock_fanalyze.return_value = {
            'has_subtitle': 'O', 'has_3s_hook': 'X', 'product_timing': '10초'
        }
        mock_tanalyze.return_value = {
            'discount_appeal': 'X', 'problem_timing': 'O(초반)', 'content_tone': '뷰티 노하우'
        }

        result = process_video('https://tiktok.com/fake', '아이패치')

    required_cols = ['소재명', '제품군', '보이스', '자막/텍스트유무',
                     '3초훅', '할인소구', '초반문제제시', '콘텐츠톤',
                     '제품등장타이밍', '전체플로우', '오류']
    for col in required_cols:
        assert col in result, f"Missing column: {col}"

def test_process_video_error_returns_all_columns():
    """오류 발생 시에도 모든 컬럼 키가 있어야 한다."""
    with patch('pipeline.download_video') as mock_dl, \
         patch('pipeline.tempfile.mkdtemp') as mock_tmp, \
         patch('pipeline.shutil.rmtree'):
        mock_tmp.return_value = '/tmp/fake'
        mock_dl.side_effect = Exception("Download failed")
        result = process_video('https://tiktok.com/bad', '')

    required_cols = ['소재명', '제품군', '보이스', '자막/텍스트유무',
                     '3초훅', '할인소구', '초반문제제시', '콘텐츠톤',
                     '제품등장타이밍', '전체플로우', '오류']
    for col in required_cols:
        assert col in result, f"Missing column on error: {col}"
    assert result['오류'] != ''
