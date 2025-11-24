"""
NexaDB Python Client

Official Python client for NexaDB with binary protocol support.

Usage:
    from nexadb import NexaClient

    # Using context manager (recommended)
    with NexaClient(host='localhost', port=6970) as db:
        user = db.create('users', {'name': 'John', 'email': 'john@example.com'})
        print(user)

    # Manual connection management
    db = NexaClient(host='localhost', port=6970)
    db.connect()
    user = db.create('users', {'name': 'John', 'email': 'john@example.com'})
    db.disconnect()
"""

from .client import NexaClient

__version__ = '1.0.0'
__all__ = ['NexaClient']
