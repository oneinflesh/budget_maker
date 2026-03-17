from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from config import Config


class TopBar(QWidget):
    logout_clicked = Signal()
    dashboard_clicked = Signal()
    categories_clicked = Signal()
    user_clicked = Signal()
    entries_clicked = Signal()
    settings_clicked = Signal()
    tentative_budget_clicked = Signal()
    revised_budget_clicked = Signal()
    
    def __init__(self, username, name, db_manager):
        super().__init__()
        self.username = username
        self.name = name
        self.db = db_manager
        self.init_ui()
    
    def init_ui(self):
        self.setFixedHeight(Config.TOPBAR_HEIGHT)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        dashboard_btn = QPushButton('Dashboard')
        dashboard_btn.clicked.connect(self.dashboard_clicked.emit)
        layout.addWidget(dashboard_btn)
        
        categories_btn = QPushButton('Categories')
        categories_btn.clicked.connect(self.categories_clicked.emit)
        layout.addWidget(categories_btn)
        
        user_btn = QPushButton('User')
        user_btn.clicked.connect(self.user_clicked.emit)
        layout.addWidget(user_btn)
        
        entries_btn = QPushButton('Entries')
        entries_btn.clicked.connect(self.entries_clicked.emit)
        layout.addWidget(entries_btn)
        
        settings_btn = QPushButton('Settings')
        settings_btn.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(settings_btn)
        
        layout.addStretch()
        
        tentative_budget_btn = QPushButton('Tentative Budget')
        tentative_budget_btn.setStyleSheet('background-color: #FFD700; color: black; font-weight: bold;')
        tentative_budget_btn.clicked.connect(self.tentative_budget_clicked.emit)
        layout.addWidget(tentative_budget_btn)
        
        revised_budget_btn = QPushButton('Revised Budget')
        revised_budget_btn.setStyleSheet('background-color: #32CD32; color: white; font-weight: bold;')
        revised_budget_btn.clicked.connect(self.revised_budget_clicked.emit)
        layout.addWidget(revised_budget_btn)
        
        layout.addStretch()
        
        logout_btn = QPushButton('Logout')
        logout_btn.clicked.connect(self.logout_clicked.emit)
        layout.addWidget(logout_btn)
        
        self.setLayout(layout)
