"""
HTTP client wrapper for calling MCP servers via REST API.

MCP servers run as HTTP endpoints (typically localhost:3000-3005).
This module provides a Python client interface for calling MCP tools.
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class MCPHTTPClient:
    """HTTP client for MCP server communication."""

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize MCP HTTP client.

        Args:
            base_url: MCP server base URL (e.g., "http://localhost:3000")
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool via HTTP POST.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool response as dict

        Raises:
            requests.RequestException: If HTTP request fails
        """
        url = f"{self.base_url}/tools/{tool_name}"

        try:
            response = requests.post(
                url,
                json={"arguments": arguments},
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"MCP timeout calling {tool_name} on {self.base_url}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"MCP connection failed to {self.base_url}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"MCP HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"MCP call failed: {e}")
            raise

    def health_check(self) -> bool:
        """Check if MCP server is responsive."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


class EmailMCPClient(MCPHTTPClient):
    """Client for Email MCP server."""

    def __init__(self, base_url: str = "http://localhost:3000"):
        """
        Initialize Email MCP client.

        Args:
            base_url: Email MCP server URL (default: http://localhost:3000)
        """
        super().__init__(base_url)

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email via MCP server.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (HTML or plain text)
            cc: Optional CC recipients
            bcc: Optional BCC recipients

        Returns:
            Response with sent message ID
        """
        arguments = {
            "to": to,
            "subject": subject,
            "body": body
        }

        if cc:
            arguments["cc"] = cc
        if bcc:
            arguments["bcc"] = bcc

        return self.call_tool("send_email", arguments)


class CalendarMCPClient(MCPHTTPClient):
    """Client for Calendar MCP server."""

    def __init__(self, base_url: str = "http://localhost:3001"):
        """
        Initialize Calendar MCP client.

        Args:
            base_url: Calendar MCP server URL (default: http://localhost:3001)
        """
        super().__init__(base_url)

    def create_event(
        self,
        title: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Create calendar event via MCP server.

        Args:
            title: Event title
            start_time: Start time (ISO format)
            end_time: End time (ISO format)
            description: Event description
            location: Event location
            attendees: List of attendee email addresses

        Returns:
            Response with created event ID
        """
        arguments = {
            "title": title,
            "start_time": start_time,
            "end_time": end_time
        }

        if description:
            arguments["description"] = description
        if location:
            arguments["location"] = location
        if attendees:
            arguments["attendees"] = attendees

        return self.call_tool("create_event", arguments)


class SlackMCPClient(MCPHTTPClient):
    """Client for Slack MCP server."""

    def __init__(self, base_url: str = "http://localhost:3002"):
        """
        Initialize Slack MCP client.

        Args:
            base_url: Slack MCP server URL (default: http://localhost:3002)
        """
        super().__init__(base_url)

    def send_message(
        self,
        channel: str,
        text: str
    ) -> Dict[str, Any]:
        """
        Send message via Slack MCP server.

        Args:
            channel: Channel ID or name
            text: Message text

        Returns:
            Response with sent message timestamp
        """
        arguments = {
            "channel": channel,
            "text": text
        }

        return self.call_tool("send_message", arguments)


# Factory function for getting the right client
def get_mcp_client(service: str, base_url: Optional[str] = None) -> MCPHTTPClient:
    """
    Factory function to get the appropriate MCP client for a service.

    Args:
        service: Service name (email, calendar, slack)
        base_url: Optional base URL (uses defaults if not provided)

    Returns:
        MCP client instance

    Raises:
        ValueError: If service is not supported
    """
    default_urls = {
        "email": "http://localhost:3000",
        "calendar": "http://localhost:3001",
        "slack": "http://localhost:3002"
    }

    if service not in default_urls:
        raise ValueError(f"Unsupported MCP service: {service}. Supported: {list(default_urls.keys())}")

    url = base_url or default_urls[service]

    if service == "email":
        return EmailMCPClient(url)
    elif service == "calendar":
        return CalendarMCPClient(url)
    elif service == "slack":
        return SlackMCPClient(url)
    else:
        raise ValueError(f"No client implemented for service: {service}")
