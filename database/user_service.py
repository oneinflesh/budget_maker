"""User service layer for abstracting database operations"""


class UserService:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def update_username(self, old_username, new_username):
        """Update username across all tables"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET username = ? WHERE username = ?', 
                         (new_username, old_username))
            cursor.execute('UPDATE sessions SET username = ? WHERE username = ?', 
                         (new_username, old_username))
        return True
    
    def update_name(self, username, new_name):
        """Update user display name"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET name = ? WHERE username = ?', 
                         (new_name, username))
        # Update cache
        self.db.cache.update_name(username, new_name)
        return True
    
    def update_password(self, username, new_password):
        """Update user password with hashing"""
        hashed_password = self.db.hash_password(new_password)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET password = ? WHERE username = ?', 
                         (hashed_password, username))
        return True
    
    def get_user_info(self, username):
        """Get complete user information"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT username, name FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            if result:
                return {'username': result[0], 'name': result[1]}
            return None
