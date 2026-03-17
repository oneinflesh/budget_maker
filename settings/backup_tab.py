from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QComboBox, QMessageBox, QFileDialog, QTextEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database.category_service import CategoryService
from config import Config
import csv
from datetime import datetime
from pathlib import Path


class BackupTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.service = CategoryService(db_manager)
        self.init_ui()
    
    def refresh_pastorates(self):
        """Refresh the pastorate dropdown"""
        current_selection = self.pastorate_combo.currentData()
        self.pastorate_combo.clear()
        self.pastorate_combo.addItem('All Pastorates', None)
        self.load_pastorates()
        
        # Try to restore previous selection
        if current_selection is not None:
            index = self.pastorate_combo.findData(current_selection)
            if index >= 0:
                self.pastorate_combo.setCurrentIndex(index)
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel('Backup Budget Data')
        title.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_HEADING, QFont.Bold))
        layout.addWidget(title)
        
        # Description
        desc = QLabel('Export budget entries to CSV file. You can export all entries or filter by pastorate.')
        desc.setWordWrap(True)
        desc.setStyleSheet('color: #666; padding: 10px 0;')
        layout.addWidget(desc)
        
        # Filter section
        filter_layout = QHBoxLayout()
        
        filter_label = QLabel('Filter by Pastorate:')
        filter_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL))
        filter_layout.addWidget(filter_label)
        
        self.pastorate_combo = QComboBox()
        self.pastorate_combo.addItem('All Pastorates', None)
        self.load_pastorates()
        filter_layout.addWidget(self.pastorate_combo, 1)
        
        layout.addLayout(filter_layout)
        
        # Backup button
        backup_btn = QPushButton('Export to CSV')
        backup_btn.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 15px 30px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        ''')
        backup_btn.clicked.connect(self.export_backup)
        layout.addWidget(backup_btn)
        
        # Log area
        log_label = QLabel('Export Log:')
        log_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet('background-color: #f5f5f5; border: 1px solid #ccc; padding: 10px;')
        layout.addWidget(self.log_text)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def load_pastorates(self):
        """Load pastorates into combo box"""
        pastorates = self.service.get_all_pastorates()
        for pastorate_id, pastorate_name in pastorates:
            self.pastorate_combo.addItem(pastorate_name, pastorate_id)
    
    def export_backup(self):
        """Export budget data to CSV"""
        try:
            # Get selected pastorate filter
            pastorate_id = self.pastorate_combo.currentData()
            
            # Ask user where to save
            timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
            default_filename = f'budget_backup_{timestamp}.csv'
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                'Save Backup File',
                default_filename,
                'CSV Files (*.csv)'
            )
            
            if not file_path:
                return
            
            self.log_text.clear()
            self.log_text.append(f'Starting backup at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}...\n')
            
            # Get budget data
            budget_data = self.get_budget_data(pastorate_id)
            
            if not budget_data:
                self.log_text.append('No data to export!')
                QMessageBox.warning(self, 'No Data', 'No budget entries found to export.')
                return
            
            # Write to CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Pastorate_name', 'Year', 'Data_type', 'Category_name', 'Item_name', 'Amount'])
                
                # Write data
                for row in budget_data:
                    writer.writerow(row)
            
            self.log_text.append(f'Exported {len(budget_data)} entries successfully!')
            self.log_text.append(f'File saved to: {file_path}')
            
            QMessageBox.information(self, 'Success', 
                                   f'Backup completed successfully!\n\n{len(budget_data)} entries exported to:\n{file_path}')
            
        except Exception as e:
            self.log_text.append(f'\nERROR: {str(e)}')
            QMessageBox.critical(self, 'Error', f'Backup failed: {str(e)}')
    
    def get_budget_data(self, pastorate_id=None):
        """Get budget data with all names (not IDs)"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT 
                    p.name as pastorate_name,
                    y.year,
                    dt.type_name as data_type,
                    c.category_name,
                    i.item_name,
                    b.amount
                FROM budget b
                JOIN pastorates p ON b.pastorate_id = p.id
                JOIN years y ON b.year_id = y.id
                JOIN data_types dt ON b.data_type_id = dt.id
                JOIN categories c ON b.category_id = c.id
                JOIN items i ON b.item_id = i.id
            '''
            
            if pastorate_id:
                query += ' WHERE b.pastorate_id = ?'
                cursor.execute(query + ' ORDER BY p.name, y.year, dt.type_name, c.category_name, i.display_order', 
                             (pastorate_id,))
            else:
                cursor.execute(query + ' ORDER BY p.name, y.year, dt.type_name, c.category_name, i.display_order')
            
            return cursor.fetchall()
