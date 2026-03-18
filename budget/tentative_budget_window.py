from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QPushButton, QStackedWidget, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database.category_service import CategoryService
from budget.tentative_budget_view import TentativeBudgetView
from config import Config


class TentativeBudgetWindow(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.service = CategoryService(db_manager)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Stacked widget to switch between selection and view
        self.stacked_widget = QStackedWidget()
        
        # Selection page
        self.selection_page = self.create_selection_page()
        self.stacked_widget.addWidget(self.selection_page)
        
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
    
    def create_selection_page(self):
        """Create the selection page for pastorate and year"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Title
        title = QLabel('Create Tentative Budget')
        title.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_HEADING, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Pastorate selection
        pastorate_layout = QHBoxLayout()
        pastorate_label = QLabel('Select Pastorate:')
        pastorate_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL))
        pastorate_label.setMinimumWidth(150)
        pastorate_layout.addWidget(pastorate_label)
        
        self.pastorate_combo = QComboBox()
        self.pastorate_combo.setMinimumWidth(300)
        self.load_pastorates()
        pastorate_layout.addWidget(self.pastorate_combo)
        pastorate_layout.addStretch()
        
        layout.addLayout(pastorate_layout)
        
        # Year selection
        year_layout = QHBoxLayout()
        year_label = QLabel('Select Year:')
        year_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL))
        year_label.setMinimumWidth(150)
        year_layout.addWidget(year_label)
        
        self.year_combo = QComboBox()
        self.year_combo.setMinimumWidth(300)
        self.load_years()
        year_layout.addWidget(self.year_combo)
        year_layout.addStretch()
        
        layout.addLayout(year_layout)
        
        layout.addSpacing(20)
        
        # Create button
        create_btn = QPushButton('Create Tentative Budget')
        create_btn.setStyleSheet('''
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
        create_btn.clicked.connect(self.create_budget_view)
        layout.addWidget(create_btn, alignment=Qt.AlignCenter)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def load_pastorates(self):
        """Load pastorates into combo box"""
        pastorates = self.service.get_all_pastorates()
        for pastorate_id, pastorate_name in pastorates:
            self.pastorate_combo.addItem(pastorate_name, pastorate_id)
    
    def load_years(self):
        """Load years into combo box"""
        years = self.service.get_all_years()
        for year_id, year in years:
            self.year_combo.addItem(year, year_id)
    
    def create_budget_view(self):
        """Create and show the budget view"""
        if self.pastorate_combo.count() == 0:
            QMessageBox.warning(self, 'Error', 'No pastorates available. Please add a pastorate first.')
            return
        
        if self.year_combo.count() == 0:
            QMessageBox.warning(self, 'Error', 'No years available. Please add a year first.')
            return
        
        pastorate_id = self.pastorate_combo.currentData()
        pastorate_name = self.pastorate_combo.currentText()
        year_id = self.year_combo.currentData()
        year = self.year_combo.currentText()
        
        # Create budget view
        budget_view = TentativeBudgetView(self.db, pastorate_id, pastorate_name, year_id, year)
        budget_view.back_to_selection.connect(self.back_to_selection)
        
        self.stacked_widget.addWidget(budget_view)
        self.stacked_widget.setCurrentWidget(budget_view)
    
    def back_to_selection(self):
        """Return to selection page"""
        self.stacked_widget.setCurrentIndex(0)
        # Remove budget view from stack
        if self.stacked_widget.count() > 1:
            widget = self.stacked_widget.widget(1)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
