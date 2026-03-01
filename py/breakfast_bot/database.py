from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
from datetime import datetime, date
from typing import List, Optional

class Database:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def create_order(self, user_id: int, username: str, room_number: str, 
                    breakfast_name: str, order_date: date, total_price: int) -> Optional[dict]:
        """Создать новый заказ"""
        try:
            data = {
                'user_id': user_id,
                'username': username,
                'room_number': room_number,
                'breakfast_name': breakfast_name,
                'order_date': order_date.isoformat(),
                'total_price': total_price,
                'status': 'pending_payment'
            }
            
            result = self.client.table('orders').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating order: {e}")
            return None
    
    def get_user_orders(self, user_id: int, limit: int = 10) -> List[dict]:
        """Получить заказы пользователя"""
        try:
            result = self.client.table('orders')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error getting user orders: {e}")
            return []
    
    def get_order_by_id(self, order_id: int, user_id: int) -> Optional[dict]:
        """Получить конкретный заказ по ID"""
        try:
            result = self.client.table('orders')\
                .select('*')\
                .eq('id', order_id)\
                .eq('user_id', user_id)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting order: {e}")
            return None
    
    def update_order_status(self, order_id: int, user_id: int, status: str) -> Optional[dict]:
        """Обновить статус заказа"""
        try:
            update_data = {'status': status}
            if status == 'paid':
                update_data['paid_at'] = datetime.now().isoformat()
            
            result = self.client.table('orders')\
                .update(update_data)\
                .eq('id', order_id)\
                .eq('user_id', user_id)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating order status: {e}")
            return None
    
    def get_todays_orders(self, user_id: int) -> List[dict]:
        """Получить сегодняшние заказы пользователя"""
        try:
            today = date.today().isoformat()
            result = self.client.table('orders')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('order_date', today)\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error getting today's orders: {e}")
            return []