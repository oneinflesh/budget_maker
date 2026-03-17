from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from config import Config


class RevisedBudgetWindow(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel('Revised Budget')
        title.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_HEADING, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        placeholder = QLabel('Revised budget functionality will be implemented here')
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)
        
        layout.addStretch()
        self.setLayout(layout)
