"""User data caching to reduce database queries"""


class UserCache:
    def __init__(self):
        self._cache = {}
    
    def set_user(self, username, name):
        """Cache user data"""
        self._cache[username] = {'name': name}
    
    def get_name(self, username):
        """Get cached user name"""
        if username in self._cache:
            return self._cache[username].get('name')
        return None
    
    def update_name(self, username, new_name):
        """Update cached name"""
        if username in self._cache:
            self._cache[username]['name'] = new_name
    
    def clear(self):
        """Clear all cached data"""
        self._cache.clear()
    
    def remove_user(self, username):
        """Remove specific user from cache"""
        if username in self._cache:
            del self._cache[username]
