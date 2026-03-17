from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QScrollArea, QGridLayout, QPushButton)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from database.category_service import CategoryService
from config import Config


class BudgetEntryPage(QWidget):
    back_to_list = Signal()
    
    def __init__(self, db_manager, year_id, pastorate_id, data_type_id, data_type_name):
        super().__init__()
        self.db = db_manager
        self.service = CategoryService(db_manager)
        self.year_id = year_id
        self.pastorate_id = pastorate_id
        self.data_type_id = data_type_id
        self.data_type_name = data_type_name
        
        self.income_inputs = {}
        self.expense_inputs = {}
        
        self.init_ui()
        self.load_items()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll area for entries
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_layout = QHBoxLayout()
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)
        
        # Income section (50% width)
        self.income_widget = self.create_income_section()
        scroll_layout.addWidget(self.income_widget, 1)
        
        # Expenses section (50% width)
        self.expense_widget = self.create_expense_section()
        scroll_layout.addWidget(self.expense_widget, 1)
        
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Summary bar (sticky at bottom)
        self.summary_bar = self.create_summary_bar()
        main_layout.addWidget(self.summary_bar)
        
        # Action buttons bar (sticky at bottom)
        self.action_bar = self.create_action_bar()
        main_layout.addWidget(self.action_bar)
        
        self.setLayout(main_layout)
    
    def create_income_section(self):
        """Create income section with 70% items, 30% amount"""
        widget = QWidget()
        widget.setStyleSheet("background-color: white; border-right: 2px solid #ccc;")
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)
        
        income_header = QLabel('INCOME')
        income_header.setFont(QFont(Config.FONT_FAMILY, 12, QFont.Bold))
        income_header.setStyleSheet("color: #4CAF50; padding: 5px;")
        header_layout.addWidget(income_header, 7)
        
        amount_header = QLabel('Amount')
        amount_header.setFont(QFont(Config.FONT_FAMILY, 12, QFont.Bold))
        amount_header.setAlignment(Qt.AlignCenter)
        amount_header.setStyleSheet("padding: 5px;")
        header_layout.addWidget(amount_header, 3)
        
        layout.addLayout(header_layout)
        
        # Items grid
        self.income_grid = QGridLayout()
        self.income_grid.setSpacing(5)
        self.income_grid.setColumnStretch(0, 7)  # 70% for items
        self.income_grid.setColumnStretch(1, 3)  # 30% for amount
        layout.addLayout(self.income_grid)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_expense_section(self):
        """Create expense section with 70% items, 30% amount"""
        widget = QWidget()
        widget.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)
        
        expense_header = QLabel('EXPENSES')
        expense_header.setFont(QFont(Config.FONT_FAMILY, 12, QFont.Bold))
        expense_header.setStyleSheet("color: #f44336; padding: 5px;")
        header_layout.addWidget(expense_header, 7)
        
        amount_header = QLabel('Amount')
        amount_header.setFont(QFont(Config.FONT_FAMILY, 12, QFont.Bold))
        amount_header.setAlignment(Qt.AlignCenter)
        amount_header.setStyleSheet("padding: 5px;")
        header_layout.addWidget(amount_header, 3)
        
        layout.addLayout(header_layout)
        
        # Items grid
        self.expense_grid = QGridLayout()
        self.expense_grid.setSpacing(5)
        self.expense_grid.setColumnStretch(0, 7)  # 70% for items
        self.expense_grid.setColumnStretch(1, 3)  # 30% for amount
        layout.addLayout(self.expense_grid)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_summary_bar(self):
        """Create summary bar with totals"""
        widget = QWidget()
        widget.setFixedHeight(40)
        widget.setStyleSheet("background-color: #f5f5f5; border-top: 2px solid #ccc;")
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 5, 20, 5)
        
        self.total_income_label = QLabel('Total Income: 0.00')
        self.total_income_label.setFont(QFont(Config.FONT_FAMILY, 11, QFont.Bold))
        self.total_income_label.setStyleSheet("color: #4CAF50;")
        layout.addWidget(self.total_income_label)
        
        layout.addStretch()
        
        self.total_expense_label = QLabel('Total Expenses: 0.00')
        self.total_expense_label.setFont(QFont(Config.FONT_FAMILY, 11, QFont.Bold))
        self.total_expense_label.setStyleSheet("color: #f44336;")
        layout.addWidget(self.total_expense_label)
        
        layout.addStretch()
        
        self.closing_balance_label = QLabel('Closing Balance: 0.00')
        self.closing_balance_label.setFont(QFont(Config.FONT_FAMILY, 11, QFont.Bold))
        layout.addWidget(self.closing_balance_label)
        
        widget.setLayout(layout)
        return widget
    
    def load_items(self):
        """Load income and expense items"""
        # Clear existing inputs
        self.income_inputs.clear()
        self.expense_inputs.clear()
        
        # Get Income category items
        categories = self.service.get_all_categories()
        income_id = None
        expense_id = None
        
        for cat_id, cat_name in categories:
            if cat_name == 'Income':
                income_id = cat_id
            elif cat_name == 'Expenses':
                expense_id = cat_id
        
        # Get existing amounts if editing
        existing_amounts = self.service.get_budget_entry_amounts(
            self.year_id, self.pastorate_id, self.data_type_id
        )
        
        # Load income items
        if income_id:
            income_items = self.service.get_items_by_category(income_id)
            for row, (item_id, item_name) in enumerate(income_items):
                label = QLabel(item_name)
                label.setStyleSheet("color: #4CAF50; padding: 3px;")
                self.income_grid.addWidget(label, row, 0)
                
                input_field = QLineEdit()
                input_field.setPlaceholderText('0.00')
                input_field.setAlignment(Qt.AlignRight)
                
                # Populate existing amount if available
                if item_id in existing_amounts:
                    amount = existing_amounts[item_id]
                    # Format the amount properly
                    input_field.setText(f'{amount:.2f}' if amount else '')
                
                input_field.textChanged.connect(self.calculate_totals)
                self.income_grid.addWidget(input_field, row, 1)
                
                self.income_inputs[item_id] = input_field
        
        # Load expense items
        if expense_id:
            expense_items = self.service.get_items_by_category(expense_id)
            for row, (item_id, item_name) in enumerate(expense_items):
                label = QLabel(item_name)
                label.setStyleSheet("color: #f44336; padding: 3px;")
                self.expense_grid.addWidget(label, row, 0)
                
                input_field = QLineEdit()
                input_field.setPlaceholderText('0.00')
                input_field.setAlignment(Qt.AlignRight)
                
                # Populate existing amount if available
                if item_id in existing_amounts:
                    amount = existing_amounts[item_id]
                    # Format the amount properly
                    input_field.setText(f'{amount:.2f}' if amount else '')
                
                input_field.textChanged.connect(self.calculate_totals)
                self.expense_grid.addWidget(input_field, row, 1)
                
                self.expense_inputs[item_id] = input_field
        
        # Calculate totals after loading
        self.calculate_totals()
    
    def calculate_totals(self):
        """Calculate and update totals"""
        total_income = 0.0
        for input_field in self.income_inputs.values():
            try:
                value = float(input_field.text() or 0)
                total_income += value
            except ValueError:
                pass
        
        total_expense = 0.0
        for input_field in self.expense_inputs.values():
            try:
                value = float(input_field.text() or 0)
                total_expense += value
            except ValueError:
                pass
        
        closing_balance = total_income - total_expense
        
        self.total_income_label.setText(f'Total Income: {total_income:,.2f}')
        self.total_expense_label.setText(f'Total Expenses: {total_expense:,.2f}')
        self.closing_balance_label.setText(f'Closing Balance: {closing_balance:,.2f}')
    
    def create_action_bar(self):
        """Create action bar with Save and Cancel buttons"""
        widget = QWidget()
        widget.setFixedHeight(50)
        widget.setStyleSheet("background-color: #f5f5f5; border-top: 2px solid #ccc;")
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 5, 20, 5)
        
        layout.addStretch()
        
        cancel_btn = QPushButton('Cancel')
        cancel_btn.setStyleSheet('background-color: #f44336; color: white; font-weight: bold; padding: 10px 30px;')
        cancel_btn.clicked.connect(self.cancel_entry)
        layout.addWidget(cancel_btn)
        
        save_btn = QPushButton('Save')
        save_btn.setStyleSheet('background-color: #4CAF50; color: white; font-weight: bold; padding: 10px 30px;')
        save_btn.clicked.connect(self.save_entry)
        layout.addWidget(save_btn)
        
        widget.setLayout(layout)
        return widget
    
    def save_entry(self):
        """Save budget entry to database"""
        try:
            # Get Income and Expenses category IDs
            categories = self.service.get_all_categories()
            income_id = None
            expense_id = None
            
            for cat_id, cat_name in categories:
                if cat_name == 'Income':
                    income_id = cat_id
                elif cat_name == 'Expenses':
                    expense_id = cat_id
            
            # Delete existing entries for this year/pastorate/data_type
            self.service.delete_budget_entries(self.year_id, self.pastorate_id, self.data_type_id)
            
            # Save income entries
            for item_id, input_field in self.income_inputs.items():
                amount_text = input_field.text().strip()
                if amount_text:
                    try:
                        amount = float(amount_text)
                        if amount > 0:
                            self.service.save_budget_entry(
                                self.year_id, self.pastorate_id, self.data_type_id,
                                income_id, item_id, amount
                            )
                    except ValueError:
                        pass
            
            # Save expense entries
            for item_id, input_field in self.expense_inputs.items():
                amount_text = input_field.text().strip()
                if amount_text:
                    try:
                        amount = float(amount_text)
                        if amount > 0:
                            self.service.save_budget_entry(
                                self.year_id, self.pastorate_id, self.data_type_id,
                                expense_id, item_id, amount
                            )
                    except ValueError:
                        pass
            
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, 'Success', 'Entry saved successfully!')
            self.back_to_list.emit()
            
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, 'Error', f'Failed to save: {str(e)}')
    
    def cancel_entry(self):
        """Cancel and go back to list"""
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, 'Confirm', 
                                     'Are you sure you want to cancel? Unsaved changes will be lost.',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.back_to_list.emit()
