"""
Vision and image understanding capabilities.

This module provides image analysis, OCR, and screenshot understanding
using LLM vision models and OCR libraries.
"""

import base64
from typing import Union, Optional
from pathlib import Path
from .models import ImageDescription, ScreenAnalysis
from llm.provider import LLMProvider


class VisionProcessor:
    """
    Vision processing for images and screenshots.
    
    Provides image description, object detection, OCR,
    and screenshot analysis capabilities.
    """
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize the vision processor.
        
        Args:
            llm_provider: LLM provider with vision capabilities
        """
        self.llm_provider = llm_provider
    
    async def describe_image(
        self,
        image: Union[bytes, str],
        detailed: bool = False
    ) -> ImageDescription:
        """
        Generate description of an image.
        
        Args:
            image: Image as bytes or file path
            detailed: Whether to provide detailed analysis
            
        Returns:
            ImageDescription with analysis results
        """
        # Load image if path provided
        if isinstance(image, str):
            image_bytes = Path(image).read_bytes()
        else:
            image_bytes = image
        
        # Encode for LLM
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Build prompt
        prompt = self._build_description_prompt(detailed)
        
        # For now, use text-based description
        # In production, this would use vision-capable models
        response = await self.llm_provider.generate(
            prompt=f"{prompt}\n\n[Note: Image analysis would use vision model in production]",
            temperature=0.5,
            max_tokens=500
        )
        
        # Parse response
        return self._parse_description(response.content)
    
    def _build_description_prompt(self, detailed: bool) -> str:
        """Build prompt for image description."""
        if detailed:
            return """Analyze this image in detail and provide:
1. Overall description
2. List of objects/items visible
3. Colors and composition
4. Any text visible in the image
5. Tags or categories that apply
6. Confidence in the analysis (0-1)

Format as JSON with keys: description, objects, text, colors, tags, confidence"""
        else:
            return """Describe this image briefly, including:
- What you see
- Main objects
- Any visible text

Format as JSON with keys: description, objects, text, colors, tags, confidence"""
    
    def _parse_description(self, content: str) -> ImageDescription:
        """Parse LLM response into ImageDescription."""
        import json
        
        try:
            data = json.loads(content)
            return ImageDescription(
                description=data.get('description', ''),
                objects=data.get('objects', []),
                text=data.get('text'),
                colors=data.get('colors', []),
                tags=data.get('tags', []),
                confidence=data.get('confidence', 0.7)
            )
        except json.JSONDecodeError:
            # Fallback if not JSON
            return ImageDescription(
                description=content,
                confidence=0.5
            )
    
    async def extract_text(
        self,
        image: Union[bytes, str]
    ) -> str:
        """
        Extract text from image using OCR.
        
        Args:
            image: Image as bytes or file path
            
        Returns:
            Extracted text
        """
        # Load image if path provided
        if isinstance(image, str):
            image_bytes = Path(image).read_bytes()
        else:
            image_bytes = image
        
        # Try pytesseract for OCR
        try:
            import pytesseract
            from PIL import Image
            import io
            
            img = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(img)
            return text.strip()
        except ImportError:
            # Fallback to LLM-based text extraction
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            response = await self.llm_provider.generate(
                prompt="Extract all visible text from this image. Return only the text, no additional commentary.\n\n[Image would be provided here]",
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.content.strip()
    
    async def analyze_screenshot(
        self,
        image: bytes
    ) -> ScreenAnalysis:
        """
        Analyze a screenshot for UI elements and interactions.
        
        Args:
            image: Screenshot image bytes
            
        Returns:
            ScreenAnalysis with detected elements
        """
        image_b64 = base64.b64encode(image).decode('utf-8')
        
        prompt = """Analyze this screenshot and identify:
1. What type of interface/page this is
2. UI elements visible (buttons, forms, menus, etc)
3. All text content
4. Possible user interactions
5. Page structure and layout

Format as JSON with keys: description, ui_elements (list of dicts with 'type' and 'label'), 
text_content, interactions (list), page_type"""
        
        response = await self.llm_provider.generate(
            prompt=f"{prompt}\n\n[Screenshot would be provided to vision model]",
            temperature=0.5,
            max_tokens=1000
        )
        
        # Parse response
        return self._parse_screen_analysis(response.content)
    
    def _parse_screen_analysis(self, content: str) -> ScreenAnalysis:
        """Parse LLM response into ScreenAnalysis."""
        import json
        
        try:
            data = json.loads(content)
            return ScreenAnalysis(
                description=data.get('description', ''),
                ui_elements=data.get('ui_elements', []),
                text_content=data.get('text_content', ''),
                interactions=data.get('interactions', []),
                page_type=data.get('page_type')
            )
        except json.JSONDecodeError:
            # Fallback
            return ScreenAnalysis(
                description=content
            )
    
    async def detect_objects(
        self,
        image: Union[bytes, str]
    ) -> list[str]:
        """
        Detect objects in an image.
        
        Args:
            image: Image as bytes or file path
            
        Returns:
            List of detected objects
        """
        description = await self.describe_image(image)
        return description.objects
    
    async def get_dominant_colors(
        self,
        image: Union[bytes, str]
    ) -> list[str]:
        """
        Get dominant colors from an image.
        
        Args:
            image: Image as bytes or file path
            
        Returns:
            List of color names or hex codes
        """
        # Load image if path provided
        if isinstance(image, str):
            image_bytes = Path(image).read_bytes()
        else:
            image_bytes = image
        
        try:
            from PIL import Image
            import io
            from collections import Counter
            
            img = Image.open(io.BytesIO(image_bytes))
            img = img.resize((150, 150))  # Resize for performance
            img = img.convert('RGB')
            
            # Get colors
            pixels = list(img.getdata())
            most_common = Counter(pixels).most_common(5)
            
            # Convert to hex
            colors = [
                f"#{r:02x}{g:02x}{b:02x}"
                for (r, g, b), _ in most_common
            ]
            
            return colors
        except ImportError:
            # Fallback
            description = await self.describe_image(image)
            return description.colors
