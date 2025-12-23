from database import get_db
from calculator import find_best_rate
from scraper import fetch_all_rates
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

def create_alert(user_id, user_name, target_rate, condition='above'):
    """
    Create a rate alert for a user.
    
    Args:
        user_id: LINE user ID
        user_name: User display name
        target_rate: Target exchange rate
        condition: 'above' or 'below'
    
    Returns:
        Alert creation result
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if user already has an active alert
        cursor.execute('''
            SELECT * FROM alerts
            WHERE user_id = ? AND active = 1
        ''', (user_id,))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing alert
            cursor.execute('''
                UPDATE alerts
                SET target_rate = ?, condition = ?, created_at = ?
                WHERE user_id = ? AND active = 1
            ''', (target_rate, condition, datetime.now(), user_id))
            
            conn.commit()
            
            return {
                'status': 'updated',
                'message': f'已更新预警: 当汇率{condition}时 {target_rate:.4f} 时提醒您'
            }
        else:
            # Create new alert
            cursor.execute('''
                INSERT INTO alerts (user_id, user_name, target_rate, condition)
                VALUES (?, ?, ?, ?)
            ''', (user_id, user_name, target_rate, condition))
            
            conn.commit()
            
            return {
                'status': 'created',
                'message': f'✅ 已设置预警: 当汇率高于 {target_rate:.4f} 时提醒您\n\n输入 "取消预警" 可关闭通知'
            }

def cancel_alert(user_id):
    """Cancel active alerts for a user."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE alerts
            SET active = 0
            WHERE user_id = ? AND active = 1
        ''', (user_id,))
        
        cancelled = cursor.rowcount
        conn.commit()
        
        if cancelled > 0:
            return {
                'status': 'success',
                'message': '✅ 已取消汇率预警'
            }
        else:
            return {
                'status': 'none',
                'message': '您目前没有活跃的汇率预警'
            }

def get_user_alerts(user_id):
    """Get active alerts for a user."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM alerts
            WHERE user_id = ? AND active = 1
        ''', (user_id,))
        
        return [dict(row) for row in cursor.fetchall()]

def check_alerts_and_notify():
    """
    Background task: Check current rates against all active alerts.
    Returns list of users to notify with their alert details.
    
    This should be called periodically (e.g., every 30 minutes).
    """
    # Fetch current rates
    current_rates = fetch_all_rates()
    best_rate = find_best_rate(current_rates, 'buying_tt')
    
    if not best_rate:
        logging.warning("No valid rates to check alerts against")
        return []
    
    current_best_rate = best_rate['buying_tt']
    
    notifications = []
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get all active alerts
        cursor.execute('SELECT * FROM alerts WHERE active = 1')
        alerts = cursor.fetchall()
        
        for alert in alerts:
            should_notify = False
            
            if alert['condition'] == 'above' and current_best_rate >= alert['target_rate']:
                should_notify = True
            elif alert['condition'] == 'below' and current_best_rate <= alert['target_rate']:
                should_notify = True
            
            if should_notify:
                notifications.append({
                    'user_id': alert['user_id'],
                    'user_name': alert['user_name'],
                    'target_rate': alert['target_rate'],
                    'current_rate': current_best_rate,
                    'provider': best_rate['provider'],
                    'message': f"🔔 **汇率预警触发!**\n\n"
                              f"目标汇率: {alert['target_rate']:.4f}\n"
                              f"当前最佳: {current_best_rate:.4f}\n"
                              f"提供方: {best_rate['provider']}\n\n"
                              f"现在是兑换的好时机! 💰"
                })
                
                # Mark alert as triggered
                cursor.execute('''
                    UPDATE alerts
                    SET active = 0, triggered_at = ?
                    WHERE alert_id = ?
                ''', (datetime.now(), alert['alert_id']))
        
        conn.commit()
    
    logging.info(f"Checked alerts: {len(notifications)} notifications to send")
    return notifications

if __name__ == "__main__":
    from database import init_database
    init_database()
    
    # Test alert creation
    result = create_alert("test_user", "Test User", 4.55, "above")
    print(result)
    
    # Test alert checking
    notifications = check_alerts_and_notify()
    print(f"Notifications: {notifications}")
