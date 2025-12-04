"""PDF generation tool."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class PDFGeneratorTool(BaseTool):
    name = "pdf_generator"
    description = "Generate PDFs from HTML or web pages"
    version = "1.0.0"
    category = ToolCategory.BROWSER.value
    
    def get_capabilities(self) -> List[str]:
        return ["generate"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [ToolParameter(name="source", type="string", description="HTML or URL", required=True)]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"source": kwargs.get("source")}, tool_name=self.name)
