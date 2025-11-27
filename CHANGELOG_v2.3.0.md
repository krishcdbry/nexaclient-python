# NexaClient Python v2.3.0 - Change Streams Support

## New Features

### MongoDB-Style Change Streams

Added support for real-time change notifications over the network!

**Key Features:**
- Watch for database changes in real-time
- MongoDB-compatible API
- Works over network (no filesystem access needed)
- Can connect to remote NexaDB servers
- Filter by collection and operation type

**Usage:**

```python
from nexaclient import NexaClient

# Connect to NexaDB
client = NexaClient(host='localhost', port=6970, username='root', password='nexadb123')
client.connect()

# Watch for changes
for change in client.watch('orders'):
    if change['operationType'] == 'insert':
        print(f"New order: {change['fullDocument']}")
```

**Examples:**
- `examples/change_streams_example.py` - Complete working example

## API Changes

### New Methods

- `client.watch(collection=None, operations=None)` - Watch for database changes

### New Message Types

- `MSG_SUBSCRIBE_CHANGES = 0x30` - Subscribe to change streams
- `MSG_UNSUBSCRIBE_CHANGES = 0x31` - Unsubscribe from change streams
- `MSG_CHANGE_EVENT = 0x90` - Change event notification

## Change Event Format

All change events follow MongoDB's format:

```python
{
    'operationType': 'insert',  # insert, update, delete, dropCollection
    'ns': {
        'db': 'nexadb',
        'coll': 'orders'
    },
    'documentKey': {
        '_id': 'abc123def456'
    },
    'fullDocument': {  # Only for insert/update
        '_id': 'abc123def456',
        'customer': 'Alice',
        'total': 99.99,
        '_created_at': '2025-11-27T...',
        '_updated_at': '2025-11-27T...'
    },
    'updateDescription': {  # Only for update
        'updatedFields': {
            'status': 'shipped',
            'tracking': 'XYZ123'
        }
    },
    'timestamp': 1700000000.123
}
```

## Use Cases

Perfect for:
- Real-time notifications
- Cache invalidation
- Audit logging
- Data synchronization
- Analytics pipelines
- Event-driven architectures
- Microservices communication
- Real-time dashboards
- Workflow automation

## Requirements

- NexaDB v1.3.0 or higher
- Python 3.7+
- msgpack>=1.0.0

## Installation

```bash
pip install nexaclient==2.3.0
```

## Documentation

For complete documentation, see:
- Main NexaDB docs: https://github.com/krishcdbry/nexadb
- Change streams guide: `CHANGE_STREAMS_NETWORK.md` in main repo
