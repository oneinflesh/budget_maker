from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QLabel, QComboBox)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QFont
from database.category_service import CategoryService
from config import Config


class ItemTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.service = CategoryService(db_manager)
        self.selected_id = None
        self.init_ui()
        self.load_categories()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel('Manage Items')
        title.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_HEADING, QFont.Bold))
        layout.addWidget(title)
        
        # Input section
        input_layout = QHBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Enter item name')
        input_layout.addWidget(self.name_input)
        
        self.category_combo = QComboBox()
        input_layout.addWidget(self.category_combo)
        
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
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['ID', 'Item Name', 'Category'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(2, 250)
        
        # Allow clicking on empty space to deselect
        self.table.viewport().installEventFilter(self)
        
        layout.addWidget(self.table)
        
        # Delete button
        delete_btn = QPushButton('Delete Selected')
        delete_btn.clicked.connect(self.delete_item)
        layout.addWidget(delete_btn)
        
        # Reorder buttons
        reorder_layout = QHBoxLayout()
        reorder_layout.addStretch()
        
        move_up_btn = QPushButton('Move Up ↑')
        move_up_btn.clicked.connect(self.move_item_up)
        reorder_layout.addWidget(move_up_btn)
        
        move_down_btn = QPushButton('Move Down ↓')
        move_down_btn.clicked.connect(self.move_item_down)
        reorder_layout.addWidget(move_down_btn)
        
        layout.addLayout(reorder_layout)
        
        self.setLayout(layout)
    
    def load_categories(self):
        self.category_combo.clear()
        categories = self.service.get_all_categories()
        for cat_id, cat_name in categories:
            self.category_combo.addItem(cat_name, cat_id)
    
    def load_data(self):
        self.table.setRowCount(0)
        data = self.service.get_all_items()
        
        for row_idx, (item_id, item_name, category_id, category_name) in enumerate(data):
            self.table.insertRow(row_idx)
            
            # ID column with category_id stored in UserRole
            id_item = QTableWidgetItem(str(item_id))
            id_item.setData(Qt.UserRole, category_id)
            self.table.setItem(row_idx, 0, id_item)
            
            # Item name column
            self.table.setItem(row_idx, 1, QTableWidgetItem(item_name))
            
            # Category name column
            self.table.setItem(row_idx, 2, QTableWidgetItem(category_name))
    
    def refresh_data(self):
        self.load_categories()
        self.load_data()
    
    def add_item(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, 'Error', 'Please enter an item name')
            return
        
        if self.category_combo.count() == 0:
            QMessageBox.warning(self, 'Error', 'Please create a category first')
            return
        
        category_id = self.category_combo.currentData()
        
        try:
            self.service.add_item(name, category_id)
            self.name_input.clear()
            self.load_data()
            QMessageBox.information(self, 'Success', 'Item added successfully')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to add: {str(e)}')
    
    def update_item(self):
        if not self.selected_id:
            return
        
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, 'Error', 'Please enter an item name')
            return
        
        category_id = self.category_combo.currentData()
        
        try:
            self.service.update_item(self.selected_id, name, category_id)
            self.clear_selection()
            self.load_data()
            QMessageBox.information(self, 'Success', 'Item updated successfully')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to update: {str(e)}')
    
    def delete_item(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, 'Error', 'Please select an item to delete')
            return
        
        row = self.table.currentRow()
        item_id = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(self, 'Confirm Delete', 
                                     f'Are you sure you want to delete "{name}"?',
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.service.delete_item(item_id)
                self.clear_selection()
                self.load_data()
                QMessageBox.information(self, 'Success', 'Item deleted successfully')
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
            
            # Set category combo
            category_id = self.table.item(row, 0).data(Qt.UserRole)
            index = self.category_combo.findData(category_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            
            self.add_btn.setEnabled(False)
            self.update_btn.setEnabled(True)
        else:
            self.clear_selection()
    
    def clear_selection(self):
        self.selected_id = None
        self.name_input.clear()
        self.table.clearSelection()
        if self.category_combo.count() > 0:
            self.category_combo.setCurrentIndex(0)
        self.add_btn.setEnabled(True)
        self.update_btn.setEnabled(False)
    
    def move_item_up(self):
        """Move selected item up in display order"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, 'Error', 'Please select an item to move')
            return
        
        row = self.table.currentRow()
        if row == 0:
            QMessageBox.information(self, 'Info', 'Item is already at the top')
            return
        
        # Get current and previous item IDs
        current_item_id = int(self.table.item(row, 0).text())
        previous_item_id = int(self.table.item(row - 1, 0).text())
        
        try:
            self.service.swap_item_order(current_item_id, previous_item_id)
            self.load_data()
            # Reselect the moved item
            self.table.selectRow(row - 1)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to move: {str(e)}')
    
    def move_item_down(self):
        """Move selected item down in display order"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, 'Error', 'Please select an item to move')
            return
        
        row = self.table.currentRow()
        if row == self.table.rowCount() - 1:
            QMessageBox.information(self, 'Info', 'Item is already at the bottom')
            return
        
        # Get current and next item IDs
        current_item_id = int(self.table.item(row, 0).text())
        next_item_id = int(self.table.item(row + 1, 0).text())
        
        try:
            self.service.swap_item_order(current_item_id, next_item_id)
            self.load_data()
            # Reselect the moved item
            self.table.selectRow(row + 1)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to move: {str(e)}')
    
    def eventFilter(self, obj, event):
        """Handle clicks on empty table area to deselect"""
        if obj == self.table.viewport() and event.type() == QEvent.MouseButtonPress:
            index = self.table.indexAt(event.pos())
            if not index.isValid():
                self.table.clearSelection()
                self.clear_selection()
        return super().eventFilter(obj, event)
