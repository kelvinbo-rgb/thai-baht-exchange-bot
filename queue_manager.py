from database import get_db
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

def join_queue(user_id, user_name, notes=None):
    """
    Add a customer to the queue.
    Returns queue_id and position.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if user already in queue
        cursor.execute('''
            SELECT * FROM queue 
            WHERE user_id = ? AND status = 'waiting'
        ''', (user_id,))
        
        existing = cursor.fetchone()
        if existing:
            position = get_position(user_id)
            return {
                'status': 'already_in_queue',
                'queue_id': existing['queue_id'],
                'position': position
            }
        
        # Add to queue
        cursor.execute('''
            INSERT INTO queue (user_id, user_name, notes)
            VALUES (?, ?, ?)
        ''', (user_id, user_name, notes))
        
        queue_id = cursor.lastrowid
        conn.commit()
        
        position = get_position(user_id)
        
        logging.info(f"User {user_name} ({user_id}) joined queue at position {position}")
        
        return {
            'status': 'success',
            'queue_id': queue_id,
            'position': position
        }

def get_position(user_id):
    """
    Get the position of a user in the queue.
    Returns the position number (1-indexed).
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get all waiting queue entries ordered by creation time
        cursor.execute('''
            SELECT queue_id, user_id FROM queue
            WHERE status = 'waiting'
            ORDER BY created_at ASC
        ''')
        
        entries = cursor.fetchall()
        
        for idx, entry in enumerate(entries, 1):
            if entry['user_id'] == user_id:
                return idx
        
        return None

def get_queue_status(user_id):
    """
    Get queue status for a specific user.
    Returns position and count of people ahead.
    """
    position = get_position(user_id)
    
    if position is None:
        return {
            'in_queue': False,
            'message': '您目前不在队列中 (You are not in the queue)'
        }
    
    ahead = position - 1
    
    return {
        'in_queue': True,
        'position': position,
        'ahead': ahead,
        'message': f'您前面还有 {ahead} 人 (There are {ahead} people ahead of you)'
    }

def get_next_customer():
    """
    Admin function: Get the next customer in queue.
    Marks their status as 'processing'.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM queue
            WHERE status = 'waiting'
            ORDER BY created_at ASC
            LIMIT 1
        ''')
        
        customer = cursor.fetchone()
        
        if not customer:
            return None
        
        # Mark as processing
        cursor.execute('''
            UPDATE queue
            SET status = 'processing'
            WHERE queue_id = ?
        ''', (customer['queue_id'],))
        
        conn.commit()
        
        return dict(customer)

def mark_completed(queue_id):
    """
    Admin function: Mark a customer as completed.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE queue
            SET status = 'completed', processed_at = ?
            WHERE queue_id = ?
        ''', (datetime.now(), queue_id))
        
        conn.commit()
        
        return True

def get_full_queue():
    """
    Admin function: Get the entire queue.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM queue
            WHERE status IN ('waiting', 'processing')
            ORDER BY created_at ASC
        ''')
        
        return [dict(row) for row in cursor.fetchall()]

def leave_queue(user_id):
    """
    Allow a user to leave the queue.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM queue
            WHERE user_id = ? AND status = 'waiting'
        ''', (user_id,))
        
        deleted = cursor.rowcount
        conn.commit()
        
        return deleted > 0

if __name__ == "__main__":
    # Test
    from database import init_database
    init_database()
    
    # Test queue operations
    result = join_queue("test_user_1", "Test User 1")
    print(f"Join result: {result}")
    
    status = get_queue_status("test_user_1")
    print(f"Status: {status}")
    
    full_queue = get_full_queue()
    print(f"Full queue: {full_queue}")
