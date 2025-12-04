"""
Email integration tool with SMTP and IMAP support.

Provides email sending and reading capabilities.
"""

import asyncio
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict, Any
import logging

from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult
from ..exceptions import ToolAuthenticationError, ToolExecutionError


logger = logging.getLogger(__name__)


class EmailTool(BaseTool):
    """
    Email sending and reading tool.
    
    Supports:
    - SMTP sending (Gmail, Outlook, custom servers)
    - HTML emails
    - Attachments
    - IMAP reading (planned)
    """
    
    name = "email"
    description = "Send and read emails via SMTP/IMAP"
    version = "1.0.0"
    category = ToolCategory.COMMUNICATION.value
    
    def __init__(self, **config):
        """
        Initialize Email tool.
        
        Args:
            smtp_server: SMTP server address (required)
            smtp_port: SMTP port (default: 587)
            username: Email username (required)
            password: Email password (required)
            from_email: Sender email address
            use_tls: Use TLS encryption (default: True)
        """
        super().__init__(**config)
        self.smtp_server = config.get("smtp_server")
        self.smtp_port = config.get("smtp_port", 587)
        self.username = config.get("username")
        self.password = config.get("password")
        self.from_email = config.get("from_email", self.username)
        self.use_tls = config.get("use_tls", True)
        
        if not all([self.smtp_server, self.username, self.password]):
            raise ToolAuthenticationError(
                "SMTP credentials required (smtp_server, username, password)",
                tool_name=self.name
            )
    
    def get_capabilities(self) -> List[str]:
        """Get email tool capabilities."""
        return ["email_sending", "html_email", "attachments"]
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get email tool parameters."""
        return [
            ToolParameter(
                name="action",
                type="string",
                description="Action to perform",
                required=True,
                enum=["send_email"]
            ),
            ToolParameter(
                name="to",
                type="string",
                description="Recipient email address",
                required=True
            ),
            ToolParameter(
                name="subject",
                type="string",
                description="Email subject",
                required=True
            ),
            ToolParameter(
                name="body",
                type="string",
                description="Email body text",
                required=True
            ),
            ToolParameter(
                name="html",
                type="string",
                description="HTML body (optional)",
                required=False
            ),
        ]
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        retries: int = 3
    ) -> ToolResult:
        """
        Send an email.
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Plain text body
            html: HTML body (optional)
            attachments: List of attachments (optional)
            retries: Number of retries
            
        Returns:
            ToolResult with send status
        """
        for attempt in range(retries):
            try:
                # Create message
                message = MIMEMultipart("alternative")
                message["Subject"] = subject
                message["From"] = self.from_email
                message["To"] = to
                
                # Add text and HTML parts
                text_part = MIMEText(body, "plain")
                message.attach(text_part)
                
                if html:
                    html_part = MIMEText(html, "html")
                    message.attach(html_part)
                
                # Add attachments
                if attachments:
                    for attachment in attachments:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.get("content", b""))
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename={attachment.get('filename', 'file')}"
                        )
                        message.attach(part)
                
                # Run blocking SMTP operations in thread pool
                await asyncio.to_thread(self._send_smtp, message, to)
                
                return ToolResult.success_result(
                    output={
                        "to": to,
                        "subject": subject,
                        "sent": True
                    },
                    tool_name=self.name,
                    metadata={"action": "send_email"}
                )
                
            except Exception as e:
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Email send failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                    continue
                raise ToolExecutionError(
                    f"Failed to send email: {str(e)}",
                    tool_name=self.name
                )
        
        raise ToolExecutionError(
            f"Email send failed after {retries} retries",
            tool_name=self.name
        )
    
    def _send_smtp(self, message: MIMEMultipart, to: str) -> None:
        """Send email via SMTP (blocking operation)."""
        context = ssl.create_default_context()
        
        if self.use_tls:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.send_message(message)
        else:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.username, self.password)
                server.send_message(message)
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute email action."""
        action = kwargs.get("action")
        
        if action == "send_email":
            return await self.send_email(
                to=kwargs.get("to"),
                subject=kwargs.get("subject"),
                body=kwargs.get("body"),
                html=kwargs.get("html"),
                attachments=kwargs.get("attachments")
            )
        else:
            return ToolResult.error_result(
                error=f"Unknown action: {action}",
                tool_name=self.name
            )
