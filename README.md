# NexaDB Python Client

Official Python client for NexaDB - The high-performance, easy-to-use database.

## Features

- **3-10x faster than HTTP/REST** - Binary protocol with MessagePack encoding
- **Persistent TCP connections** - No HTTP overhead
- **Context manager support** - Pythonic `with` statement
- **Type hints** - Full type annotations for better IDE support
- **Automatic reconnection** - Built-in connection management
- **Connection pooling** - Handle 1000+ concurrent operations

## Installation

```bash
pip install nexadb
```

## Quick Start

```python
from nexadb import NexaClient

# Using context manager (recommended)
with NexaClient(host='localhost', port=6970) as db:
    # Create document
    user = db.create('users', {
        'name': 'John Doe',
        'email': 'john@example.com'
    })

    # Get document
    found = db.get('users', user['document_id'])

    # Update document
    db.update('users', user['document_id'], {'age': 30})

    # Query documents
    results = db.query('users', {'age': {'$gte': 25}})

    # Delete document
    db.delete('users', user['document_id'])
```

## API Reference

### Constructor

```python
db = NexaClient(host='localhost', port=6970, timeout=30)
```

**Parameters:**
- `host` (str) - Server host (default: 'localhost')
- `port` (int) - Server port (default: 6970)
- `timeout` (int) - Connection timeout in seconds (default: 30)

### Methods

#### `connect()`

Connect to NexaDB server.

```python
db = NexaClient()
db.connect()
```

#### `create(collection, data)`

Create document in collection.

```python
result = db.create('users', {
    'name': 'Alice',
    'email': 'alice@example.com'
})
# Returns: {'collection': 'users', 'document_id': '...', 'message': '...'}
```

#### `get(collection, key)`

Get document by ID.

```python
user = db.get('users', user_id)
# Returns: {'_id': '...', 'name': 'Alice', ...} or None
```

#### `update(collection, key, updates)`

Update document.

```python
db.update('users', user_id, {
    'age': 30,
    'department': 'Engineering'
})
```

#### `delete(collection, key)`

Delete document.

```python
db.delete('users', user_id)
```

#### `query(collection, filters, limit=100)`

Query documents with filters.

```python
results = db.query('users', {
    'role': 'developer',
    'age': {'$gte': 25}
}, limit=100)
# Returns: [{'_id': '...', 'name': '...', ...}, ...]
```

#### `batch_write(collection, documents)`

Bulk insert documents.

```python
db.batch_write('users', [
    {'name': 'Alice', 'email': 'alice@example.com'},
    {'name': 'Bob', 'email': 'bob@example.com'},
    {'name': 'Carol', 'email': 'carol@example.com'}
])
```

#### `vector_search(collection, vector, limit=10, dimensions=768)`

Vector similarity search (for AI/ML applications).

```python
results = db.vector_search('embeddings', [0.1, 0.2, ...], limit=10)
# Returns: [{'document_id': '...', 'similarity': 0.95, 'document': {...}}, ...]
```

#### `ping()`

Ping server (keep-alive / health check).

```python
pong = db.ping()
```

#### `disconnect()`

Disconnect from server.

```python
db.disconnect()
```

## Context Manager

The recommended way to use NexaClient is with a context manager:

```python
with NexaClient(host='localhost', port=6970) as db:
    # Connection is automatically established
    user = db.create('users', {'name': 'John'})
    # Connection is automatically closed when exiting the block
```

This ensures proper connection management and cleanup.

## Performance

NexaClient uses a custom binary protocol for maximum performance:

| Metric | HTTP/REST | NexaDB (Binary) | Improvement |
|--------|-----------|-----------------|-------------|
| Latency | 5-10ms | 1-2ms | 3-5x faster |
| Throughput | 1K ops/sec | 5-10K ops/sec | 5-10x faster |
| Bandwidth | 300KB | 62KB | 80% less |

## Examples

### Basic CRUD

```python
from nexadb import NexaClient

with NexaClient() as db:
    # Create
    user = db.create('users', {
        'name': 'Alice Johnson',
        'email': 'alice@example.com',
        'age': 28,
        'role': 'developer'
    })

    user_id = user['document_id']

    # Read
    found = db.get('users', user_id)
    print(f"Found user: {found['name']}")

    # Update
    db.update('users', user_id, {
        'age': 29,
        'department': 'Engineering'
    })

    # Delete
    db.delete('users', user_id)
```

### Batch Operations

```python
with NexaClient() as db:
    # Bulk insert
    users = [
        {'name': 'Alice', 'email': 'alice@example.com'},
        {'name': 'Bob', 'email': 'bob@example.com'},
        {'name': 'Carol', 'email': 'carol@example.com'}
    ]

    result = db.batch_write('users', users)
    print(f"Inserted {result['count']} users")
```

### Querying

```python
with NexaClient() as db:
    # Find all developers aged 25+
    developers = db.query('users', {
        'role': 'developer',
        'age': {'$gte': 25}
    }, limit=10)

    for user in developers:
        print(f"{user['name']} - {user['age']} years old")
```

### Vector Search

```python
import numpy as np
from nexadb import NexaClient

with NexaClient() as db:
    # Generate or load embedding vector
    query_vector = np.random.rand(768).tolist()

    # Search for similar documents
    results = db.vector_search('embeddings', query_vector, limit=5)

    for result in results:
        print(f"Similarity: {result['similarity']:.2f}")
        print(f"Document: {result['document']}")
```

## Requirements

- Python >= 3.7
- msgpack >= 1.0.0
- NexaDB server running on localhost:6970 (or custom host/port)

## NexaDB vs MongoDB

| Feature | MongoDB | NexaDB |
|---------|---------|---------|
| Setup | 15 min | 2 min (`brew install nexadb`) |
| Write speed | ~50K/s | ~89K/s |
| Memory | 2-4 GB | 111 MB |
| Protocol | Custom binary | Custom binary |
| Python client | `pymongo` | `nexadb` (this package) |

## License

MIT

## Links

- [NexaDB GitHub](https://github.com/krishcdbry/nexadb)
- [Python Client GitHub](https://github.com/krishcdbry/nexadb-python)
- [Documentation](https://nexadb.dev/docs)
- [NPM Client](https://www.npmjs.com/package/nexaclient)

## Contributing

Contributions are welcome! Please open an issue or PR on GitHub.

## Support

For support, please:
- Open an issue on [GitHub](https://github.com/krishcdbry/nexadb-python/issues)
- Email: support@nexadb.dev
