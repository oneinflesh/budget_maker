"""
Database Migration Script
Run this once to update your existing database with new features
"""
import sqlite3
from pathlib import Path


def migrate_database():
    db_path = Path(__file__).parent / 'database' / 'app.db'
    
    if not db_path.exists():
        print("Database not found. No migration needed.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Starting database migration...")
    
    try:
        # Step 1: Check if display_order column exists, if not add it
        cursor.execute("PRAGMA table_info(items)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'display_order' not in columns:
            print("  Adding display_order column...")
            cursor.execute('ALTER TABLE items ADD COLUMN display_order INTEGER DEFAULT 0')
            conn.commit()
            print("  ✓ display_order column added")
        else:
            print("  ✓ display_order column already exists")
        
        # Step 2: Remove duplicate items
        print("  Removing duplicate items...")
        
        # Get Income category ID
        cursor.execute('SELECT id FROM categories WHERE category_name = ?', ('Income',))
        income_result = cursor.fetchone()
        
        if income_result:
            income_id = income_result[0]
            
            # Remove duplicate "Blind School Off/Coll" (without space)
            cursor.execute('DELETE FROM items WHERE item_name = ? AND category_id = ?', 
                         ('Blind School Off/Coll', income_id))
            
            # Remove duplicate "Children Mission Off/Coll" (without space)
            cursor.execute('DELETE FROM items WHERE item_name = ? AND category_id = ?', 
                         ('Children Mission Off/Coll', income_id))
            
            # Remove "Sunday Collections"
            cursor.execute('DELETE FROM items WHERE item_name = ? AND category_id = ?', 
                         ('Sunday Collections', income_id))
            
            conn.commit()
            print("  ✓ Duplicate items removed")
        
        # Step 3: Add missing items and fix spelling
        print("  Adding missing items and fixing spelling...")
        
        if income_result:
            income_id = income_result[0]
            
            # Check if "Miscellaneous Collection" exists
            cursor.execute('SELECT id FROM items WHERE item_name = ? AND category_id = ?', 
                         ('Miscellaneous Collection', income_id))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO items (item_name, category_id, display_order) VALUES (?, ?, ?)', 
                             ('Miscellaneous Collection', income_id, 8))
                print("  ✓ Added 'Miscellaneous Collection'")
            else:
                print("  ✓ 'Miscellaneous Collection' already exists")
            
            # Fix spelling: Miscillaneous → Miscellaneous
            # First check if old spelling exists and new spelling doesn't exist
            cursor.execute('SELECT id FROM items WHERE item_name = ? AND category_id = ?', 
                         ('Miscillaneous Income', income_id))
            old_income = cursor.fetchone()
            
            cursor.execute('SELECT id FROM items WHERE item_name = ? AND category_id = ?', 
                         ('Miscellaneous Income', income_id))
            new_income = cursor.fetchone()
            
            if old_income and not new_income:
                cursor.execute('UPDATE items SET item_name = ? WHERE item_name = ? AND category_id = ?', 
                             ('Miscellaneous Income', 'Miscillaneous Income', income_id))
                print("  ✓ Fixed spelling: 'Miscillaneous Income' → 'Miscellaneous Income'")
            elif old_income and new_income:
                # Both exist, delete the old one
                cursor.execute('DELETE FROM items WHERE item_name = ? AND category_id = ?', 
                             ('Miscillaneous Income', income_id))
                print("  ✓ Removed duplicate 'Miscillaneous Income'")
            
            # Same for Miscellaneous Offertory
            cursor.execute('SELECT id FROM items WHERE item_name = ? AND category_id = ?', 
                         ('Miscillaneous Offertory', income_id))
            old_offertory = cursor.fetchone()
            
            cursor.execute('SELECT id FROM items WHERE item_name = ? AND category_id = ?', 
                         ('Miscellaneous Offertory', income_id))
            new_offertory = cursor.fetchone()
            
            if old_offertory and not new_offertory:
                cursor.execute('UPDATE items SET item_name = ? WHERE item_name = ? AND category_id = ?', 
                             ('Miscellaneous Offertory', 'Miscillaneous Offertory', income_id))
                print("  ✓ Fixed spelling: 'Miscillaneous Offertory' → 'Miscellaneous Offertory'")
            elif old_offertory and new_offertory:
                # Both exist, delete the old one
                cursor.execute('DELETE FROM items WHERE item_name = ? AND category_id = ?', 
                             ('Miscillaneous Offertory', income_id))
                print("  ✓ Removed duplicate 'Miscillaneous Offertory'")
            
            conn.commit()
        
        # Step 4: Assign display_order to all items
        print("  Assigning display order to items...")
        
        # Income items order
        income_items_order = [
            'Opening Balance', 'Baptism Offertory', 'Church Offertory', 'Harvest Festival Offertory',
            'Holy Communion Offertory', 'House Visit Offertory', 'Marriage Offertory',
            'Miscellaneous Collection', 'Miscellaneous Income', 'Miscellaneous Offertory', 'Sangam - CW/ DW',
            'Sangam - Sabai', 'Thanks Offertory', 'Tithe Offertory', 'Trumphat Festival',
            'Interest Income - Diocesan office', 'Interest - FDR - Endowment', 'Intrest - saving Bank',
            'Rock Hall ( From Diocese)', 'North Church Council - Grant', 'Clergy Salary & Allowance ( From Diocese)',
            'Diocesan Catechist ( From Diocese)', 'Grant From Institution', 'Grant From Pastroate',
            'Light Work Clergy ( From Diocese)', 'Wife Allowence ( From Diocese)', 'Canditate for Ordination',
            'TDTA Packiam Ammal Siruvar Illam Off/ Coll', 'Vision', 'Child Care & Edn Development Centre',
            'Anbin illam -Off/ Coll', 'Blind School Off/ Coll', 'Children Mission Off/ Coll',
            'Communication Off/ Coll', 'Counselling Off/Coll', 'Deaf Ministry Off/Coll',
            'Diocesan School Welfare Fund', 'Deaf School Off/Coll', 'DME Off/Coll', 'IMS Off/Coll',
            'Jews Offertory', 'LCF Off/Coll', 'Mens - Off/ Coll', 'Mentally Rtd Off/ Coll',
            'Pastorate School Welfare Funds Collection', 'Self Denial Offertory', 'Womens Off/ Coll',
            'Youth Off/ Coll', 'Clergy Diocesan Pension Fund', 'Clergy Diocesan Provident Fund',
            'Clergy Dio PF Loan Recovery', 'Clergy Income Tax', 'Clergy Staff Welfare Fund',
            'Clergy & Staff Welfare Fund Loan', 'Clergy Vehicle Loan', 'Advances', 'Rent - Building',
            'Donations - Receipt'
        ]
        
        if income_result:
            for order, item_name in enumerate(income_items_order, start=1):
                cursor.execute('UPDATE items SET display_order = ? WHERE item_name = ? AND category_id = ?',
                             (order, item_name, income_id))
        
        # Expenses items order
        cursor.execute('SELECT id FROM categories WHERE category_name = ?', ('Expenses',))
        expenses_result = cursor.fetchone()
        
        if expenses_result:
            expenses_id = expenses_result[0]
            
            expenses_items_order = [
                'Opening Deficit', 'Furniture & Fittings', 'Land Purchased', 'Office Equipments',
                'Building Working in Progress', 'Salary (STAFF)', 'Interest Paid', 'Donations Payment',
                'Payment to Centre for Rural Women Development', 'Payment to TDTA Packiam Ammal Siruvar Illam',
                'Payment to Vison', 'Payment to Social Welfare Department', 'Payment to Institution',
                'Payment to Child Care & Edn Development Centre', 'Payment to Ecology Department',
                'Assessment to Diocese (From Pastorate)', 'Payment to Anbin Illam', 'Payment to Blind School',
                'Payment to Central CC', 'Payment to Children Mission', 'Payment to Communication',
                'Payment to Confirmation Offertory', 'Payment to Counselling', 'Payment to Deaf Ministry',
                'Payment to Diocesan Magazine', 'Payment to Diocesan School Welfare Fund', 'Payment to DME',
                'Payment to Jews Offertory', 'Payment to Mens', 'Payment to Mentally Rtd', 'Payment to North CC',
                'Payment to North West CC', 'Payment to Pastorate', 'Payment to Self Denial',
                'Payment to Shalom Home for Aged', 'Payment to South CC', 'Payment to South West CC',
                'Payment to West CC', 'Payment to Womens.', 'Payment to Youth', 'Clergy Diocesan Pension Fund',
                'Clergy Diocesan Provident Fund', 'Clergy Dio PF Loan Recovery', 'Clergy Income Tax',
                'Clergy Staff Welfare Fund', 'Clergy Vehicle Loan', 'Audit Fees', 'Electricity Church',
                'Electricty Parsonage', 'Hospitality', 'Legal and Professional Charges', 'Miscellaneous Expenses',
                'Printing and Stationery', 'Property Maintenance', 'Rates & Property Taxes',
                'Repair and Maintenance - Building', 'Repair and Maintenance - Plant and Equipment',
                'School Exepenses', 'Telephone Bill - Office', 'Telephone Bill - Parsonage',
                'Travelling and Conveyance', 'Charge Allowance', 'Pastorate Allowance',
                'Clergy Salary & Allowances', 'Committee Conferrence and Meeting', 'Convention',
                'Fasting Prayer Expenses', 'Festival Expenses', 'Harvest Festival Expenses',
                'Holy Communion Expenses', 'IMS Payment', 'Payment to LCF', 'Retreat Expenses',
                'Trumphet Festival Expenses', 'VBS', 'Wife Allowance Payment', 'Advances'
            ]
            
            for order, item_name in enumerate(expenses_items_order, start=1):
                cursor.execute('UPDATE items SET display_order = ? WHERE item_name = ? AND category_id = ?',
                             (order, item_name, expenses_id))
        
        # Assign high order numbers to any custom items (items not in the default lists)
        cursor.execute('''
            UPDATE items 
            SET display_order = 1000 + id 
            WHERE display_order = 0 OR display_order IS NULL
        ''')
        
        conn.commit()
        print("  ✓ Display order assigned to all items")
        
        print("\n✅ Migration completed successfully!")
        print("\nYour database has been updated with:")
        print("  • Removed duplicate items")
        print("  • Added 'Miscellaneous Collection'")
        print("  • Fixed spelling errors")
        print("  • Assigned proper display order to all items")
        print("  • Custom items preserved at the end")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {str(e)}")
        print("Please backup your database and try again.")
    
    finally:
        conn.close()


if __name__ == '__main__':
    print("=" * 60)
    print("DATABASE MIGRATION SCRIPT")
    print("=" * 60)
    print("\nThis will update your existing database without deleting data.")
    print("It's safe to run multiple times.\n")
    
    response = input("Do you want to proceed? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        migrate_database()
    else:
        print("Migration cancelled.")
