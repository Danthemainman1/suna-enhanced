"""
Multi-channel notification service.

This module provides notification capabilities through webhooks, email,
Slack, and Discord channels.
"""

import asyncio
import aiohttp
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
from .models import (
    TaskEvent,
    NotificationChannel,
    NotificationChannelType,
    WebhookConfig,
    EmailConfig,
    SlackConfig,
    DiscordConfig
)


class NotificationService:
    """
    Multi-channel notification service.
    
    Sends notifications about task events through various channels
    including webhooks, email, Slack, and Discord.
    """
    
    def __init__(self):
        """Initialize the notification service."""
        self._channels: dict[str, NotificationChannel] = {}
        self._webhook_configs: dict[str, WebhookConfig] = {}
        self._email_config: Optional[EmailConfig] = None
    
    async def notify(
        self,
        task_id: str,
        event: TaskEvent,
        channels: list[NotificationChannel]
    ):
        """
        Send notifications through specified channels.
        
        Args:
            task_id: Task identifier
            event: The event to notify about
            channels: List of notification channels to use
        """
        # Send notifications concurrently to all channels
        tasks = []
        
        for channel in channels:
            if not channel.enabled:
                continue
            
            if channel.channel_type == NotificationChannelType.WEBHOOK:
                if channel.webhook_config:
                    tasks.append(self._send_webhook(event, channel.webhook_config))
            
            elif channel.channel_type == NotificationChannelType.EMAIL:
                if channel.email_config:
                    tasks.append(self._send_email(event, channel.email_config))
            
            elif channel.channel_type == NotificationChannelType.SLACK:
                if channel.slack_config:
                    tasks.append(self._send_slack(event, channel.slack_config))
            
            elif channel.channel_type == NotificationChannelType.DISCORD:
                if channel.discord_config:
                    tasks.append(self._send_discord(event, channel.discord_config))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_webhook(self, event: TaskEvent, config: WebhookConfig):
        """Send webhook notification."""
        try:
            # Prepare payload
            payload = {
                'event_id': event.event_id,
                'task_id': event.task_id,
                'event_type': event.event_type.value,
                'timestamp': event.timestamp.isoformat(),
                'data': event.data
            }
            
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                **config.headers
            }
            
            # Add signature if secret is provided
            if config.secret:
                import hmac
                import hashlib
                signature = hmac.new(
                    config.secret.encode(),
                    json.dumps(payload).encode(),
                    hashlib.sha256
                ).hexdigest()
                headers['X-Webhook-Signature'] = signature
            
            # Send request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config.url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=config.timeout_seconds)
                ) as response:
                    response.raise_for_status()
        
        except Exception as e:
            print(f"Error sending webhook notification: {e}")
    
    async def _send_email(self, event: TaskEvent, config: EmailConfig):
        """Send email notification."""
        try:
            # Format subject and body
            subject = config.subject_template.format(
                event_type=event.event_type.value,
                task_id=event.task_id,
                timestamp=event.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            )
            
            body = config.body_template.format(
                event_type=event.event_type.value,
                task_id=event.task_id,
                timestamp=event.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                data=json.dumps(event.data, indent=2)
            )
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = config.smtp.from_email
            msg['To'] = ', '.join(config.to_emails)
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._send_smtp_email,
                config.smtp,
                msg
            )
        
        except Exception as e:
            print(f"Error sending email notification: {e}")
    
    def _send_smtp_email(self, smtp_config, msg):
        """Send email via SMTP (blocking, run in executor)."""
        if smtp_config.use_ssl:
            server = smtplib.SMTP_SSL(smtp_config.host, smtp_config.port)
        else:
            server = smtplib.SMTP(smtp_config.host, smtp_config.port)
            if smtp_config.use_tls:
                server.starttls()
        
        server.login(smtp_config.username, smtp_config.password)
        server.send_message(msg)
        server.quit()
    
    async def _send_slack(self, event: TaskEvent, config: SlackConfig):
        """Send Slack notification."""
        try:
            # Format message
            color = self._get_event_color(event.event_type.value)
            
            payload = {
                'username': config.username,
                'icon_emoji': config.icon_emoji,
                'attachments': [{
                    'color': color,
                    'title': f'Task Event: {event.event_type.value}',
                    'text': f'Task ID: `{event.task_id}`',
                    'fields': [
                        {
                            'title': 'Timestamp',
                            'value': event.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'),
                            'short': True
                        }
                    ],
                    'footer': 'Suna Ultra',
                    'ts': int(event.timestamp.timestamp())
                }]
            }
            
            # Add channel if specified
            if config.channel:
                payload['channel'] = config.channel
            
            # Add event data as fields
            for key, value in event.data.items():
                payload['attachments'][0]['fields'].append({
                    'title': key,
                    'value': str(value),
                    'short': True
                })
            
            # Send to Slack
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
        
        except Exception as e:
            print(f"Error sending Slack notification: {e}")
    
    async def _send_discord(self, event: TaskEvent, config: DiscordConfig):
        """Send Discord notification."""
        try:
            # Format embed
            color = self._get_event_color_int(event.event_type.value)
            
            embed = {
                'title': f'Task Event: {event.event_type.value}',
                'description': f'Task ID: `{event.task_id}`',
                'color': color,
                'timestamp': event.timestamp.isoformat(),
                'footer': {
                    'text': 'Suna Ultra'
                },
                'fields': []
            }
            
            # Add event data as fields
            for key, value in event.data.items():
                embed['fields'].append({
                    'name': key,
                    'value': str(value),
                    'inline': True
                })
            
            payload = {
                'embeds': [embed]
            }
            
            # Add username and avatar if specified
            if config.username:
                payload['username'] = config.username
            if config.avatar_url:
                payload['avatar_url'] = config.avatar_url
            
            # Send to Discord
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
        
        except Exception as e:
            print(f"Error sending Discord notification: {e}")
    
    def _get_event_color(self, event_type: str) -> str:
        """Get color for event type (Slack format)."""
        colors = {
            'started': '#3498db',      # Blue
            'completed': '#2ecc71',     # Green
            'failed': '#e74c3c',        # Red
            'paused': '#f39c12',        # Orange
            'resumed': '#9b59b6',       # Purple
            'cancelled': '#95a5a6',     # Gray
            'progress_update': '#1abc9c'  # Teal
        }
        return colors.get(event_type, '#34495e')
    
    def _get_event_color_int(self, event_type: str) -> int:
        """Get color for event type (Discord format - integer)."""
        colors = {
            'started': 0x3498db,      # Blue
            'completed': 0x2ecc71,     # Green
            'failed': 0xe74c3c,        # Red
            'paused': 0xf39c12,        # Orange
            'resumed': 0x9b59b6,       # Purple
            'cancelled': 0x95a5a6,     # Gray
            'progress_update': 0x1abc9c  # Teal
        }
        return colors.get(event_type, 0x34495e)
    
    async def configure_webhook(
        self,
        webhook_id: str,
        url: str,
        secret: Optional[str] = None,
        headers: Optional[dict] = None,
        timeout_seconds: int = 30
    ) -> WebhookConfig:
        """
        Configure a webhook.
        
        Args:
            webhook_id: Unique webhook identifier
            url: Webhook URL
            secret: Optional secret for signing
            headers: Custom headers
            timeout_seconds: Request timeout
            
        Returns:
            WebhookConfig
        """
        config = WebhookConfig(
            url=url,
            secret=secret,
            headers=headers or {},
            timeout_seconds=timeout_seconds
        )
        
        self._webhook_configs[webhook_id] = config
        return config
    
    async def configure_email(
        self,
        smtp_config: EmailConfig
    ) -> EmailConfig:
        """
        Configure email notifications.
        
        Args:
            smtp_config: Email configuration
            
        Returns:
            EmailConfig
        """
        self._email_config = smtp_config
        return smtp_config
    
    def get_channel(self, channel_id: str) -> Optional[NotificationChannel]:
        """
        Get a notification channel by ID.
        
        Args:
            channel_id: Channel identifier
            
        Returns:
            NotificationChannel if found, None otherwise
        """
        return self._channels.get(channel_id)
    
    def add_channel(
        self,
        channel_id: str,
        channel: NotificationChannel
    ):
        """
        Add a notification channel.
        
        Args:
            channel_id: Channel identifier
            channel: Notification channel configuration
        """
        self._channels[channel_id] = channel
    
    def remove_channel(self, channel_id: str) -> bool:
        """
        Remove a notification channel.
        
        Args:
            channel_id: Channel identifier
            
        Returns:
            True if removed, False if not found
        """
        if channel_id in self._channels:
            del self._channels[channel_id]
            return True
        return False
