from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QLabel)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from database.category_service import CategoryService
from config import Config


class YearTab(QWidget):
    year_changed = Signal()  # Signal when years are added/updated/deleted
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.service = CategoryService(db_manager)
        self.selected_id = None
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel('Manage Financial Years')
        title.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_HEADING, QFont.Bold))
        layout.addWidget(title)
        
        # Input section
        input_layout = QHBoxLayout()
        
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText('Enter financial year (e.g., 2024-2025)')
        input_layout.addWidget(self.year_input)
        
        self.add_btn = QPushButton('Add')
        self.add_btn.clicked.connect(self.add_item)
        input_layout.addWidget(self.add_btn)
        
        self.update_btn = QPushButton('Update')
        self.update_btn.clicked.connect(self.update_item)
        self.update_btn.setEnabled(False)
        input_layout.addWidget(self.update_btn)
        
        self.clear_btn = QPushButton('Clear')
        self.clear_btn.clicked.connect(self.clear_selection)
        input_layout.addWidget(self.clear_btn)
        
        layout.addLayout(input_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['ID', 'Financial Year'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 400)
        layout.addWidget(self.table)
        
        # Delete button
        delete_btn = QPushButton('Delete Selected')
        delete_btn.clicked.connect(self.delete_item)
        layout.addWidget(delete_btn)
        
        self.setLayout(layout)
    
    def load_data(self):
        self.table.setRowCount(0)
        data = self.service.get_all_years()
        
        for row_idx, (year_id, year) in enumerate(data):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(year_id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(year)))
    
    def add_item(self):
        year = self.year_input.text().strip()
        
        if not year:
            QMessageBox.warning(self, 'Error', 'Please enter a financial year')
            return
        
        # Validate format (YYYY-YYYY)
        if '-' not in year or len(year.split('-')) != 2:
            QMessageBox.warning(self, 'Error', 'Please use format: YYYY-YYYY (e.g., 2024-2025)')
            return
        
        try:
            self.service.add_year(year)
            self.year_input.clear()
            self.load_data()
            self.year_changed.emit()  # Emit signal
            QMessageBox.information(self, 'Success', 'Financial year added successfully')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to add: {str(e)}')
    
    def update_item(self):
        if not self.selected_id:
            return
        
        year = self.year_input.text().strip()
        
        if not year:
            QMessageBox.warning(self, 'Error', 'Please enter a financial year')
            return
        
        if '-' not in year or len(year.split('-')) != 2:
            QMessageBox.warning(self, 'Error', 'Please use format: YYYY-YYYY (e.g., 2024-2025)')
            return
        
        try:
            self.service.update_year(self.selected_id, year)
            self.clear_selection()
            self.load_data()
            self.year_changed.emit()  # Emit signal
            QMessageBox.information(self, 'Success', 'Financial year updated successfully')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to update: {str(e)}')
    
    def delete_item(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, 'Error', 'Please select a year to delete')
            return
        
        year_id = int(self.table.item(self.table.currentRow(), 0).text())
        year = self.table.item(self.table.currentRow(), 1).text()
        
        reply = QMessageBox.question(self, 'Confirm Delete', 
                                     f'Are you sure you want to delete year "{year}"?',
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.service.delete_year(year_id)
                self.clear_selection()
                self.load_data()
                self.year_changed.emit()  # Emit signal
                QMessageBox.information(self, 'Success', 'Financial year deleted successfully')
            except ValueError as e:
                QMessageBox.warning(self, 'Error', str(e))
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to delete: {str(e)}')
    
    def on_selection_changed(self):
        selected_rows = self.table.selectedItems()
        if selected_rows:
            row = self.table.currentRow()
            self.selected_id = int(self.table.item(row, 0).text())
            self.year_input.setText(self.table.item(row, 1).text())
            self.add_btn.setEnabled(False)
            self.update_btn.setEnabled(True)
        else:
            self.clear_selection()
    
    def clear_selection(self):
        self.selected_id = None
        self.year_input.clear()
        self.table.clearSelection()
        self.add_btn.setEnabled(True)
        self.update_btn.setEnabled(False)
