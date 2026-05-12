from unittest.mock import patch, MagicMock
from text_analyzer import analyze_text

SAMPLE_TRANSCRIPT = """
My friends always ask how I get smooth skin.
The answer is proper skin prep with PDRN lifting pad.
Get 20% off today only - link in bio!
"""

def test_analyze_text_returns_required_keys():
    mock_response = MagicMock()
    mock_response.text = '{"discount": "O(초반)", "problem": "O(초반)", "tone": "뷰티 노하우"}'

    with patch('text_analyzer._get_model') as mock_model:
        mock_model.return_value.generate_content.return_value = mock_response
        result = analyze_text(SAMPLE_TRANSCRIPT)

    assert 'discount_appeal' in result
    assert 'problem_timing' in result
    assert 'content_tone' in result

def test_analyze_text_no_discount():
    mock_response = MagicMock()
    mock_response.text = '{"discount": "X", "problem": "O(초반)", "tone": "ASMR형"}'

    with patch('text_analyzer._get_model') as mock_model:
        mock_model.return_value.generate_content.return_value = mock_response
        result = analyze_text("No discount here, just skincare tips.")

    assert result['discount_appeal'] == 'X'
