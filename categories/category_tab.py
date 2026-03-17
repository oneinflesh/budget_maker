from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QLabel)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from database.category_service import CategoryService
from config import Config


class CategoryTab(QWidget):
    category_changed = Signal()
    
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
        
        title = QLabel('Manage Categories')
        title.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_HEADING, QFont.Bold))
        layout.addWidget(title)
        
        # Input section
        input_layout = QHBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Enter category name')
        input_layout.addWidget(self.name_input)
        
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
        self.table.setHorizontalHeaderLabels(['ID', 'Category Name'])
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
        data = self.service.get_all_categories()
        
        for row_idx, (category_id, name) in enumerate(data):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(category_id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(name))
    
    def add_item(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, 'Error', 'Please enter a category name')
            return
        
        try:
            self.service.add_category(name)
            self.name_input.clear()
            self.load_data()
            self.category_changed.emit()
            QMessageBox.information(self, 'Success', 'Category added successfully')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to add: {str(e)}')
    
    def update_item(self):
        if not self.selected_id:
            return
        
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, 'Error', 'Please enter a category name')
            return
        
        try:
            self.service.update_category(self.selected_id, name)
            self.clear_selection()
            self.load_data()
            self.category_changed.emit()
            QMessageBox.information(self, 'Success', 'Category updated successfully')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to update: {str(e)}')
    
    def delete_item(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, 'Error', 'Please select a category to delete')
            return
        
        category_id = int(self.table.item(self.table.currentRow(), 0).text())
        name = self.table.item(self.table.currentRow(), 1).text()
        
        reply = QMessageBox.question(self, 'Confirm Delete', 
                                     f'Are you sure you want to delete "{name}"?',
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.service.delete_category(category_id)
                self.clear_selection()
                self.load_data()
                self.category_changed.emit()
                QMessageBox.information(self, 'Success', 'Category deleted successfully')
            except ValueError as e:
                QMessageBox.warning(self, 'Error', str(e))
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to delete: {str(e)}')
    
    def on_selection_changed(self):
        selected_rows = self.table.selectedItems()
        if selected_rows:
            row = self.table.currentRow()
            self.selected_id = int(self.table.item(row, 0).text())
            self.name_input.setText(self.table.item(row, 1).text())
            self.add_btn.setEnabled(False)
            self.update_btn.setEnabled(True)
        else:
            self.clear_selection()
    
    def clear_selection(self):
        self.selected_id = None
        self.name_input.clear()
        self.table.clearSelection()
        self.add_btn.setEnabled(True)
        self.update_btn.setEnabled(False)
