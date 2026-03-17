from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QStackedWidget)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from database.category_service import CategoryService
from entries.create_entry_dialog import CreateEntryDialog
from config import Config


class EntryTab(QWidget):
    def __init__(self, db_manager, data_type_id, data_type_name):
        super().__init__()
        self.db = db_manager
        self.service = CategoryService(db_manager)
        self.data_type_id = data_type_id
        self.data_type_name = data_type_name
        self.init_ui()
        self.load_entries()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Stacked widget to switch between list and entry page
        self.stacked_widget = QStackedWidget()
        
        # List page
        self.list_page = self.create_list_page()
        self.stacked_widget.addWidget(self.list_page)
        
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
    
    def create_list_page(self):
        """Create the list view page"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header with title and create button
        header_layout = QHBoxLayout()
        
        title = QLabel(f'{self.data_type_name} Entries')
        title.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_HEADING, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        create_btn = QPushButton('Create New Entry')
        create_btn.setStyleSheet('background-color: #4CAF50; color: white; font-weight: bold; padding: 10px 20px;')
        create_btn.clicked.connect(self.show_create_dialog)
        header_layout.addWidget(create_btn)
        
        layout.addLayout(header_layout)
        
        # Table to show existing entries
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['ID', 'Year', 'Pastorate', 'Created Date', 'View/Edit', 'Delete'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        layout.addWidget(self.table)
        
        widget.setLayout(layout)
        return widget
    
    def load_entries(self):
        """Load entries for this data type"""
        self.table.setRowCount(0)
        
        entries = self.service.get_budget_entries_by_data_type(self.data_type_id)
        
        if not entries:
            self.table.insertRow(0)
            no_data_item = QTableWidgetItem('No entries yet. Click "Create New Entry" to add one.')
            no_data_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, no_data_item)
            self.table.setSpan(0, 0, 1, 6)
        else:
            for row_idx, (year_id, pastorate_id, year, pastorate, created_at) in enumerate(entries):
                self.table.insertRow(row_idx)
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
                self.table.setItem(row_idx, 1, QTableWidgetItem(year))
                self.table.setItem(row_idx, 2, QTableWidgetItem(pastorate))
                self.table.setItem(row_idx, 3, QTableWidgetItem(created_at))
                
                # View/Edit button
                view_btn = QPushButton('View/Edit')
                view_btn.setStyleSheet('background-color: #2196F3; color: white; padding: 5px;')
                view_btn.clicked.connect(lambda checked, y=year_id, p=pastorate_id: self.view_entry(y, p))
                self.table.setCellWidget(row_idx, 4, view_btn)
                
                # Delete button
                delete_btn = QPushButton('Delete')
                delete_btn.setStyleSheet('background-color: #f44336; color: white; padding: 5px;')
                delete_btn.clicked.connect(lambda checked, y=year_id, p=pastorate_id, yr=year, pt=pastorate: self.delete_entry(y, p, yr, pt))
                self.table.setCellWidget(row_idx, 5, delete_btn)
    
    def show_create_dialog(self):
        """Show dialog to select Year and Pastorate"""
        dialog = CreateEntryDialog(self.db, self.data_type_name, self)
        if dialog.exec():
            year_id = dialog.selected_year_id
            pastorate_id = dialog.selected_pastorate_id
            
            # Open entry page in same window
            from entries.budget_entry_page import BudgetEntryPage
            
            entry_page = BudgetEntryPage(self.db, year_id, pastorate_id, 
                                        self.data_type_id, self.data_type_name)
            entry_page.back_to_list.connect(self.back_to_list)
            
            self.stacked_widget.addWidget(entry_page)
            self.stacked_widget.setCurrentWidget(entry_page)
    
    def back_to_list(self):
        """Return to list page"""
        self.stacked_widget.setCurrentIndex(0)
        # Remove entry page from stack
        if self.stacked_widget.count() > 1:
            widget = self.stacked_widget.widget(1)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        # Refresh list
        self.load_entries()
    
    def view_entry(self, year_id, pastorate_id):
        """View/Edit existing entry"""
        from entries.budget_entry_page import BudgetEntryPage
        
        entry_page = BudgetEntryPage(self.db, year_id, pastorate_id, 
                                    self.data_type_id, self.data_type_name)
        entry_page.back_to_list.connect(self.back_to_list)
        
        self.stacked_widget.addWidget(entry_page)
        self.stacked_widget.setCurrentWidget(entry_page)
    
    def delete_entry(self, year_id, pastorate_id, year, pastorate):
        """Delete an entry"""
        reply = QMessageBox.question(self, 'Confirm Delete', 
                                     f'Are you sure you want to delete the entry for:\n{year} - {pastorate}?',
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.service.delete_budget_entries(year_id, pastorate_id, self.data_type_id)
                QMessageBox.information(self, 'Success', 'Entry deleted successfully!')
                self.load_entries()
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to delete: {str(e)}')
