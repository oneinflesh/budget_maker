"""Service layer for category management"""


class CategoryService:
    def __init__(self, db_manager):
        self.db = db_manager
    
    # Pastorate operations
    def get_all_pastorates(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name FROM pastorates ORDER BY name')
            return cursor.fetchall()
    
    def add_pastorate(self, name):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO pastorates (name) VALUES (?)', (name,))
            return cursor.lastrowid
    
    def update_pastorate(self, pastorate_id, name):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE pastorates SET name = ? WHERE id = ?', (name, pastorate_id))
    
    def delete_pastorate(self, pastorate_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # Check if used in budget
            cursor.execute('SELECT COUNT(*) FROM budget WHERE pastorate_id = ?', (pastorate_id,))
            if cursor.fetchone()[0] > 0:
                raise ValueError("Cannot delete: Pastorate is used in budget entries")
            cursor.execute('DELETE FROM pastorates WHERE id = ?', (pastorate_id,))
    
    # Year operations
    def get_all_years(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, year FROM years ORDER BY year DESC')
            return cursor.fetchall()
    
    def add_year(self, year):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO years (year) VALUES (?)', (year,))
            return cursor.lastrowid
    
    def update_year(self, year_id, year):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE years SET year = ? WHERE id = ?', (year, year_id))
    
    def delete_year(self, year_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM budget WHERE year_id = ?', (year_id,))
            if cursor.fetchone()[0] > 0:
                raise ValueError("Cannot delete: Year is used in budget entries")
            cursor.execute('DELETE FROM years WHERE id = ?', (year_id,))
    
    # Data Type operations
    def get_all_data_types(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, type_name FROM data_types ORDER BY type_name')
            return cursor.fetchall()
    
    def add_data_type(self, type_name):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO data_types (type_name) VALUES (?)', (type_name,))
            return cursor.lastrowid
    
    def update_data_type(self, data_type_id, type_name):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE data_types SET type_name = ? WHERE id = ?', (type_name, data_type_id))
    
    def delete_data_type(self, data_type_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM budget WHERE data_type_id = ?', (data_type_id,))
            if cursor.fetchone()[0] > 0:
                raise ValueError("Cannot delete: Data Type is used in budget entries")
            cursor.execute('DELETE FROM data_types WHERE id = ?', (data_type_id,))
    
    # Category operations
    def get_all_categories(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, category_name FROM categories ORDER BY category_name')
            return cursor.fetchall()
    
    def add_category(self, category_name):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO categories (category_name) VALUES (?)', (category_name,))
            return cursor.lastrowid
    
    def update_category(self, category_id, category_name):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE categories SET category_name = ? WHERE id = ?', (category_name, category_id))
    
    def delete_category(self, category_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM budget WHERE category_id = ?', (category_id,))
            if cursor.fetchone()[0] > 0:
                raise ValueError("Cannot delete: Category is used in budget entries")
            cursor.execute('SELECT COUNT(*) FROM items WHERE category_id = ?', (category_id,))
            if cursor.fetchone()[0] > 0:
                raise ValueError("Cannot delete: Category has items linked to it")
            cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))
    
    # Item operations
    def get_all_items(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT i.id, i.item_name, i.category_id, c.category_name 
                FROM items i
                JOIN categories c ON i.category_id = c.id
                ORDER BY c.category_name, i.item_name
            ''')
            return cursor.fetchall()
    
    def get_items_by_category(self, category_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, item_name FROM items WHERE category_id = ? ORDER BY display_order, item_name', (category_id,))
            return cursor.fetchall()
    
    def add_item(self, item_name, category_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO items (item_name, category_id) VALUES (?, ?)', (item_name, category_id))
            return cursor.lastrowid
    
    def update_item(self, item_id, item_name, category_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE items SET item_name = ?, category_id = ? WHERE id = ?', (item_name, category_id, item_id))
    
    def get_budget_entries_by_data_type(self, data_type_id):
        """Get all budget entries for a specific data type"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT b.year_id, b.pastorate_id, y.year, p.name, 
                       COALESCE(MIN(b.created_at), 'N/A') as created_at
                FROM budget b
                JOIN years y ON b.year_id = y.id
                JOIN pastorates p ON b.pastorate_id = p.id
                WHERE b.data_type_id = ?
                GROUP BY b.year_id, b.pastorate_id, y.year, p.name
                ORDER BY b.year_id DESC, b.pastorate_id
            ''', (data_type_id,))
            return cursor.fetchall()

    def delete_item(self, item_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM budget WHERE item_id = ?', (item_id,))
            if cursor.fetchone()[0] > 0:
                raise ValueError("Cannot delete: Item is used in budget entries")
            cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))
    
    def save_budget_entry(self, year_id, pastorate_id, data_type_id, category_id, item_id, amount):
        """Save a single budget entry"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO budget (pastorate_id, year_id, data_type_id, category_id, item_id, amount)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (pastorate_id, year_id, data_type_id, category_id, item_id, amount))
            return cursor.lastrowid

    def get_budget_entry_amounts(self, year_id, pastorate_id, data_type_id):
        """Get all amounts for a specific budget entry"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT item_id, amount
                FROM budget
                WHERE year_id = ? AND pastorate_id = ? AND data_type_id = ?
            ''', (year_id, pastorate_id, data_type_id))
            return {item_id: amount for item_id, amount in cursor.fetchall()}

    def delete_budget_entries(self, year_id, pastorate_id, data_type_id):
        """Delete all budget entries for a specific year/pastorate/data_type combination"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM budget
                WHERE year_id = ? AND pastorate_id = ? AND data_type_id = ?
            ''', (year_id, pastorate_id, data_type_id))
