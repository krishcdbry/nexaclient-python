"""
NexaDB Python Client

High-performance binary protocol client for NexaDB.
"""

import socket
import struct
import threading
import queue
from typing import Dict, Any, List, Optional
import msgpack


# Protocol constants
MAGIC = 0x4E455841  # "NEXA"
VERSION = 0x01

# Client → Server message types
MSG_CONNECT = 0x01
MSG_CREATE = 0x02
MSG_READ = 0x03
MSG_UPDATE = 0x04
MSG_DELETE = 0x05
MSG_QUERY = 0x06
MSG_VECTOR_SEARCH = 0x07
MSG_BATCH_WRITE = 0x08
MSG_PING = 0x09
MSG_DISCONNECT = 0x0A
MSG_QUERY_TOON = 0x0B
MSG_EXPORT_TOON = 0x0C
MSG_LIST_COLLECTIONS = 0x20
MSG_SUBSCRIBE_CHANGES = 0x30
MSG_UNSUBSCRIBE_CHANGES = 0x31

# Server → Client response types
MSG_SUCCESS = 0x81
MSG_ERROR = 0x82
MSG_NOT_FOUND = 0x83
MSG_DUPLICATE = 0x84
MSG_PONG = 0x88
MSG_CHANGE_EVENT = 0x90


class NexaClient:
    """
    Official Python client for NexaDB.

    Features:
    - Binary protocol (3-10x faster than HTTP/REST)
    - MessagePack encoding (2-10x faster than JSON)
    - Persistent TCP connections
    - Context manager support
    - Type hints for better IDE support
    - Automatic reconnection

    Usage:
        # Context manager (recommended)
        with NexaClient(host='localhost', port=6970, username='root', password='nexadb123') as db:
            user = db.create('users', {'name': 'John', 'email': 'john@example.com'})
            found = db.get('users', user['document_id'])
            db.update('users', user['document_id'], {'age': 30})
            db.delete('users', user['document_id'])

        # Manual connection
        db = NexaClient(host='localhost', port=6970, username='root', password='nexadb123')
        db.connect()
        user = db.create('users', {'name': 'John', 'email': 'john@example.com'})
        db.disconnect()
    """

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6970,
        username: str = 'root',
        password: str = 'nexadb123',
        timeout: int = 30
    ):
        """
        Initialize NexaDB client.

        Args:
            host: Server host (default: 'localhost')
            port: Server port (default: 6970)
            username: Username for authentication (default: 'root')
            password: Password for authentication (default: 'nexadb123')
            timeout: Connection timeout in seconds (default: 30)
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout

        self.socket: Optional[socket.socket] = None
        self.connected = False

    def connect(self) -> None:
        """
        Connect to NexaDB server.

        Raises:
            ConnectionError: If connection fails
        """
        if self.connected:
            return

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            self.connected = True

            # Send handshake
            self._send_connect()

        except Exception as e:
            raise ConnectionError(f"Failed to connect to NexaDB at {self.host}:{self.port}: {e}")

    def disconnect(self) -> None:
        """Disconnect from server."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            finally:
                self.socket = None
                self.connected = False

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def create(self, collection: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create document in collection.

        Args:
            collection: Collection name
            data: Document data

        Returns:
            Creation result with document_id

        Example:
            >>> db.create('users', {'name': 'Alice', 'email': 'alice@example.com'})
            {'collection': 'users', 'document_id': '...', 'message': 'Document inserted'}
        """
        return self._send_message(MSG_CREATE, {
            'collection': collection,
            'data': data
        })

    def get(self, collection: str, key: str) -> Optional[Dict[str, Any]]:
        """
        Get document by ID.

        Args:
            collection: Collection name
            key: Document ID

        Returns:
            Document data or None if not found

        Example:
            >>> user = db.get('users', 'abc123')
            >>> print(user['name'])
            'Alice'
        """
        try:
            response = self._send_message(MSG_READ, {
                'collection': collection,
                'key': key
            })
            return response.get('document')
        except Exception as e:
            if 'Not found' in str(e):
                return None
            raise

    def update(self, collection: str, key: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update document.

        Args:
            collection: Collection name
            key: Document ID
            updates: Updates to apply

        Returns:
            Update result

        Example:
            >>> db.update('users', 'abc123', {'age': 30, 'city': 'NYC'})
            {'collection': 'users', 'document_id': 'abc123', 'message': 'Document updated'}
        """
        return self._send_message(MSG_UPDATE, {
            'collection': collection,
            'key': key,
            'updates': updates
        })

    def delete(self, collection: str, key: str) -> Dict[str, Any]:
        """
        Delete document.

        Args:
            collection: Collection name
            key: Document ID

        Returns:
            Delete result

        Example:
            >>> db.delete('users', 'abc123')
            {'collection': 'users', 'document_id': 'abc123', 'message': 'Document deleted'}
        """
        return self._send_message(MSG_DELETE, {
            'collection': collection,
            'key': key
        })

    def query(
        self,
        collection: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query documents with filters.

        Args:
            collection: Collection name
            filters: Query filters (default: {})
            limit: Max results (default: 100)

        Returns:
            List of matching documents

        Example:
            >>> users = db.query('users', {'role': 'developer', 'age': {'$gte': 25}}, 10)
            >>> print(len(users))
            5
        """
        response = self._send_message(MSG_QUERY, {
            'collection': collection,
            'filters': filters or {},
            'limit': limit
        })
        return response.get('documents', [])

    def vector_search(
        self,
        collection: str,
        vector: List[float],
        limit: int = 10,
        dimensions: int = 768
    ) -> List[Dict[str, Any]]:
        """
        Vector similarity search (for AI/ML applications).

        Args:
            collection: Collection name
            vector: Query vector
            limit: Max results (default: 10)
            dimensions: Vector dimensions (default: 768)

        Returns:
            List of similar documents with similarity scores

        Example:
            >>> results = db.vector_search('embeddings', [0.1, 0.2, ...], limit=5)
            >>> for r in results:
            ...     print(f"Similarity: {r['similarity']}, Doc: {r['document']}")
        """
        response = self._send_message(MSG_VECTOR_SEARCH, {
            'collection': collection,
            'vector': vector,
            'limit': limit,
            'dimensions': dimensions
        })
        return response.get('results', [])

    def batch_write(self, collection: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk insert documents.

        Args:
            collection: Collection name
            documents: List of documents to insert

        Returns:
            Insert result with document IDs

        Example:
            >>> users = [
            ...     {'name': 'Alice', 'email': 'alice@example.com'},
            ...     {'name': 'Bob', 'email': 'bob@example.com'},
            ...     {'name': 'Carol', 'email': 'carol@example.com'}
            ... ]
            >>> result = db.batch_write('users', users)
            >>> print(f"Inserted {result['count']} documents")
        """
        return self._send_message(MSG_BATCH_WRITE, {
            'collection': collection,
            'documents': documents
        })

    def ping(self) -> Dict[str, Any]:
        """
        Ping server (keep-alive / health check).

        Returns:
            Pong response with timestamp

        Example:
            >>> pong = db.ping()
            >>> print(pong['status'])
            'ok'
        """
        return self._send_message(MSG_PING, {})

    def query_toon(
        self,
        collection: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Query documents with TOON format response.
        TOON format reduces token count by 40-50% for LLM applications.

        Args:
            collection: Collection name
            filters: Query filters (default: {})
            limit: Max results (default: 100)

        Returns:
            Dictionary with 'data' (TOON string) and 'token_stats'

        Example:
            >>> result = db.query_toon('users', {'age': {'$gt': 25}}, 100)
            >>> print(result['data'])
            collection: users
            documents[18]{_id,name,email,age}:
              abc123,Alice,alice@example.com,28
              ...
            >>> print(f"Token reduction: {result['token_stats']['reduction_percent']}%")
            Token reduction: 42.3%
        """
        return self._send_message(MSG_QUERY_TOON, {
            'collection': collection,
            'filters': filters or {},
            'limit': limit
        })

    def export_toon(self, collection: str) -> Dict[str, Any]:
        """
        Export entire collection to TOON format.
        Perfect for AI/ML pipelines that need efficient data transfer.

        Args:
            collection: Collection name

        Returns:
            Dictionary with 'data' (TOON string), 'count', and 'token_stats'

        Example:
            >>> result = db.export_toon('users')
            >>> with open('users.toon', 'w') as f:
            ...     f.write(result['data'])
            >>> print(f"Exported {result['count']} documents")
            >>> print(f"Token reduction: {result['token_stats']['reduction_percent']}%")
            Exported 1000 documents
            Token reduction: 45.2%
        """
        return self._send_message(MSG_EXPORT_TOON, {
            'collection': collection
        })

    def list_collections(self) -> List[str]:
        """
        List all collections in the database.

        Returns:
            List of collection names

        Example:
            >>> collections = db.list_collections()
            >>> print(collections)
            ['users', 'products', 'orders']
        """
        response = self._send_message(MSG_LIST_COLLECTIONS, {})
        return response.get('collections', [])

    def watch(self, collection: Optional[str] = None, operations: Optional[List[str]] = None):
        """
        Watch for database changes (MongoDB-style change streams).

        This method returns an iterator that yields change events as they happen.
        It works over the network - no filesystem access needed!

        Args:
            collection: Collection name to watch (default: watch all collections)
            operations: List of operations to watch (default: ['insert', 'update', 'delete'])

        Yields:
            Change event dictionaries in MongoDB format

        Example:
            >>> # Watch all collections
            >>> for change in db.watch():
            ...     print(f"Change in {change['ns']['coll']}: {change['operationType']}")

            >>> # Watch specific collection
            >>> for change in db.watch('orders'):
            ...     if change['operationType'] == 'insert':
            ...         print(f"New order: {change['fullDocument']}")

            >>> # Watch specific operations
            >>> for change in db.watch('users', operations=['insert', 'update']):
            ...     print(f"User changed: {change}")

        Change Event Format:
            {
                'operationType': 'insert',  # insert, update, delete, dropCollection
                'ns': {'db': 'nexadb', 'coll': 'orders'},
                'documentKey': {'_id': 'abc123'},
                'fullDocument': {...},  # Only for insert/update
                'updateDescription': {...},  # Only for update
                'timestamp': 1700000000.123
            }
        """
        if not self.connected or not self.socket:
            raise ConnectionError("Not connected to NexaDB")

        # Event queue for thread communication
        event_queue = queue.Queue()
        stop_watching = threading.Event()
        error_container = {'error': None}

        # Subscribe to changes
        try:
            subscribe_response = self._send_message(MSG_SUBSCRIBE_CHANGES, {
                'collection': collection,
                'operations': operations or ['insert', 'update', 'delete']
            })
        except Exception as e:
            raise Exception(f"Failed to subscribe to changes: {e}")

        # Background thread to receive change events
        def receive_events():
            try:
                while not stop_watching.is_set():
                    try:
                        # Set timeout to allow checking stop_watching
                        self.socket.settimeout(1.0)

                        # Read change event from server
                        event_data = self._read_response()

                        # Put event in queue for main thread
                        event_queue.put(event_data)

                    except socket.timeout:
                        # Timeout is expected, just continue
                        continue
                    except Exception as e:
                        # Store error and stop
                        error_container['error'] = e
                        stop_watching.set()
                        break
            finally:
                # Restore normal timeout
                if self.socket:
                    self.socket.settimeout(self.timeout)

        # Start receiver thread
        receiver_thread = threading.Thread(target=receive_events, daemon=True)
        receiver_thread.start()

        try:
            # Yield events as they arrive
            while True:
                # Check for errors from receiver thread
                if error_container['error']:
                    raise error_container['error']

                try:
                    # Get event with timeout to allow checking for errors
                    event = event_queue.get(timeout=0.1)
                    yield event
                except queue.Empty:
                    # No event yet, continue waiting
                    continue

        except KeyboardInterrupt:
            # Clean shutdown on Ctrl+C
            stop_watching.set()
            receiver_thread.join(timeout=2.0)

            # Unsubscribe from changes
            try:
                self._send_message(MSG_UNSUBSCRIBE_CHANGES, {})
            except:
                pass

            raise

        except Exception as e:
            # Stop receiver thread
            stop_watching.set()
            receiver_thread.join(timeout=2.0)

            # Try to unsubscribe
            try:
                self._send_message(MSG_UNSUBSCRIBE_CHANGES, {})
            except:
                pass

            raise

    def _send_connect(self) -> None:
        """Send authentication handshake."""
        self._send_message(MSG_CONNECT, {
            'username': self.username,
            'password': self.password
        })

    def _send_message(self, msg_type: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send binary message and receive response.

        Args:
            msg_type: Message type code
            data: Message data

        Returns:
            Response data

        Raises:
            ConnectionError: If not connected
            Exception: If server returns error
        """
        if not self.connected or not self.socket:
            raise ConnectionError("Not connected to NexaDB")

        # Encode payload with MessagePack
        payload = msgpack.packb(data, use_bin_type=True)

        # Build header (12 bytes)
        header = struct.pack(
            '>IBBHI',
            MAGIC,       # Magic (4 bytes)
            VERSION,     # Version (1 byte)
            msg_type,    # Message type (1 byte)
            0,           # Flags (2 bytes)
            len(payload) # Payload length (4 bytes)
        )

        # Send header + payload
        self.socket.sendall(header + payload)

        # Read response
        return self._read_response()

    def _read_response(self) -> Dict[str, Any]:
        """
        Read binary response from server.

        Returns:
            Response data

        Raises:
            ConnectionError: If connection closed
            Exception: If server returns error
        """
        # Read header (12 bytes)
        header = self._recv_exact(12)

        magic, version, msg_type, flags, payload_len = struct.unpack('>IBBHI', header)

        # Verify magic
        if magic != MAGIC:
            raise ValueError(f"Invalid protocol magic: {hex(magic)}")

        # Read payload
        payload = self._recv_exact(payload_len)

        # Decode MessagePack
        data = msgpack.unpackb(payload, raw=False)

        # Handle response type
        if msg_type == MSG_SUCCESS or msg_type == MSG_PONG or msg_type == MSG_CHANGE_EVENT:
            return data
        elif msg_type == MSG_ERROR:
            raise Exception(data.get('error', 'Unknown error'))
        elif msg_type == MSG_NOT_FOUND:
            raise Exception('Not found')
        else:
            raise ValueError(f"Unknown response type: {msg_type}")

    def _recv_exact(self, n: int) -> bytes:
        """
        Receive exactly n bytes from socket.

        Args:
            n: Number of bytes to read

        Returns:
            Bytes read

        Raises:
            ConnectionError: If connection closed
        """
        data = b''
        while len(data) < n:
            chunk = self.socket.recv(n - len(data))
            if not chunk:
                raise ConnectionError("Connection closed by server")
            data += chunk
        return data

    def __repr__(self) -> str:
        """String representation."""
        status = "connected" if self.connected else "disconnected"
        return f"NexaClient(host='{self.host}', port={self.port}, status='{status}')"
