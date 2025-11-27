#!/usr/bin/env python3
"""
NexaDB Change Streams Example (PyPI Package)
=============================================

This example shows how to use NexaDB change streams with the official PyPI package.

Install:
    pip install nexaclient

Run:
    python3 change_streams_example.py
"""

from nexaclient import NexaClient

print("=" * 70)
print("NexaDB Change Streams Example")
print("=" * 70)

# Connect to NexaDB (can be remote!)
client = NexaClient(
    host='localhost',
    port=6970,
    username='root',
    password='nexadb123'
)

print("\n[1/2] Connecting to NexaDB...")
client.connect()
print("✅ Connected!")

print("\n[2/2] Watching for changes on 'orders' collection...")
print("   (Keep this running, then insert orders in another terminal)\n")

# Watch for changes - just like MongoDB!
try:
    for change in client.watch('orders'):
        operation = change['operationType']
        collection = change['ns']['coll']

        if operation == 'insert':
            doc = change.get('fullDocument', {})
            print(f"\n✅ NEW ORDER:")
            print(f"   Customer: {doc.get('customer', 'Unknown')}")
            print(f"   Total: ${doc.get('total', 0):.2f}")
            print(f"   Order ID: {change['documentKey']['_id']}")

        elif operation == 'update':
            doc_id = change['documentKey']['_id']
            updates = change.get('updateDescription', {}).get('updatedFields', {})
            print(f"\n🔄 ORDER UPDATED:")
            print(f"   Order ID: {doc_id}")
            print(f"   Changes: {updates}")

        elif operation == 'delete':
            doc_id = change['documentKey']['_id']
            print(f"\n❌ ORDER DELETED:")
            print(f"   Order ID: {doc_id}")

except KeyboardInterrupt:
    print("\n\n👋 Stopped watching. Goodbye!")
    client.disconnect()
