"""Tests for communication tools."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from tools.communication.slack import SlackTool
from tools.communication.discord import DiscordTool
from tools.communication.telegram import TelegramTool
from tools.communication.email_tool import EmailTool
from tools.communication.twilio_sms import TwilioSMSTool
from tools.result import ToolResult
from tools.exceptions import ToolAuthenticationError


class TestSlackTool:
    """Tests for Slack integration tool."""
    
    def test_slack_tool_init_without_token(self):
        """Test Slack tool initialization fails without token."""
        with pytest.raises(ToolAuthenticationError):
            SlackTool()
    
    def test_slack_tool_init_with_token(self):
        """Test Slack tool initialization with token."""
        tool = SlackTool(token="xoxb-test-token")
        assert tool.name == "slack"
        assert tool.token == "xoxb-test-token"
    
    def test_slack_tool_capabilities(self):
        """Test Slack tool capabilities."""
        tool = SlackTool(token="xoxb-test-token")
        capabilities = tool.get_capabilities()
        assert "messaging" in capabilities
        assert "file_upload" in capabilities
        assert "channel_management" in capabilities
    
    @pytest.mark.asyncio
    async def test_slack_send_message_mock(self):
        """Test Slack send message with mock."""
        tool = SlackTool(token="xoxb-test-token")
        
        # Mock the HTTP request
        with patch.object(tool, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "ok": True,
                "ts": "1234567890.123456",
                "channel": "C0123456789"
            }
            
            result = await tool.send_message(
                channel="C0123456789",
                text="Test message"
            )
            
            assert result.success is True
            assert result.output["message_ts"] == "1234567890.123456"
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_slack_execute_send_message(self):
        """Test Slack execute with send_message action."""
        tool = SlackTool(token="xoxb-test-token")
        
        with patch.object(tool, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = ToolResult.success_result(
                output={"message_ts": "123"},
                tool_name="slack"
            )
            
            result = await tool.execute(
                action="send_message",
                channel="C0123456789",
                text="Test"
            )
            
            assert result.success is True
            mock_send.assert_called_once()


class TestDiscordTool:
    """Tests for Discord integration tool."""
    
    def test_discord_tool_init_without_token(self):
        """Test Discord tool initialization fails without token."""
        with pytest.raises(ToolAuthenticationError):
            DiscordTool()
    
    def test_discord_tool_init_with_token(self):
        """Test Discord tool initialization with token."""
        tool = DiscordTool(token="test-discord-token")
        assert tool.name == "discord"
        assert tool.token == "test-discord-token"
    
    def test_discord_tool_capabilities(self):
        """Test Discord tool capabilities."""
        tool = DiscordTool(token="test-discord-token")
        capabilities = tool.get_capabilities()
        assert "messaging" in capabilities
        assert "embeds" in capabilities
    
    @pytest.mark.asyncio
    async def test_discord_send_message(self):
        """Test Discord send message."""
        tool = DiscordTool(token="test-discord-token")
        
        with patch.object(tool, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "123456789",
                "channel_id": "987654321"
            }
            
            result = await tool.send_message(
                channel_id="987654321",
                content="Test message"
            )
            
            assert result.success is True
            assert result.output["message_id"] == "123456789"


class TestTelegramTool:
    """Tests for Telegram integration tool."""
    
    def test_telegram_tool_init_without_token(self):
        """Test Telegram tool initialization fails without token."""
        with pytest.raises(ToolAuthenticationError):
            TelegramTool()
    
    def test_telegram_tool_init_with_token(self):
        """Test Telegram tool initialization with token."""
        tool = TelegramTool(token="123456:ABC-DEF")
        assert tool.name == "telegram"
        assert tool.token == "123456:ABC-DEF"
    
    @pytest.mark.asyncio
    async def test_telegram_send_message(self):
        """Test Telegram send message."""
        tool = TelegramTool(token="123456:ABC-DEF")
        
        with patch.object(tool, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"message_id": 123}
            
            result = await tool.send_message(
                chat_id="123456789",
                text="Test message"
            )
            
            assert result.success is True
            assert result.output["message_id"] == 123


class TestEmailTool:
    """Tests for Email tool."""
    
    def test_email_tool_init_without_credentials(self):
        """Test Email tool initialization fails without credentials."""
        with pytest.raises(ToolAuthenticationError):
            EmailTool()
    
    def test_email_tool_init_with_credentials(self):
        """Test Email tool initialization with credentials."""
        tool = EmailTool(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            username="test@example.com",
            password="password123"
        )
        assert tool.name == "email"
        assert tool.smtp_server == "smtp.gmail.com"
    
    def test_email_tool_capabilities(self):
        """Test Email tool capabilities."""
        tool = EmailTool(
            smtp_server="smtp.gmail.com",
            username="test@example.com",
            password="password123"
        )
        capabilities = tool.get_capabilities()
        assert "email_sending" in capabilities
        assert "html_email" in capabilities


class TestTwilioSMSTool:
    """Tests for Twilio SMS tool."""
    
    def test_twilio_tool_init_without_credentials(self):
        """Test Twilio tool initialization fails without credentials."""
        with pytest.raises(ToolAuthenticationError):
            TwilioSMSTool()
    
    def test_twilio_tool_init_with_credentials(self):
        """Test Twilio tool initialization with credentials."""
        tool = TwilioSMSTool(
            account_sid="ACxxxxx",
            auth_token="token123",
            from_number="+1234567890"
        )
        assert tool.name == "twilio_sms"
        assert tool.account_sid == "ACxxxxx"
    
    @pytest.mark.asyncio
    async def test_twilio_send_sms(self):
        """Test Twilio send SMS."""
        tool = TwilioSMSTool(
            account_sid="ACxxxxx",
            auth_token="token123",
            from_number="+1234567890"
        )
        
        with patch.object(tool, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "sid": "SM123456",
                "status": "sent"
            }
            
            result = await tool.send_sms(
                to="+1987654321",
                body="Test SMS"
            )
            
            assert result.success is True
            assert result.output["message_sid"] == "SM123456"
