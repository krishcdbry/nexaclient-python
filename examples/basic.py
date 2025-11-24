#!/usr/bin/env python3
"""
Basic usage example for NexaDB Python client
"""

from nexadb import NexaClient


def main():
    print('=' * 60)
    print('NexaDB Python Client - Basic Usage Example')
    print('=' * 60)

    # Using context manager (recommended)
    with NexaClient(host='localhost', port=6970) as db:
        print('\n1️⃣  Connected to NexaDB')

        # Create user
        print('\n2️⃣  Creating user...')
        create_result = db.create('users', {
            'name': 'Alice Johnson',
            'email': 'alice@example.com',
            'age': 28,
            'role': 'developer'
        })
        print(f'✅ User created: {create_result}')

        user_id = create_result['document_id']

        # Get user
        print('\n3️⃣  Getting user...')
        user = db.get('users', user_id)
        print(f'✅ User retrieved: {user}')

        # Update user
        print('\n4️⃣  Updating user...')
        db.update('users', user_id, {
            'age': 29,
            'department': 'Engineering'
        })
        print('✅ User updated')

        # Get updated user
        updated_user = db.get('users', user_id)
        print(f'📝 Updated user: {updated_user}')

        # Create more users
        print('\n5️⃣  Creating more users...')
        db.batch_write('users', [
            {'name': 'Bob Smith', 'email': 'bob@example.com', 'age': 35, 'role': 'manager'},
            {'name': 'Carol White', 'email': 'carol@example.com', 'age': 42, 'role': 'director'},
            {'name': 'David Brown', 'email': 'david@example.com', 'age': 31, 'role': 'developer'}
        ])
        print('✅ Batch insert complete')

        # Query users
        print('\n6️⃣  Querying users...')
        developers = db.query('users', {'role': 'developer'}, limit=10)
        print(f'✅ Found {len(developers)} developers:')
        for dev in developers:
            print(f'   - {dev["name"]} ({dev["age"]} years old)')

        # Ping server
        print('\n7️⃣  Pinging server...')
        pong = db.ping()
        print(f'✅ Ping successful: {pong}')

        # Delete user
        print('\n8️⃣  Deleting user...')
        db.delete('users', user_id)
        print('✅ User deleted')

        # Verify deletion
        deleted_user = db.get('users', user_id)
        print(f'📝 User after deletion: {deleted_user}')

        print('\n' + '=' * 60)
        print('✅ All operations completed successfully!')
        print('=' * 60)
        print('\nPerformance Benefits:')
        print('  - 3-10x faster than HTTP/REST')
        print('  - Binary protocol with MessagePack')
        print('  - Persistent TCP connections')
        print('  - Context manager support')

    print('\n9️⃣  Disconnected (automatic via context manager)\n')


if __name__ == '__main__':
    main()
