import sqlite3
import bcrypt
from pathlib import Path
from contextlib import contextmanager
from database.user_cache import UserCache


class DatabaseManager:
    def __init__(self, db_name='app.db'):
        self.db_path = Path(__file__).parent / db_name
        self.connection = None
        self.cache = UserCache()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _get_persistent_connection(self):
        """Get persistent connection for init only"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
        return self.connection
    
    def init_database(self):
        conn = self._get_persistent_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                remember_me INTEGER DEFAULT 0,
                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create master tables for budget categories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pastorates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS years (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id),
                UNIQUE(item_name, category_id)
            )
        ''')
        
        # Create main budget table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budget (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pastorate_id INTEGER NOT NULL,
                year_id INTEGER NOT NULL,
                data_type_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pastorate_id) REFERENCES pastorates(id),
                FOREIGN KEY (year_id) REFERENCES years(id),
                FOREIGN KEY (data_type_id) REFERENCES data_types(id),
                FOREIGN KEY (category_id) REFERENCES categories(id),
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        ''')
        
        # Insert default categories
        try:
            cursor.execute('INSERT INTO categories (category_name) VALUES (?)', ('Income',))
            cursor.execute('INSERT INTO categories (category_name) VALUES (?)', ('Expenses',))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        
        # Insert default data types
        try:
            cursor.execute('INSERT INTO data_types (type_name) VALUES (?)', ('Actual',))
            cursor.execute('INSERT INTO data_types (type_name) VALUES (?)', ('Budget',))
            cursor.execute('INSERT INTO data_types (type_name) VALUES (?)', ('Actual Estimate',))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        
        # Insert default financial years (2020-2021 to 2026-2027)
        default_years = [
            '2020-2021', '2021-2022', '2022-2023', '2023-2024',
            '2024-2025', '2025-2026', '2026-2027'
        ]
        for year in default_years:
            try:
                cursor.execute('INSERT INTO years (year) VALUES (?)', (year,))
                conn.commit()
            except sqlite3.IntegrityError:
                pass
        
        # Insert default items for Income category
        try:
            cursor.execute('SELECT id FROM categories WHERE category_name = ?', ('Income',))
            income_cat = cursor.fetchone()
            if income_cat:
                income_id = income_cat[0]
                income_items = [
                    'Opening Balance',  # First item at top
                    'Baptism Offertory', 'Church Offertory', 'Harvest Festival Offertory',
                    'Holy Communion Offertory', 'House Visit Offertory', 'Marriage Offertory',
                    'Miscellaneous Collection', 'Miscellaneous Income', 'Miscellaneous Offertory', 'Sangam - CW/ DW',
                    'Sangam - Sabai', 'Thanks Offertory',
                    'Tithe Offertory', 'Trumphat Festival', 'Interest Income - Diocesan office',
                    'Interest - FDR - Endowment', 'Intrest - saving Bank', 'Rock Hall ( From Diocese)',
                    'North Church Council - Grant', 'Clergy Salary & Allowance ( From Diocese)',
                    'Diocesan Catechist ( From Diocese)', 'Grant From Institution',
                    'Grant From Pastroate', 'Light Work Clergy ( From Diocese)',
                    'Wife Allowence ( From Diocese)', 'Canditate for Ordination',
                    'TDTA Packiam Ammal Siruvar Illam Off/ Coll', 'Vision',
                    'Child Care & Edn Development Centre', 'Anbin illam -Off/ Coll',
                    'Blind School Off/ Coll', 'Children Mission Off/ Coll',
                    'Communication Off/ Coll', 'Counselling Off/Coll',
                    'Deaf Ministry Off/Coll', 'Diocesan School Welfare Fund',
                    'Deaf School Off/Coll', 'DME Off/Coll', 'IMS Off/Coll',
                    'Jews Offertory', 'LCF Off/Coll', 'Mens - Off/ Coll',
                    'Mentally Rtd Off/ Coll', 'Pastorate School Welfare Funds Collection',
                    'Self Denial Offertory', 'Womens Off/ Coll', 'Youth Off/ Coll',
                    'Clergy Diocesan Pension Fund', 'Clergy Diocesan Provident Fund',
                    'Clergy Dio PF Loan Recovery', 'Clergy Income Tax',
                    'Clergy Staff Welfare Fund', 'Clergy & Staff Welfare Fund Loan',
                    'Clergy Vehicle Loan', 'Advances', 'Rent - Building', 'Donations - Receipt'
                ]
                for order, item in enumerate(income_items, start=1):
                    try:
                        cursor.execute('INSERT INTO items (item_name, category_id, display_order) VALUES (?, ?, ?)', 
                                     (item, income_id, order))
                        conn.commit()
                    except sqlite3.IntegrityError:
                        pass
        except Exception:
            pass
        
        # Insert default items for Expenses category
        try:
            cursor.execute('SELECT id FROM categories WHERE category_name = ?', ('Expenses',))
            expenses_cat = cursor.fetchone()
            if expenses_cat:
                expenses_id = expenses_cat[0]
                expenses_items = [
                    'Opening Deficit',  # First item at top
                    'Furniture & Fittings', 'Land Purchased', 'Office Equipments',
                    'Building Working in Progress', 'Salary (STAFF)', 'Interest Paid',
                    'Donations Payment', 'Payment to Centre for Rural Women Development',
                    'Payment to TDTA Packiam Ammal Siruvar Illam', 'Payment to Vison',
                    'Payment to Social Welfare Department', 'Payment to Institution',
                    'Payment to Child Care & Edn Development Centre', 'Payment to Ecology Department',
                    'Assessment to Diocese (From Pastorate)', 'Payment to Anbin Illam',
                    'Payment to Blind School', 'Payment to Central CC',
                    'Payment to Children Mission', 'Payment to Communication',
                    'Payment to Confirmation Offertory', 'Payment to Counselling',
                    'Payment to Deaf Ministry', 'Payment to Diocesan Magazine',
                    'Payment to Diocesan School Welfare Fund', 'Payment to DME',
                    'Payment to Jews Offertory', 'Payment to Mens',
                    'Payment to Mentally Rtd', 'Payment to North CC',
                    'Payment to North West CC', 'Payment to Pastorate',
                    'Payment to Self Denial', 'Payment to Shalom Home for Aged',
                    'Payment to South CC', 'Payment to South West CC',
                    'Payment to West CC', 'Payment to Womens.', 'Payment to Youth',
                    'Clergy Diocesan Pension Fund', 'Clergy Diocesan Provident Fund',
                    'Clergy Dio PF Loan Recovery', 'Clergy Income Tax',
                    'Clergy Staff Welfare Fund', 'Clergy Vehicle Loan',
                    'Audit Fees', 'Electricity Church', 'Electricty Parsonage',
                    'Hospitality', 'Legal and Professional Charges', 'Miscellaneous Expenses',
                    'Printing and Stationery', 'Property Maintenance', 'Rates & Property Taxes',
                    'Repair and Maintenance - Building', 'Repair and Maintenance - Plant and Equipment',
                    'School Exepenses', 'Telephone Bill - Office', 'Telephone Bill - Parsonage',
                    'Travelling and Conveyance', 'Charge Allowance', 'Pastorate Allowance',
                    'Clergy Salary & Allowances', 'Committee Conferrence and Meeting',
                    'Convention', 'Fasting Prayer Expenses', 'Festival Expenses',
                    'Harvest Festival Expenses', 'Holy Communion Expenses', 'IMS Payment',
                    'Payment to LCF', 'Retreat Expenses', 'Trumphet Festival Expenses',
                    'VBS', 'Wife Allowance Payment', 'Advances'
                ]
                for order, item in enumerate(expenses_items, start=1):
                    try:
                        cursor.execute('INSERT INTO items (item_name, category_id, display_order) VALUES (?, ?, ?)', 
                                     (item, expenses_id, order))
                        conn.commit()
                    except sqlite3.IntegrityError:
                        pass
        except Exception:
            pass
        
        # Check if name column exists, if not add it
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'name' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN name TEXT')
            # Update existing users with default name
            cursor.execute('UPDATE users SET name = username WHERE name IS NULL')
            conn.commit()
        
        # Create default user with password "1234"
        hashed_password = self.hash_password('1234')
        try:
            cursor.execute('INSERT INTO users (username, password, name) VALUES (?, ?, ?)', 
                         ('admin', hashed_password, 'Administrator'))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        
        # Close persistent connection after init
        self.close()
    
    def hash_password(self, password):
        """Hash password using bcrypt with salt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_login(self, username, password):
        """Verify login credentials using bcrypt"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            
            if result is None:
                return False
            
            stored_hash = result[0]
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    
    def save_session(self, username, remember_me=False):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM sessions')
            cursor.execute('INSERT INTO sessions (username, remember_me) VALUES (?, ?)', 
                          (username, 1 if remember_me else 0))
    
    def get_saved_session(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT username FROM sessions WHERE remember_me = 1')
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_user_name(self, username):
        # Check cache first
        cached_name = self.cache.get_name(username)
        if cached_name:
            return cached_name
        
        # Query database if not cached
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT name FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            name = result[0] if result and result[0] else username
            
            # Cache the result
            self.cache.set_user(username, name)
            return name
    
    def clear_session(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sessions')
        # Clear cache on logout
        self.cache.clear()
    
    def close(self):
        """Close persistent connection and clear cache"""
        if self.connection:
            self.connection.close()
            self.connection = None
        self.cache.clear()
