"""
Budget Data Types Migration Script
Renames Budget data types and migrates existing entries
"""
import sqlite3
from pathlib import Path


def migrate_budget_types():
    db_path = Path(__file__).parent / 'database' / 'app.db'
    
    if not db_path.exists():
        print("Database not found. No migration needed.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Starting budget types migration...")
    print("=" * 60)
    
    try:
        # Step 1: Check current data types
        print("\nStep 1: Checking current data types...")
        cursor.execute('SELECT id, type_name FROM data_types ORDER BY type_name')
        current_types = cursor.fetchall()
        
        print("Current data types:")
        for dt_id, dt_name in current_types:
            print(f"  ID {dt_id}: {dt_name}")
        
        # Step 2: Check which years have budget entries
        print("\nStep 2: Checking budget entries by year...")
        cursor.execute('''
            SELECT DISTINCT y.year, dt.type_name, COUNT(*) as entry_count
            FROM budget b
            JOIN years y ON b.year_id = y.id
            JOIN data_types dt ON b.data_type_id = dt.id
            WHERE dt.type_name = 'Budget'
            GROUP BY y.year, dt.type_name
            ORDER BY y.year
        ''')
        budget_entries = cursor.fetchall()
        
        if budget_entries:
            print("Found Budget entries for years:")
            for year, dtype, count in budget_entries:
                print(f"  {year}: {count} entries")
        else:
            print("No Budget entries found.")
        
        # Step 3: Get year IDs for 2025-2026 and 2026-2027
        cursor.execute('SELECT id FROM years WHERE year = ?', ('2025-2026',))
        year_2025_result = cursor.fetchone()
        year_2025_id = year_2025_result[0] if year_2025_result else None
        
        cursor.execute('SELECT id FROM years WHERE year = ?', ('2026-2027',))
        year_2026_result = cursor.fetchone()
        year_2026_id = year_2026_result[0] if year_2026_result else None
        
        # Step 4: Get Budget data type ID
        cursor.execute('SELECT id FROM data_types WHERE type_name = ?', ('Budget',))
        budget_type_result = cursor.fetchone()
        budget_type_id = budget_type_result[0] if budget_type_result else None
        
        if not budget_type_id:
            print("\n⚠ 'Budget' data type not found. Creating new data types...")
        
        # Step 5: Create new data types if they don't exist
        print("\nStep 3: Creating new data types...")
        
        # Check and create R-Budget (Revised Budget)
        cursor.execute('SELECT id FROM data_types WHERE type_name = ?', ('R-Budget',))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO data_types (type_name) VALUES (?)', ('R-Budget',))
            print("  ✓ Created 'R-Budget' data type")
        else:
            print("  ✓ 'R-Budget' already exists")
        
        # Check and create T-Budget (Tentative Budget)
        cursor.execute('SELECT id FROM data_types WHERE type_name = ?', ('T-Budget',))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO data_types (type_name) VALUES (?)', ('T-Budget',))
            print("  ✓ Created 'T-Budget' data type")
        else:
            print("  ✓ 'T-Budget' already exists")
        
        conn.commit()
        
        # Get new data type IDs
        cursor.execute('SELECT id FROM data_types WHERE type_name = ?', ('R-Budget',))
        r_budget_id = cursor.fetchone()[0]
        
        cursor.execute('SELECT id FROM data_types WHERE type_name = ?', ('T-Budget',))
        t_budget_id = cursor.fetchone()[0]
        
        # Step 6: Migrate existing Budget entries
        print("\nStep 4: Migrating existing Budget entries...")
        
        migrated_count = 0
        
        # Migrate 2025-2026 Budget → R-Budget
        if year_2025_id and budget_type_id:
            cursor.execute('''
                SELECT COUNT(*) FROM budget 
                WHERE year_id = ? AND data_type_id = ?
            ''', (year_2025_id, budget_type_id))
            count_2025 = cursor.fetchone()[0]
            
            if count_2025 > 0:
                cursor.execute('''
                    UPDATE budget 
                    SET data_type_id = ? 
                    WHERE year_id = ? AND data_type_id = ?
                ''', (r_budget_id, year_2025_id, budget_type_id))
                print(f"  ✓ Migrated {count_2025} entries: 2025-2026 Budget → R-Budget")
                migrated_count += count_2025
        
        # Migrate 2026-2027 Budget → T-Budget
        if year_2026_id and budget_type_id:
            cursor.execute('''
                SELECT COUNT(*) FROM budget 
                WHERE year_id = ? AND data_type_id = ?
            ''', (year_2026_id, budget_type_id))
            count_2026 = cursor.fetchone()[0]
            
            if count_2026 > 0:
                cursor.execute('''
                    UPDATE budget 
                    SET data_type_id = ? 
                    WHERE year_id = ? AND data_type_id = ?
                ''', (t_budget_id, year_2026_id, budget_type_id))
                print(f"  ✓ Migrated {count_2026} entries: 2026-2027 Budget → T-Budget")
                migrated_count += count_2026
        
        if migrated_count == 0:
            print("  ℹ No Budget entries found to migrate")
        
        conn.commit()
        
        # Step 7: Verify migration
        print("\nStep 5: Verifying migration...")
        cursor.execute('''
            SELECT dt.type_name, COUNT(*) as entry_count
            FROM budget b
            JOIN data_types dt ON b.data_type_id = dt.id
            GROUP BY dt.type_name
            ORDER BY dt.type_name
        ''')
        final_counts = cursor.fetchall()
        
        print("Final budget entry counts by data type:")
        for dtype, count in final_counts:
            print(f"  {dtype}: {count} entries")
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("\nSummary:")
        print("  • Created 'R-Budget' and 'T-Budget' data types")
        print(f"  • Migrated {migrated_count} budget entries")
        print("  • 2025-2026 Budget → R-Budget")
        print("  • 2026-2027 Budget → T-Budget")
        print("\nNew data types:")
        print("  • Actual - For actual amounts")
        print("  • Actual Estimate - For estimated actual amounts")
        print("  • R-Budget - For revised budget (previous year)")
        print("  • T-Budget - For tentative budget (current year)")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {str(e)}")
        print("Database has been rolled back to previous state.")
    
    finally:
        conn.close()


if __name__ == '__main__':
    print("=" * 60)
    print("BUDGET DATA TYPES MIGRATION SCRIPT")
    print("=" * 60)
    print("\nThis will:")
    print("  1. Create 'R-Budget' and 'T-Budget' data types")
    print("  2. Migrate 2025-2026 Budget entries → R-Budget")
    print("  3. Migrate 2026-2027 Budget entries → T-Budget")
    print("\nYour data will be preserved.\n")
    
    response = input("Do you want to proceed? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        migrate_budget_types()
    else:
        print("Migration cancelled.")
