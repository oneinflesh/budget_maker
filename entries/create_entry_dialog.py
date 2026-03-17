from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QPushButton, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database.category_service import CategoryService
from config import Config


class CreateEntryDialog(QDialog):
    def __init__(self, db_manager, data_type_name, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.service = CategoryService(db_manager)
        self.data_type_name = data_type_name
        self.selected_year_id = None
        self.selected_pastorate_id = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f'Create {self.data_type_name} Entry')
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        title = QLabel(f'Create New {self.data_type_name} Entry')
        title.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_SUBHEADING, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Year selection
        year_label = QLabel('Select Financial Year:')
        layout.addWidget(year_label)
        
        self.year_combo = QComboBox()
        self.load_years()
        layout.addWidget(self.year_combo)
        
        # Pastorate selection
        pastorate_label = QLabel('Select Pastorate:')
        layout.addWidget(pastorate_label)
        
        self.pastorate_combo = QComboBox()
        self.load_pastorates()
        layout.addWidget(self.pastorate_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        create_btn = QPushButton('Create')
        create_btn.setStyleSheet('background-color: #4CAF50; color: white; font-weight: bold;')
        create_btn.clicked.connect(self.handle_create)
        button_layout.addWidget(create_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_years(self):
        """Load years from database"""
        years = self.service.get_all_years()
        for year_id, year in years:
            self.year_combo.addItem(year, year_id)
    
    def load_pastorates(self):
        """Load pastorates from database"""
        pastorates = self.service.get_all_pastorates()
        for pastorate_id, name in pastorates:
            self.pastorate_combo.addItem(name, pastorate_id)
    
    def handle_create(self):
        """Validate and accept dialog"""
        if self.year_combo.count() == 0:
            QMessageBox.warning(self, 'Error', 'No years available. Please add years in Categories.')
            return
        
        if self.pastorate_combo.count() == 0:
            QMessageBox.warning(self, 'Error', 'No pastorates available. Please add pastorates in Categories.')
            return
        
        self.selected_year_id = self.year_combo.currentData()
        self.selected_pastorate_id = self.pastorate_combo.currentData()
        
        self.accept()
