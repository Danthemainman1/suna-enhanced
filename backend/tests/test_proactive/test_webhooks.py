"""
Tests for proactive webhooks.
"""

import pytest
from proactive.webhooks import WebhookManager


@pytest.mark.asyncio
async def test_create_webhook():
    """Test creating a webhook."""
    webhook_manager = WebhookManager()
    
    webhook = await webhook_manager.create(
        workspace_id="ws-123",
        name="Test Webhook",
        trigger_id="trigger-123"
    )
    
    assert webhook is not None
    assert webhook.name == "Test Webhook"
    assert webhook.trigger_id == "trigger-123"
    assert webhook.is_active is True
    assert webhook.secret is not None


@pytest.mark.asyncio
async def test_list_webhooks():
    """Test listing webhooks."""
    webhook_manager = WebhookManager()
    
    await webhook_manager.create("ws-1", "Webhook 1", "trigger-1")
    await webhook_manager.create("ws-1", "Webhook 2", "trigger-2")
    
    webhooks = await webhook_manager.list("ws-1")
    assert len(webhooks) == 2


@pytest.mark.asyncio
async def test_regenerate_secret():
    """Test regenerating webhook secret."""
    webhook_manager = WebhookManager()
    
    webhook = await webhook_manager.create("ws-1", "Test", "trigger-1")
    old_secret = webhook.secret
    
    updated = await webhook_manager.regenerate_secret(webhook.id)
    assert updated is not None
    assert updated.secret != old_secret


@pytest.mark.asyncio
async def test_delete_webhook():
    """Test deleting a webhook."""
    webhook_manager = WebhookManager()
    
    webhook = await webhook_manager.create("ws-1", "Test", "trigger-1")
    
    success = await webhook_manager.delete(webhook.id)
    assert success is True
    
    result = await webhook_manager.get(webhook.id)
    assert result is None
