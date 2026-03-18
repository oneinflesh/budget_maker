from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QScrollArea, QTableWidget, QTableWidgetItem, QMessageBox, QPushButton)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from database.category_service import CategoryService
from config import Config


class TentativeBudgetView(QWidget):
    back_to_selection = Signal()
    
    def __init__(self, db_manager, pastorate_id, pastorate_name, year_id, year):
        super().__init__()
        self.db = db_manager
        self.service = CategoryService(db_manager)
        self.pastorate_id = pastorate_id
        self.pastorate_name = pastorate_name
        self.year_id = year_id
        self.year = year
        
        # Store totals for closing balance calculation
        self.income_totals = [0.0, 0.0, 0.0, 0.0]
        self.expense_totals = [0.0, 0.0, 0.0, 0.0]
        
        # Store item IDs for saving
        self.income_items = []
        self.expense_items = []
        
        # Store opening balance item IDs
        self.income_opening_item_id = None
        self.expense_opening_item_id = None
        
        self.init_ui()
        self.load_budget_data()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Title bar
        title_widget = QWidget()
        title_widget.setStyleSheet('background-color: #f5f5f5; border-bottom: 2px solid #ccc;')
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(20, 10, 20, 10)
        
        # Back button
        back_btn = QPushButton('← Back')
        back_btn.setStyleSheet('''
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        ''')
        back_btn.clicked.connect(self.back_to_selection.emit)
        title_layout.addWidget(back_btn)
        
        title_layout.addSpacing(10)
        
        # Save Changes button
        save_btn = QPushButton('Save Changes')
        save_btn.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        ''')
        save_btn.clicked.connect(self.save_changes)
        title_layout.addWidget(save_btn)
        
        title_layout.addSpacing(20)
        
        title = QLabel(f'Tentative Budget for {self.pastorate_name} - {self.year}')
        title.setFont(QFont(Config.FONT_FAMILY, 14, QFont.Bold))
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        title_widget.setLayout(title_layout)
        main_layout.addWidget(title_widget)
        
        # Single scroll area for both tables (items only, not totals)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        scroll_content = QWidget()
        scroll_layout = QHBoxLayout()
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)
        
        # Income table (50% width)
        self.income_table = self.create_budget_table('INCOME')
        scroll_layout.addWidget(self.income_table, 1)
        
        # Expenses table (50% width)
        self.expense_table = self.create_budget_table('EXPENSES')
        scroll_layout.addWidget(self.expense_table, 1)
        
        # Sync vertical scrolling between tables
        self.income_table.verticalScrollBar().valueChanged.connect(
            self.expense_table.verticalScrollBar().setValue
        )
        self.expense_table.verticalScrollBar().valueChanged.connect(
            self.income_table.verticalScrollBar().setValue
        )
        
        # Connect cell changes to recalculate totals and opening balances
        self.income_table.itemChanged.connect(self.on_cell_changed)
        self.expense_table.itemChanged.connect(self.on_cell_changed)
        
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Sticky summary bar at bottom (Closing Balance/Deficit + Total)
        self.summary_bar = self.create_summary_bar()
        main_layout.addWidget(self.summary_bar)
        
        self.setLayout(main_layout)
    
    def create_summary_bar(self):
        """Create sticky summary bar with closing balance and totals"""
        widget = QWidget()
        widget.setStyleSheet('background-color: #f5f5f5; border-top: 2px solid #ccc;')
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Income summary table (50% width)
        self.income_summary = self.create_summary_table('INCOME')
        layout.addWidget(self.income_summary, 1)
        
        # Expenses summary table (50% width)
        self.expense_summary = self.create_summary_table('EXPENSES')
        layout.addWidget(self.expense_summary, 1)
        
        widget.setLayout(layout)
        return widget
    
    def create_summary_table(self, category_name):
        """Create summary table for closing balance and total"""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setRowCount(2)  # Closing Balance/Deficit + Total
        
        # Hide headers
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        
        # Stretch columns to match main tables
        from PySide6.QtWidgets import QHeaderView
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        
        # Set row heights
        table.setRowHeight(0, 30)
        table.setRowHeight(1, 30)
        
        # Fixed height for 2 rows (60px + some padding)
        table.setFixedHeight(65)
        table.setMaximumHeight(65)
        table.setMinimumHeight(65)
        
        # Disable scrollbars
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Disable size policies that might cause expansion
        from PySide6.QtWidgets import QSizePolicy
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Style
        if category_name == 'INCOME':
            table.setStyleSheet('''
                QTableWidget {
                    border-right: 2px solid #ccc;
                    background-color: #f5f5f5;
                    gridline-color: #ccc;
                }
            ''')
        else:
            table.setStyleSheet('''
                QTableWidget {
                    background-color: #f5f5f5;
                    gridline-color: #ccc;
                }
            ''')
        
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        
        return table
    
    def create_budget_table(self, category_name):
        """Create budget table for Income or Expenses"""
        table = QTableWidget()
        table.setColumnCount(5)
        
        # Calculate year columns
        current_year_start = int(self.year.split('-')[0])
        year_minus_2 = f'{current_year_start-2}-{current_year_start-1}'
        year_minus_1 = f'{current_year_start-1}-{current_year_start}'
        
        # Use category name instead of "Items"
        header_label = category_name  # "INCOME" or "EXPENSES"
        
        headers = [
            header_label,
            f'Actual\n{year_minus_2}',
            f'R-Budget\n{year_minus_1}',
            f'Actual Est\n{year_minus_1}',  # Actual Estimate is for year-1
            f'T-Budget\n{self.year}'
        ]
        
        table.setHorizontalHeaderLabels(headers)
        
        # Stretch columns to fill available space
        from PySide6.QtWidgets import QHeaderView
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Item name column stretches
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Amount columns stretch
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        
        # Disable row numbering
        table.verticalHeader().setVisible(False)
        
        # Keep table scrollbars enabled for syncing
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Style
        if category_name == 'INCOME':
            table.setStyleSheet('''
                QTableWidget {
                    border-right: 2px solid #ccc;
                    background-color: white;
                }
                QHeaderView::section {
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                    border: 1px solid #45a049;
                }
            ''')
        else:
            table.setStyleSheet('''
                QTableWidget {
                    background-color: white;
                }
                QHeaderView::section {
                    background-color: #f44336;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                    border: 1px solid #da190b;
                }
            ''')
        
        table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed | QTableWidget.AnyKeyPressed)  # Allow editing on any key press
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setTabKeyNavigation(False)  # Disable tab navigation, use arrows only
        
        return table
    
    def load_budget_data(self):
        """Load budget data for all columns"""
        # Get category IDs
        categories = self.service.get_all_categories()
        income_id = None
        expense_id = None
        
        for cat_id, cat_name in categories:
            if cat_name == 'Income':
                income_id = cat_id
            elif cat_name == 'Expenses':
                expense_id = cat_id
        
        # Calculate years
        current_year_start = int(self.year.split('-')[0])
        year_minus_2 = f'{current_year_start-2}-{current_year_start-1}'
        year_minus_1 = f'{current_year_start-1}-{current_year_start}'
        
        # Get year IDs
        year_ids = {}
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            for year_str in [year_minus_2, year_minus_1, self.year]:
                cursor.execute('SELECT id FROM years WHERE year = ?', (year_str,))
                result = cursor.fetchone()
                year_ids[year_str] = result[0] if result else None
        
        # Get data type IDs
        data_type_ids = {}
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            for dtype in ['Actual', 'R-Budget', 'Actual Estimate', 'T-Budget']:
                cursor.execute('SELECT id FROM data_types WHERE type_name = ?', (dtype,))
                result = cursor.fetchone()
                data_type_ids[dtype] = result[0] if result else None
        
        # Load Income data
        if income_id:
            self.populate_table(self.income_table, income_id, year_ids, data_type_ids, 
                              year_minus_2, year_minus_1, 'Income')
        
        # Load Expenses data
        if expense_id:
            self.populate_table(self.expense_table, expense_id, year_ids, data_type_ids, 
                              year_minus_2, year_minus_1, 'Expenses')
        
        # Make both tables same height (use the larger one)
        max_rows = max(self.income_table.rowCount(), self.expense_table.rowCount())
        self.income_table.setRowCount(max_rows)
        self.expense_table.setRowCount(max_rows)
        
        # Block signals during initial setup
        self.income_table.blockSignals(True)
        self.expense_table.blockSignals(True)
        
        # Recalculate totals excluding opening balance row
        self.recalculate_totals_excluding_opening()
        
        # Apply opening balance logic (closing balance from previous year becomes opening balance)
        self.apply_opening_balance_logic()
        
        # Calculate and update closing balance/deficit in sticky summary bar
        self.update_summary_bar()
        
        # Re-enable signals
        self.income_table.blockSignals(False)
        self.expense_table.blockSignals(False)
    
    def on_cell_changed(self, item):
        """Recalculate totals and opening balances when a cell is edited"""
        if not item:
            return
        
        # Only process amount columns (1-4), not item names (0)
        if item.column() == 0:
            return
        
        # Block signals to prevent infinite loops
        self.income_table.blockSignals(True)
        self.expense_table.blockSignals(True)
        
        # Recalculate totals (excluding opening balance row 0)
        self.recalculate_totals_excluding_opening()
        
        # Reapply opening balance logic (this will update row 0 and add to totals)
        self.apply_opening_balance_logic()
        
        # Update summary bar
        self.update_summary_bar()
        
        # Re-enable signals
        self.income_table.blockSignals(False)
        self.expense_table.blockSignals(False)
    
    def recalculate_totals_excluding_opening(self):
        """Recalculate totals for all columns excluding opening balance row"""
        # Reset totals
        self.income_totals = [0.0, 0.0, 0.0, 0.0]
        self.expense_totals = [0.0, 0.0, 0.0, 0.0]
        
        # Recalculate income totals (excluding row 0 - opening balance)
        for row_idx in range(1, self.income_table.rowCount()):
            for col_idx in range(1, 5):
                cell = self.income_table.item(row_idx, col_idx)
                if cell:
                    try:
                        amount = float(cell.text().replace(',', ''))
                        self.income_totals[col_idx - 1] += amount
                    except ValueError:
                        pass
        
        # Recalculate expense totals (excluding row 0 - opening deficit)
        for row_idx in range(1, self.expense_table.rowCount()):
            for col_idx in range(1, 5):
                cell = self.expense_table.item(row_idx, col_idx)
                if cell:
                    try:
                        amount = float(cell.text().replace(',', ''))
                        self.expense_totals[col_idx - 1] += amount
                    except ValueError:
                        pass
    
    def apply_opening_balance_logic(self):
        """Apply logic: Closing balance from one year becomes opening balance for next year"""
        # Column 1 closing → Column 2 & 3 opening
        # Column 3 closing → Column 4 opening
        
        # Note: Column 1 opening balance comes from database and should not be reset
        # Only reset columns 2, 3, 4 opening balance cells
        
        # Reset opening balance cells for columns 2, 3, 4 to 0 (we'll add the carried forward amount)
        for col_idx in [2, 3, 4]:  # Columns 2, 3, 4 only
            income_cell = self.income_table.item(0, col_idx)
            expense_cell = self.expense_table.item(0, col_idx)
            
            if income_cell:
                income_cell.setText('0.00')
            if expense_cell:
                expense_cell.setText('0.00')
        
        # Calculate closing balance for column 1 (Actual year-2)
        col1_diff = self.income_totals[0] - self.expense_totals[0]
        
        # Apply to columns 2 & 3 opening balance/deficit
        if col1_diff >= 0:
            # Surplus: Add to Income Opening Balance for columns 2 & 3
            if self.income_opening_item_id:
                # Column 2 (R-Budget)
                income_cell_2 = self.income_table.item(0, 2)
                if income_cell_2:
                    income_cell_2.setText(f'{col1_diff:,.2f}')
                    self.income_totals[1] += col1_diff
                
                # Column 3 (Actual Estimate)
                income_cell_3 = self.income_table.item(0, 3)
                if income_cell_3:
                    income_cell_3.setText(f'{col1_diff:,.2f}')
                    self.income_totals[2] += col1_diff
        else:
            # Deficit: Add to Expenses Opening Deficit for columns 2 & 3
            if self.expense_opening_item_id:
                # Column 2 (R-Budget)
                expense_cell_2 = self.expense_table.item(0, 2)
                if expense_cell_2:
                    expense_cell_2.setText(f'{abs(col1_diff):,.2f}')
                    self.expense_totals[1] += abs(col1_diff)
                
                # Column 3 (Actual Estimate)
                expense_cell_3 = self.expense_table.item(0, 3)
                if expense_cell_3:
                    expense_cell_3.setText(f'{abs(col1_diff):,.2f}')
                    self.expense_totals[2] += abs(col1_diff)
        
        # Calculate closing balance for column 3 (Actual Estimate year-1)
        col3_diff = self.income_totals[2] - self.expense_totals[2]
        
        # Apply to column 4 opening balance/deficit
        if col3_diff >= 0:
            # Surplus: Add to Income Opening Balance for column 4
            if self.income_opening_item_id:
                income_cell_4 = self.income_table.item(0, 4)
                if income_cell_4:
                    income_cell_4.setText(f'{col3_diff:,.2f}')
                    self.income_totals[3] += col3_diff
        else:
            # Deficit: Add to Expenses Opening Deficit for column 4
            if self.expense_opening_item_id:
                expense_cell_4 = self.expense_table.item(0, 4)
                if expense_cell_4:
                    expense_cell_4.setText(f'{abs(col3_diff):,.2f}')
                    self.expense_totals[3] += abs(col3_diff)
    
    def populate_table(self, table, category_id, year_ids, data_type_ids, 
                      year_minus_2, year_minus_1, category_name):
        """Populate table with budget data"""
        # Get items for this category
        items = self.service.get_items_by_category(category_id)
        
        # Find Opening Balance/Deficit item (first item in the list)
        opening_item_id = items[0][0] if items else None
        
        # Get budget amounts for all combinations
        budget_data = {}
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT item_id, year_id, data_type_id, amount
                FROM budget
                WHERE pastorate_id = ? AND category_id = ?
            ''', (self.pastorate_id, category_id))
            
            for item_id, year_id, dtype_id, amount in cursor.fetchall():
                key = (item_id, year_id, dtype_id)
                budget_data[key] = amount
        
        # Populate rows (without closing balance and total rows)
        table.setRowCount(len(items))  # Only item rows, no summary rows
        
        totals = [0.0, 0.0, 0.0, 0.0]  # For each column
        
        for row_idx, (item_id, item_name) in enumerate(items):
            # Item name - NON-EDITABLE
            item_cell = QTableWidgetItem(item_name)
            if category_name == 'Income':
                item_cell.setForeground(Qt.darkGreen)
            else:
                item_cell.setForeground(Qt.darkRed)
            item_cell.setFlags(item_cell.flags() & ~Qt.ItemIsEditable)  # Make non-editable
            table.setItem(row_idx, 0, item_cell)
            
            # Column 1: Actual (year-2) - EDITABLE
            amount1 = budget_data.get((item_id, year_ids.get(year_minus_2), data_type_ids.get('Actual')), 0.0)
            cell1 = self.create_amount_cell(amount1)
            cell1.setFlags(cell1.flags() | Qt.ItemIsEditable)
            cell1.setBackground(Qt.white)
            table.setItem(row_idx, 1, cell1)
            totals[0] += amount1
            
            # Column 2: R-Budget (year-1) - EDITABLE
            amount2 = budget_data.get((item_id, year_ids.get(year_minus_1), data_type_ids.get('R-Budget')), 0.0)
            cell2 = self.create_amount_cell(amount2)
            cell2.setFlags(cell2.flags() | Qt.ItemIsEditable)
            cell2.setBackground(Qt.white)
            table.setItem(row_idx, 2, cell2)
            totals[1] += amount2
            
            # Column 3: Actual Estimate (year-1) - EDITABLE
            amount3 = budget_data.get((item_id, year_ids.get(year_minus_1), data_type_ids.get('Actual Estimate')), 0.0)
            cell3 = self.create_amount_cell(amount3)
            cell3.setFlags(cell3.flags() | Qt.ItemIsEditable)
            cell3.setBackground(Qt.white)
            table.setItem(row_idx, 3, cell3)
            totals[2] += amount3
            
            # Column 4: T-Budget (current year) - EDITABLE
            amount4 = budget_data.get((item_id, year_ids.get(self.year), data_type_ids.get('T-Budget')), 0.0)
            cell4 = self.create_amount_cell(amount4)
            cell4.setFlags(cell4.flags() | Qt.ItemIsEditable)
            cell4.setBackground(Qt.white)
            table.setItem(row_idx, 4, cell4)
            totals[3] += amount4
        
        # Store totals and items for saving
        if category_name == 'Income':
            self.income_totals = totals.copy()
            self.income_items = [(item_id, item_name) for item_id, item_name in items]
            self.income_opening_item_id = opening_item_id
        else:
            self.expense_totals = totals.copy()
            self.expense_items = [(item_id, item_name) for item_id, item_name in items]
            self.expense_opening_item_id = opening_item_id
        
        # Store year IDs for saving
        self.year_minus_2 = year_minus_2
        self.year_minus_1 = year_minus_1
        self.year_ids_map = year_ids
        self.data_type_ids_map = data_type_ids
    
    def create_amount_cell(self, amount):
        """Create formatted amount cell"""
        cell = QTableWidgetItem(f'{amount:,.2f}' if amount else '0.00')
        cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return cell
    
    def add_closing_row(self, table, row_idx, category_name, totals):
        """Add closing balance/deficit row"""
        # This will be calculated after we know both income and expense totals
        # For now, just add placeholder
        if category_name == 'Income':
            label_cell = QTableWidgetItem('Closing Deficit')
            label_cell.setForeground(Qt.red)
            label_cell.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
        else:
            label_cell = QTableWidgetItem('Closing Balance')
            label_cell.setForeground(Qt.darkGreen)
            label_cell.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
        
        table.setItem(row_idx, 0, label_cell)
        
        # Placeholder amounts (will be calculated)
        for col in range(1, 5):
            cell = QTableWidgetItem('0.00')
            cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            cell.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
            table.setItem(row_idx, col, cell)
    
    def add_total_row(self, table, row_idx, totals):
        """Add total row"""
        label_cell = QTableWidgetItem('Total')
        label_cell.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
        table.setItem(row_idx, 0, label_cell)
        
        for col_idx, total in enumerate(totals, start=1):
            cell = QTableWidgetItem(f'{total:,.2f}')
            cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            cell.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
            cell.setBackground(Qt.lightGray)
            table.setItem(row_idx, col_idx, cell)
    
    def update_summary_bar(self):
        """Update sticky summary bar with closing balance and totals"""
        # Row 0: Closing Balance/Deficit
        # Row 1: Total
        
        for col_idx in range(4):
            diff = self.income_totals[col_idx] - self.expense_totals[col_idx]
            
            if diff >= 0:
                # Surplus: Show on Expenses side as Closing Balance (GREEN)
                # Income side closing deficit = 0
                income_label = QTableWidgetItem('Closing Deficit' if col_idx == 0 else '')
                income_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
                income_label.setForeground(Qt.red)
                if col_idx == 0:
                    self.income_summary.setItem(0, 0, income_label)
                
                income_cell = QTableWidgetItem('0.00')
                income_cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                income_cell.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
                self.income_summary.setItem(0, col_idx + 1, income_cell)
                
                # Expenses side closing balance = diff
                expense_label = QTableWidgetItem('Closing Balance' if col_idx == 0 else '')
                expense_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
                expense_label.setForeground(Qt.darkGreen)
                if col_idx == 0:
                    self.expense_summary.setItem(0, 0, expense_label)
                
                expense_cell = QTableWidgetItem(f'{diff:,.2f}')
                expense_cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                expense_cell.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
                expense_cell.setForeground(Qt.darkGreen)
                self.expense_summary.setItem(0, col_idx + 1, expense_cell)
                
                # Totals
                income_total_label = QTableWidgetItem('Total' if col_idx == 0 else '')
                income_total_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
                if col_idx == 0:
                    self.income_summary.setItem(1, 0, income_total_label)
                
                income_total_cell = QTableWidgetItem(f'{self.income_totals[col_idx]:,.2f}')
                income_total_cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                income_total_cell.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
                income_total_cell.setBackground(Qt.lightGray)
                self.income_summary.setItem(1, col_idx + 1, income_total_cell)
                
                expense_total_label = QTableWidgetItem('Total' if col_idx == 0 else '')
                expense_total_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
                if col_idx == 0:
                    self.expense_summary.setItem(1, 0, expense_total_label)
                
                expense_total_cell = QTableWidgetItem(f'{self.expense_totals[col_idx] + diff:,.2f}')
                expense_total_cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                expense_total_cell.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
                expense_total_cell.setBackground(Qt.lightGray)
                self.expense_summary.setItem(1, col_idx + 1, expense_total_cell)
                
            else:
                # Deficit: Show on Income side as Closing Deficit (RED)
                income_label = QTableWidgetItem('Closing Deficit' if col_idx == 0 else '')
                income_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
                income_label.setForeground(Qt.red)
                if col_idx == 0:
                    self.income_summary.setItem(0, 0, income_label)
                
                income_cell = QTableWidgetItem(f'{abs(diff):,.2f}')
                income_cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                income_cell.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
                income_cell.setForeground(Qt.red)
                self.income_summary.setItem(0, col_idx + 1, income_cell)
                
                # Expenses side closing balance = 0
                expense_label = QTableWidgetItem('Closing Balance' if col_idx == 0 else '')
                expense_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
                expense_label.setForeground(Qt.darkGreen)
                if col_idx == 0:
                    self.expense_summary.setItem(0, 0, expense_label)
                
                expense_cell = QTableWidgetItem('0.00')
                expense_cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                expense_cell.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
                self.expense_summary.setItem(0, col_idx + 1, expense_cell)
                
                # Totals
                income_total_label = QTableWidgetItem('Total' if col_idx == 0 else '')
                income_total_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
                if col_idx == 0:
                    self.income_summary.setItem(1, 0, income_total_label)
                
                income_total_cell = QTableWidgetItem(f'{self.income_totals[col_idx] + abs(diff):,.2f}')
                income_total_cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                income_total_cell.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
                income_total_cell.setBackground(Qt.lightGray)
                self.income_summary.setItem(1, col_idx + 1, income_total_cell)
                
                expense_total_label = QTableWidgetItem('Total' if col_idx == 0 else '')
                expense_total_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
                if col_idx == 0:
                    self.expense_summary.setItem(1, 0, expense_total_label)
                
                expense_total_cell = QTableWidgetItem(f'{self.expense_totals[col_idx]:,.2f}')
                expense_total_cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                expense_total_cell.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
                expense_total_cell.setBackground(Qt.lightGray)
                self.expense_summary.setItem(1, col_idx + 1, expense_total_cell)

    
    def save_changes(self):
        """Save all budget changes to database"""
        try:
            # Get category IDs
            categories = self.service.get_all_categories()
            income_id = None
            expense_id = None
            
            for cat_id, cat_name in categories:
                if cat_name == 'Income':
                    income_id = cat_id
                elif cat_name == 'Expenses':
                    expense_id = cat_id
            
            saved_count = 0
            
            # Define columns to save: (column_index, year_key, data_type_name)
            columns_to_save = [
                (1, self.year_minus_2, 'Actual'),
                (2, self.year_minus_1, 'R-Budget'),
                (3, self.year_minus_1, 'Actual Estimate'),
                (4, self.year, 'T-Budget')
            ]
            
            # Save Income amounts for all columns
            for col_idx, year_key, dtype_name in columns_to_save:
                year_id = self.year_ids_map.get(year_key)
                dtype_id = self.data_type_ids_map.get(dtype_name)
                
                if not year_id or not dtype_id:
                    continue
                
                # Delete existing entries for this combination
                self.service.delete_budget_entries(year_id, self.pastorate_id, dtype_id)
                
                # Save new Income entries
                for row_idx, (item_id, item_name) in enumerate(self.income_items):
                    cell = self.income_table.item(row_idx, col_idx)
                    if cell:
                        amount_text = cell.text().replace(',', '').strip()
                        if amount_text and amount_text != '0.00':
                            try:
                                amount = float(amount_text)
                                if amount > 0:
                                    self.service.save_budget_entry(
                                        year_id, self.pastorate_id, dtype_id,
                                        income_id, item_id, amount
                                    )
                                    saved_count += 1
                            except ValueError:
                                pass
                
                # Save new Expenses entries
                for row_idx, (item_id, item_name) in enumerate(self.expense_items):
                    cell = self.expense_table.item(row_idx, col_idx)
                    if cell:
                        amount_text = cell.text().replace(',', '').strip()
                        if amount_text and amount_text != '0.00':
                            try:
                                amount = float(amount_text)
                                if amount > 0:
                                    self.service.save_budget_entry(
                                        year_id, self.pastorate_id, dtype_id,
                                        expense_id, item_id, amount
                                    )
                                    saved_count += 1
                            except ValueError:
                                pass
            
            QMessageBox.information(self, 'Success', 
                                   f'Saved {saved_count} budget entries successfully!')
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save: {str(e)}')
