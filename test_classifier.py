from unittest.mock import patch, MagicMock
from classifier import classify_ticket
import pytest

def test_classify_ticket_billing():
    # Create a fake response that looks like OpenAI's response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "billing"
    
    # Replace the real OpenAI call with our fake during this test
    with patch("classifier.client.chat.completions.create", return_value=mock_response):
        result = classify_ticket("My payment failed and I was charged twice")
        
    # Verify the result
    assert result == "billing"
    
def test_classify_ticket_technical():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "technical"
    
    with patch("classifier.client.chat.completions.create", return_value = mock_response):
        result = classify_ticket("The app crashes every time I open it.")
        
    assert result == "technical"
    
def test_classify_ticket_general():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "general"
    
    with patch("classifier.client.chat.completions.create", return_value=mock_response):
        result = classify_ticket("What are your business hours?")
        
    assert result == "general"
    
def test_classify_ticket_empty():
    with pytest.raises(ValueError):
        classify_ticket("")