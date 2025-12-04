"""
Tests for multimodal capabilities.

This module tests vision, document parsing, and audio processing.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from multimodal import (
    VisionProcessor,
    DocumentParser,
    AudioProcessor,
    ImageDescription,
    ScreenAnalysis,
    ParsedDocument,
    Transcription,
)


@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing."""
    provider = AsyncMock()
    
    async def mock_generate(prompt, **kwargs):
        response = MagicMock()
        
        # Return JSON-like responses for vision
        if "image" in prompt.lower() or "describe" in prompt.lower():
            response.content = '{"description": "Test image", "objects": ["object1"], "text": "test text", "colors": ["red"], "tags": ["test"], "confidence": 0.8}'
        elif "screenshot" in prompt.lower():
            response.content = '{"description": "UI screenshot", "ui_elements": [{"type": "button", "label": "Click"}], "text_content": "test", "interactions": ["click"], "page_type": "web"}'
        elif "summarize" in prompt.lower():
            response.content = "This is a test summary of the content."
        elif "key points" in prompt.lower():
            response.content = "- Point 1\n- Point 2\n- Point 3"
        else:
            response.content = "Test response"
        
        response.model = "test-model"
        return response
    
    provider.generate = mock_generate
    return provider


# Vision Tests
@pytest.mark.asyncio
async def test_describe_image(mock_llm_provider):
    """Test image description."""
    processor = VisionProcessor(mock_llm_provider)
    
    # Create dummy image bytes
    image_bytes = b"fake image data"
    
    description = await processor.describe_image(image_bytes)
    
    assert isinstance(description, ImageDescription)
    assert description.description is not None
    assert isinstance(description.objects, list)
    assert isinstance(description.confidence, float)


@pytest.mark.asyncio
async def test_extract_text(mock_llm_provider):
    """Test text extraction from image."""
    processor = VisionProcessor(mock_llm_provider)
    
    image_bytes = b"fake image data"
    
    text = await processor.extract_text(image_bytes)
    
    assert isinstance(text, str)


@pytest.mark.asyncio
async def test_analyze_screenshot(mock_llm_provider):
    """Test screenshot analysis."""
    processor = VisionProcessor(mock_llm_provider)
    
    screenshot_bytes = b"fake screenshot data"
    
    analysis = await processor.analyze_screenshot(screenshot_bytes)
    
    assert isinstance(analysis, ScreenAnalysis)
    assert analysis.description is not None
    assert isinstance(analysis.ui_elements, list)
    assert isinstance(analysis.interactions, list)


@pytest.mark.asyncio
async def test_detect_objects(mock_llm_provider):
    """Test object detection."""
    processor = VisionProcessor(mock_llm_provider)
    
    image_bytes = b"fake image data"
    
    objects = await processor.detect_objects(image_bytes)
    
    assert isinstance(objects, list)


# Document Parser Tests
@pytest.mark.asyncio
async def test_parse_text_document():
    """Test parsing plain text document."""
    parser = DocumentParser()
    
    file_content = b"This is a test text document.\nWith multiple lines."
    
    doc = await parser.parse(file_content, "test.txt")
    
    assert isinstance(doc, ParsedDocument)
    assert doc.filename == "test.txt"
    assert doc.document_type == "text"
    assert "test text document" in doc.text_content


@pytest.mark.asyncio
async def test_parse_markdown():
    """Test parsing Markdown document."""
    parser = DocumentParser()
    
    markdown_content = b"""# Test Title

This is a test markdown document.

## Section 1

Content here.
"""
    
    doc = await parser.parse(markdown_content, "test.md")
    
    assert doc.filename == "test.md"
    assert doc.document_type == "markdown"
    assert doc.title == "Test Title"
    assert "test markdown" in doc.text_content.lower()


@pytest.mark.asyncio
async def test_parse_csv():
    """Test parsing CSV file."""
    parser = DocumentParser()
    
    csv_content = b"""Name,Age,City
John,30,New York
Jane,25,Los Angeles
"""
    
    doc = await parser.parse(csv_content, "test.csv")
    
    assert doc.filename == "test.csv"
    assert doc.document_type == "csv"
    assert len(doc.tables) == 1
    assert doc.tables[0].headers == ["Name", "Age", "City"]
    assert len(doc.tables[0].rows) == 2


@pytest.mark.asyncio
async def test_extract_tables():
    """Test extracting tables from document."""
    parser = DocumentParser()
    
    csv_content = b"""Col1,Col2
Value1,Value2
"""
    
    tables = await parser.extract_tables(csv_content, "test.csv")
    
    assert isinstance(tables, list)
    assert len(tables) == 1
    assert tables[0].headers == ["Col1", "Col2"]


@pytest.mark.asyncio
async def test_to_markdown():
    """Test converting document to markdown."""
    parser = DocumentParser()
    
    text_content = b"Test content"
    
    markdown = await parser.to_markdown(text_content, "test.txt")
    
    assert isinstance(markdown, str)
    assert "Test content" in markdown


# Audio Processor Tests
@pytest.mark.asyncio
async def test_transcribe_audio(mock_llm_provider):
    """Test audio transcription."""
    processor = AudioProcessor(mock_llm_provider)
    
    audio_bytes = b"fake audio data" * 1000  # Make it larger
    
    transcription = await processor.transcribe(audio_bytes)
    
    assert isinstance(transcription, Transcription)
    assert transcription.text is not None
    assert transcription.language is not None
    assert isinstance(transcription.confidence, float)
    assert transcription.duration_seconds > 0


@pytest.mark.asyncio
async def test_transcribe_with_language(mock_llm_provider):
    """Test transcription with language hint."""
    processor = AudioProcessor(mock_llm_provider)
    
    audio_bytes = b"fake audio data" * 1000
    
    transcription = await processor.transcribe(audio_bytes, language="es")
    
    assert transcription.language == "es"


@pytest.mark.asyncio
async def test_summarize_audio(mock_llm_provider):
    """Test audio summarization."""
    processor = AudioProcessor(mock_llm_provider)
    
    audio_bytes = b"fake audio data" * 1000
    
    summary = await processor.summarize_audio(audio_bytes)
    
    assert isinstance(summary, str)
    assert len(summary) > 0


@pytest.mark.asyncio
async def test_detect_language(mock_llm_provider):
    """Test language detection."""
    processor = AudioProcessor(mock_llm_provider)
    
    audio_bytes = b"fake audio data" * 1000
    
    language = await processor.detect_language(audio_bytes)
    
    assert isinstance(language, str)
    assert len(language) >= 2  # Language code like 'en', 'es'


@pytest.mark.asyncio
async def test_extract_key_points(mock_llm_provider):
    """Test extracting key points from audio."""
    processor = AudioProcessor(mock_llm_provider)
    
    audio_bytes = b"fake audio data" * 1000
    
    key_points = await processor.extract_key_points(audio_bytes)
    
    assert isinstance(key_points, list)


@pytest.mark.asyncio
async def test_get_full_summary(mock_llm_provider):
    """Test getting full audio summary."""
    processor = AudioProcessor(mock_llm_provider)
    
    audio_bytes = b"fake audio data" * 1000
    
    from multimodal.models import AudioSummary
    summary = await processor.get_full_summary(audio_bytes)
    
    assert isinstance(summary, AudioSummary)
    assert summary.summary is not None
    assert isinstance(summary.key_points, list)
    assert summary.duration_seconds > 0


@pytest.mark.asyncio
async def test_transcribe_with_timestamps(mock_llm_provider):
    """Test transcription with timestamps."""
    processor = AudioProcessor(mock_llm_provider)
    
    audio_bytes = b"fake audio data" * 1000
    
    words = await processor.transcribe_with_timestamps(audio_bytes)
    
    assert isinstance(words, list)


@pytest.mark.asyncio
async def test_transcribe_segments(mock_llm_provider):
    """Test transcription in segments."""
    processor = AudioProcessor(mock_llm_provider)
    
    audio_bytes = b"fake audio data" * 1000
    
    segments = await processor.transcribe_segments(audio_bytes)
    
    assert isinstance(segments, list)
    if segments:
        assert 'start' in segments[0]
        assert 'end' in segments[0]
        assert 'text' in segments[0]


# Integration Tests
@pytest.mark.asyncio
async def test_vision_with_file_path(mock_llm_provider, tmp_path):
    """Test vision processor with file path."""
    processor = VisionProcessor(mock_llm_provider)
    
    # Create temporary image file
    image_file = tmp_path / "test.jpg"
    image_file.write_bytes(b"fake image data")
    
    description = await processor.describe_image(str(image_file))
    
    assert isinstance(description, ImageDescription)


@pytest.mark.asyncio
async def test_document_parser_multiple_formats():
    """Test parsing multiple document formats."""
    parser = DocumentParser()
    
    test_cases = [
        (b"Plain text", "file.txt", "text"),
        (b"# Title\nContent", "file.md", "markdown"),
        (b"A,B\n1,2", "file.csv", "csv"),
    ]
    
    for content, filename, expected_type in test_cases:
        doc = await parser.parse(content, filename)
        assert doc.document_type == expected_type
        assert doc.filename == filename
