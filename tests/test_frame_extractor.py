import os
import tempfile
from unittest.mock import patch, MagicMock
from frame_extractor import has_audio_stream, extract_frames_at_timestamps


def test_has_audio_stream_returns_bool():
    with patch('frame_extractor.subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout='audio')
        result = has_audio_stream('fake.mp4')
    assert isinstance(result, bool)


def test_extract_frames_at_timestamps_returns_dict():
    with patch('frame_extractor.subprocess.run') as mock_run, \
         patch('frame_extractor.os.path.exists', return_value=True), \
         patch('frame_extractor.os.path.getsize', return_value=1000):
        mock_run.return_value = MagicMock(returncode=0)
        with tempfile.TemporaryDirectory() as tmpdir:
            timestamps = [3, 10, 30]
            result = extract_frames_at_timestamps('fake.mp4', timestamps, tmpdir)
    assert isinstance(result, dict)
    assert set(result.keys()) == {3, 10, 30}
