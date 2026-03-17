from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QMessageBox, QFileDialog, QTextEdit)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from database.category_service import CategoryService
from config import Config
import csv
from datetime import datetime


class RestoreTab(QWidget):
    data_imported = Signal()  # Signal to notify when data is imported
    pastorates_changed = Signal()  # Signal when new pastorates are created
    years_changed = Signal()  # Signal when new years are created
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.service = CategoryService(db_manager)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel('Restore Budget Data')
        title.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_HEADING, QFont.Bold))
        layout.addWidget(title)
        
        # Description
        desc = QLabel(
            'Import budget entries from CSV file.\n\n'
            'CSV Format: Pastorate_name, Year, Data_type, Category_name, Item_name, Amount\n\n'
            'Notes:\n'
            '• New pastorates and years will be created automatically\n'
            '• Categories, Data types, and Items must match existing defaults\n'
            '• Existing entries will be updated with new amounts'
        )
        desc.setWordWrap(True)
        desc.setStyleSheet('color: #666; padding: 10px; background-color: #f9f9f9; border-left: 3px solid #4CAF50;')
        layout.addWidget(desc)
        
        # Restore button
        restore_btn = QPushButton('Import from CSV')
        restore_btn.setStyleSheet('''
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 15px 30px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        ''')
        restore_btn.clicked.connect(self.import_restore)
        layout.addWidget(restore_btn)
        
        # Log area
        log_label = QLabel('Import Log:')
        log_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(300)
        self.log_text.setStyleSheet('background-color: #f5f5f5; border: 1px solid #ccc; padding: 10px;')
        layout.addWidget(self.log_text)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def import_restore(self):
        """Import budget data from CSV"""
        try:
            # Ask user to select file
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                'Select Backup File',
                '',
                'CSV Files (*.csv)'
            )
            
            if not file_path:
                return
            
            self.log_text.clear()
            self.log_text.append(f'Starting import at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}...\n')
            
            # Read and validate CSV
            errors = []
            valid_rows = []
            
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        # Validate required fields
                        if not all(key in row for key in ['Pastorate_name', 'Year', 'Data_type', 'Category_name', 'Item_name', 'Amount']):
                            errors.append(f'Row {row_num}: Missing required columns')
                            continue
                        
                        pastorate_name = row['Pastorate_name'].strip()
                        year = row['Year'].strip()
                        data_type = row['Data_type'].strip()
                        category_name = row['Category_name'].strip()
                        item_name = row['Item_name'].strip()
                        amount_str = row['Amount'].strip()
                        
                        # Validate amount
                        try:
                            amount = float(amount_str)
                        except ValueError:
                            errors.append(f'Row {row_num}: Invalid amount "{amount_str}"')
                            continue
                        
                        # Validate category, data_type, item exist
                        validation_error = self.validate_row(data_type, category_name, item_name)
                        if validation_error:
                            errors.append(f'Row {row_num}: {validation_error}')
                            continue
                        
                        valid_rows.append({
                            'pastorate_name': pastorate_name,
                            'year': year,
                            'data_type': data_type,
                            'category_name': category_name,
                            'item_name': item_name,
                            'amount': amount
                        })
                        
                    except Exception as e:
                        errors.append(f'Row {row_num}: {str(e)}')
            
            # Show validation report
            self.log_text.append(f'Validation complete:')
            self.log_text.append(f'  Valid rows: {len(valid_rows)}')
            self.log_text.append(f'  Errors: {len(errors)}\n')
            
            if errors:
                self.log_text.append('ERRORS FOUND:')
                for error in errors[:20]:  # Show first 20 errors
                    self.log_text.append(f'  • {error}')
                if len(errors) > 20:
                    self.log_text.append(f'  ... and {len(errors) - 20} more errors')
                self.log_text.append('')
            
            if not valid_rows:
                QMessageBox.warning(self, 'No Valid Data', 'No valid rows found to import.')
                return
            
            # Ask for confirmation
            reply = QMessageBox.question(
                self,
                'Confirm Import',
                f'Found {len(valid_rows)} valid entries to import.\n'
                f'{len(errors)} rows have errors and will be skipped.\n\n'
                'Existing entries will be updated. Continue?',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                self.log_text.append('Import cancelled by user.')
                return
            
            # Import data
            self.log_text.append('Starting import...\n')
            imported_count = self.import_data(valid_rows)
            
            self.log_text.append(f'\nImport completed successfully!')
            self.log_text.append(f'Imported {imported_count} entries.')
            
            # Emit signal to refresh entries
            self.data_imported.emit()
            
            QMessageBox.information(self, 'Success', 
                                   f'Import completed!\n\n'
                                   f'Imported: {imported_count} entries\n'
                                   f'Errors: {len(errors)} rows skipped')
            
        except Exception as e:
            self.log_text.append(f'\nERROR: {str(e)}')
            QMessageBox.critical(self, 'Error', f'Import failed: {str(e)}')
    
    def validate_row(self, data_type, category_name, item_name):
        """Validate that data_type, category, and item exist"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check data_type
            cursor.execute('SELECT id FROM data_types WHERE type_name = ?', (data_type,))
            if not cursor.fetchone():
                return f'Data type "{data_type}" not found in system'
            
            # Check category
            cursor.execute('SELECT id FROM categories WHERE category_name = ?', (category_name,))
            category_result = cursor.fetchone()
            if not category_result:
                return f'Category "{category_name}" not found in system'
            
            category_id = category_result[0]
            
            # Check item exists in that category
            cursor.execute('SELECT id FROM items WHERE item_name = ? AND category_id = ?', 
                         (item_name, category_id))
            if not cursor.fetchone():
                return f'Item "{item_name}" not found in category "{category_name}"'
            
            return None
    
    def import_data(self, rows):
        """Import validated data into database"""
        imported_count = 0
        new_pastorates = False
        new_years = False
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            for row in rows:
                try:
                    # Get or create pastorate
                    cursor.execute('SELECT id FROM pastorates WHERE name = ?', (row['pastorate_name'],))
                    pastorate_result = cursor.fetchone()
                    if pastorate_result:
                        pastorate_id = pastorate_result[0]
                    else:
                        cursor.execute('INSERT INTO pastorates (name) VALUES (?)', (row['pastorate_name'],))
                        pastorate_id = cursor.lastrowid
                        self.log_text.append(f'  Created new pastorate: {row["pastorate_name"]}')
                        new_pastorates = True
                    
                    # Get or create year
                    cursor.execute('SELECT id FROM years WHERE year = ?', (row['year'],))
                    year_result = cursor.fetchone()
                    if year_result:
                        year_id = year_result[0]
                    else:
                        cursor.execute('INSERT INTO years (year) VALUES (?)', (row['year'],))
                        year_id = cursor.lastrowid
                        self.log_text.append(f'  Created new year: {row["year"]}')
                        new_years = True
                    
                    # Get IDs for data_type, category, item
                    cursor.execute('SELECT id FROM data_types WHERE type_name = ?', (row['data_type'],))
                    data_type_id = cursor.fetchone()[0]
                    
                    cursor.execute('SELECT id FROM categories WHERE category_name = ?', (row['category_name'],))
                    category_id = cursor.fetchone()[0]
                    
                    cursor.execute('SELECT id FROM items WHERE item_name = ? AND category_id = ?', 
                                 (row['item_name'], category_id))
                    item_id = cursor.fetchone()[0]
                    
                    # Check if entry exists
                    cursor.execute('''
                        SELECT id FROM budget 
                        WHERE pastorate_id = ? AND year_id = ? AND data_type_id = ? 
                        AND category_id = ? AND item_id = ?
                    ''', (pastorate_id, year_id, data_type_id, category_id, item_id))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Update existing entry
                        cursor.execute('''
                            UPDATE budget SET amount = ? 
                            WHERE id = ?
                        ''', (row['amount'], existing[0]))
                    else:
                        # Insert new entry
                        cursor.execute('''
                            INSERT INTO budget (pastorate_id, year_id, data_type_id, category_id, item_id, amount)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (pastorate_id, year_id, data_type_id, category_id, item_id, row['amount']))
                    
                    imported_count += 1
                    
                except Exception as e:
                    self.log_text.append(f'  Error importing row: {str(e)}')
        
        # Emit signals if new data was created
        if new_pastorates:
            self.pastorates_changed.emit()
        if new_years:
            self.years_changed.emit()
        
        return imported_count
