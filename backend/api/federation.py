"""
Federation utilities for sending/receiving content between nodes.

This module handles the actual HTTP communication with remote nodes.
It's separate from views.py to keep things organized.

TODO: Add proper retry logic with exponential backoff
TODO: Add signature verification for security
"""
import requests
import logging
from django.conf import settings
from users.models import Author

logger = logging.getLogger(__name__)


def get_node_credentials(node_url):
    """
    Get the credentials we use to authenticate with a remote node.
    Returns (username, password) tuple or None if no credentials found.
    """
    from api.models import Node
    try:
        node = Node.objects.get(url=node_url, is_active=True)
        if node.username and node.password:
            return (node.username, node.password)
    except Node.DoesNotExist:
        pass
    return None


def send_to_remote_inbox(author_url, data):
    """
    Send an item to a remote author's inbox.

    Args:
        author_url: The full URL of the remote author (e.g. http://othernode.com/api/authors/uuid/)
        data: The data to send (dict, will be JSON-serialized)

    Returns:
        True if successful, False otherwise
    """
    # Derive inbox URL from author URL
    inbox_url = author_url.rstrip('/') + '/inbox/'

    # Figure out which node this is from the author URL
    # Just take the scheme + host
    from urllib.parse import urlparse
    parsed = urlparse(author_url)
    node_url = f"{parsed.scheme}://{parsed.netloc}"

    credentials = get_node_credentials(node_url)

    try:
        kwargs = {
            'json': data,
            'timeout': 10,
            'headers': {
                'Content-Type': 'application/json',
                'User-Agent': f'Innkeeper/{settings.NODE_NAME}',
            }
        }

        if credentials:
            kwargs['auth'] = credentials

        response = requests.post(inbox_url, **kwargs)

        if response.status_code in [200, 201]:
            logger.info(f"Successfully sent to remote inbox: {inbox_url}")
            return True
        else:
            logger.warning(f"Remote inbox returned {response.status_code}: {inbox_url}")
            return False

    except requests.Timeout:
        logger.error(f"Timeout sending to remote inbox: {inbox_url}")
        return False
    except requests.ConnectionError:
        logger.error(f"Connection error sending to remote inbox: {inbox_url}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending to remote inbox {inbox_url}: {e}")
        return False


def fetch_remote_posts(node_url):
    """
    Fetch public posts from a remote node.
    Used for discovery/aggregation.

    Returns list of post dicts or empty list on error.
    """
    posts_url = f"{node_url.rstrip('/')}/api/posts/"

    from api.models import Node
    try:
        node = Node.objects.get(url=node_url, is_active=True)
        credentials = (node.username, node.password) if node.username else None
    except Node.DoesNotExist:
        credentials = None

    try:
        kwargs = {'timeout': 10}
        if credentials:
            kwargs['auth'] = credentials

        response = requests.get(posts_url, **kwargs)

        if response.status_code == 200:
            data = response.json()
            # Handle both paginated and non-paginated responses
            return data.get('results', data) if isinstance(data, dict) else data
        else:
            logger.warning(f"Failed to fetch remote posts from {node_url}: {response.status_code}")
            return []

    except Exception as e:
        logger.error(f"Error fetching remote posts from {node_url}: {e}")
        return []


def fetch_remote_authors(node_url):
    """
    Fetch authors from a remote node.
    Used to populate remote author info.
    """
    authors_url = f"{node_url.rstrip('/')}/api/authors/"

    from api.models import Node
    try:
        node = Node.objects.get(url=node_url, is_active=True)
        credentials = (node.username, node.password) if node.username else None
    except Node.DoesNotExist:
        credentials = None

    try:
        kwargs = {'timeout': 10}
        if credentials:
            kwargs['auth'] = credentials

        response = requests.get(authors_url, **kwargs)
        if response.status_code == 200:
            data = response.json()
            return data.get('results', data) if isinstance(data, dict) else data

    except Exception as e:
        logger.error(f"Error fetching remote authors from {node_url}: {e}")

    return []
