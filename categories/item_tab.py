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
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', 'Order', 'Item Name', 'Category'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemChanged.connect(self.on_item_changed)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 60)
        self.table.setColumnWidth(2, 250)
        self.table.setColumnWidth(3, 150)
        
        # Allow clicking on empty space to deselect
        self.table.viewport().installEventFilter(self)
        
        layout.addWidget(self.table)
        
        # Delete button
        delete_btn = QPushButton('Delete Selected')
        delete_btn.clicked.connect(self.delete_item)
        layout.addWidget(delete_btn)
        
        # Info label
        info_label = QLabel('Tip: Double-click the Order column to change item position. Items are numbered separately for each category.')
        info_label.setStyleSheet('color: #666; font-style: italic; padding: 5px;')
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        self.setLayout(layout)
    
    def load_categories(self):
        self.category_combo.clear()
        categories = self.service.get_all_categories()
        for cat_id, cat_name in categories:
            self.category_combo.addItem(cat_name, cat_id)
    
    def load_data(self):
        # Disconnect itemChanged signal temporarily to avoid triggering during load
        self.table.itemChanged.disconnect(self.on_item_changed)
        
        self.table.setRowCount(0)
        data = self.service.get_all_items()
        
        for row_idx, (item_id, item_name, category_id, category_name) in enumerate(data):
            self.table.insertRow(row_idx)
            
            # ID column with category_id stored in UserRole
            id_item = QTableWidgetItem(str(item_id))
            id_item.setData(Qt.UserRole, category_id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)  # Not editable
            self.table.setItem(row_idx, 0, id_item)
            
            # Order column - editable
            order_item = QTableWidgetItem(str(row_idx + 1))  # Display relative order
            order_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 1, order_item)
            
            # Item name column - not editable in table
            name_item = QTableWidgetItem(item_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 2, name_item)
            
            # Category name column - not editable
            cat_item = QTableWidgetItem(category_name)
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 3, cat_item)
        
        # Reconnect itemChanged signal
        self.table.itemChanged.connect(self.on_item_changed)
    
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
        name = self.table.item(row, 2).text()
        
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
            self.name_input.setText(self.table.item(row, 2).text())
            
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
    
    def on_item_changed(self, item):
        """Handle when order number is changed"""
        if item.column() != 1:  # Only handle Order column
            return
        
        try:
            new_order = int(item.text())
            if new_order < 1:
                raise ValueError("Order must be positive")
            
            row = item.row()
            item_id = int(self.table.item(row, 0).text())
            category_id = self.table.item(row, 0).data(Qt.UserRole)
            
            # Get all items in the same category
            all_items = self.service.get_all_items()
            category_items = [(iid, iname, cid, cname) for iid, iname, cid, cname in all_items if cid == category_id]
            
            # Validate new order is within range
            if new_order > len(category_items):
                new_order = len(category_items)
                item.setText(str(new_order))
            
            # Reorder items in this category
            self.service.reorder_item(item_id, category_id, new_order)
            
            # Reload to show new order
            self.load_data()
            
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Please enter a valid number for order')
            self.load_data()  # Reload to reset invalid value
    
    def eventFilter(self, obj, event):
        """Handle clicks on empty table area to deselect"""
        if obj == self.table.viewport() and event.type() == QEvent.MouseButtonPress:
            index = self.table.indexAt(event.pos())
            if not index.isValid():
                self.table.clearSelection()
                self.clear_selection()
        return super().eventFilter(obj, event)
