"""Service for sending notifications to Microsoft Teams via webhook."""
import logging
import time
from typing import Optional

import requests
import click

logger = logging.getLogger(__name__)


class TeamsNotifier:
    """Service for sending notifications to Microsoft Teams."""
    
    def __init__(self, webhook_url: str, default_message: str):
        """Initialize Teams notifier.
        
        Args:
            webhook_url: Microsoft Teams webhook URL
            default_message: Default message to use if none provided
        """
        self.webhook_url = webhook_url
        self.default_message = default_message
        
    def send_notification(self, url: str, message: Optional[str] = None, webhook_url: Optional[str] = None) -> bool:
        """Send notification to Teams channel.
        
        Args:
            url: URL to include in the message (typically the GCS report URL)
            message: Custom message (uses default if None)
            webhook_url: Override webhook URL (uses default if None)
            
        Returns:
            True if notification was sent successfully, False otherwise
            
        Raises:
            click.ClickException: If all retry attempts fail
        """
        webhook = webhook_url or self.webhook_url
        msg = message or self.default_message
        
        # Create Teams message payload
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": "Rapport Dealer Disponible",
            "sections": [{
                "activityTitle": "Rapport Dealer",
                "activitySubtitle": msg,
                "facts": [{
                    "name": "Rapport:",
                    "value": f"[Voir le rapport]({self._convert_gs_to_https(url)})"
                }],
                "markdown": True
            }]
        }
        
        # Attempt to send with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    webhook,
                    json=payload,
                    timeout=10,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    logger.info(f"Teams notification sent successfully to {self._mask_webhook(webhook)}")
                    return True
                elif response.status_code >= 500:
                    # Server error, retry
                    logger.warning(f"Teams webhook returned {response.status_code}, attempt {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                else:
                    # Client error, don't retry
                    logger.error(f"Teams webhook returned {response.status_code}: {response.text}")
                    break
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Teams notification attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
        
        # All attempts failed
        error_msg = f"Failed to send Teams notification after {max_retries} attempts"
        logger.error(error_msg)
        raise click.ClickException(error_msg)
    
    def _convert_gs_to_https(self, gs_url: str) -> str:
        """Convert gs:// URL to HTTPS URL for Teams compatibility.
        
        Args:
            gs_url: GCS URL in gs://bucket/path format
            
        Returns:
            HTTPS URL for accessing the file
        """
        if gs_url.startswith('gs://'):
            # Convert gs://bucket/path to https://storage.googleapis.com/bucket/path
            path = gs_url[5:]  # Remove 'gs://'
            return f"https://storage.googleapis.com/{path}"
        return gs_url
    
    def _mask_webhook(self, webhook_url: str) -> str:
        """Mask webhook URL for logging to avoid exposing sensitive information."""
        if len(webhook_url) > 50:
            return webhook_url[:20] + "..." + webhook_url[-10:]
        return webhook_url[:10] + "..."
