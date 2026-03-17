from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont
from datetime import datetime
import pytz
from config import Config


class StatusBar(QWidget):
    def __init__(self, username, db_manager):
        super().__init__()
        self.username = username
        self.db = db_manager
        self.name = db_manager.get_user_name(username)
        self.init_ui()
        self.start_clock()
    
    def init_ui(self):
        self.setFixedHeight(30)
        self.setStyleSheet("background-color: #E0E0E0;")  # Removed border-top
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # No margins
        layout.setSpacing(0)  # No spacing
        
        # Left: Username - takes 1/3 of space
        username_container = QWidget()
        username_container.setStyleSheet("background-color: #E0E0E0;")
        username_layout = QHBoxLayout()
        username_layout.setContentsMargins(15, 5, 15, 5)
        self.username_label = QLabel(f'User: {self.name}')
        self.username_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL))
        username_layout.addWidget(self.username_label)
        username_container.setLayout(username_layout)
        layout.addWidget(username_container, 1)
        
        # Center: Date and Time - takes 1/3 of space
        datetime_container = QWidget()
        datetime_container.setStyleSheet("background-color: #E0E0E0;")
        datetime_layout = QHBoxLayout()
        datetime_layout.setContentsMargins(15, 5, 15, 5)
        self.datetime_label = QLabel()
        self.datetime_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL, QFont.Bold))
        self.datetime_label.setAlignment(Qt.AlignCenter)
        datetime_layout.addWidget(self.datetime_label)
        datetime_container.setLayout(datetime_layout)
        layout.addWidget(datetime_container, 1)
        
        # Right: Database Status - takes 1/3 of space
        db_container = QWidget()
        db_container.setStyleSheet("background-color: #E0E0E0;")
        db_layout = QHBoxLayout()
        db_layout.setContentsMargins(15, 5, 15, 5)
        db_layout.addStretch()
        self.db_status_label = QLabel()
        self.db_status_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL))
        db_layout.addWidget(self.db_status_label)
        db_container.setLayout(db_layout)
        layout.addWidget(db_container, 1)
        
        self.update_db_status()
    
    def start_clock(self):
        """Start timer to update clock every second"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # Update every 1 second
        self.update_datetime()  # Initial update
    
    def update_datetime(self):
        """Update date and time display with Indian timezone"""
        try:
            ist = pytz.timezone('Asia/Kolkata')
            now = datetime.now(ist)
            formatted_time = now.strftime('%d-%m-%Y %I:%M:%S %p')
            self.datetime_label.setText(formatted_time)
        except Exception:
            # Fallback to system time if timezone fails
            now = datetime.now()
            formatted_time = now.strftime('%d-%m-%Y %I:%M:%S %p')
            self.datetime_label.setText(formatted_time)
    
    def update_db_status(self):
        """Check database connection and update status indicator"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
                cursor.fetchone()
            # Green indicator - connected
            self.db_status_label.setText('● Database Connected')
            self.db_status_label.setStyleSheet('color: #32CD32;')
        except Exception as e:
            # Red indicator - disconnected
            self.db_status_label.setText('● Database Error')
            self.db_status_label.setStyleSheet('color: #FF0000;')
    
    def update_username(self, new_username):
        """Update username display"""
        self.username = new_username
        self.name = self.db.get_user_name(new_username)
        self.username_label.setText(f'User: {self.name}')
    
    def update_name(self, new_name):
        """Update display name"""
        self.name = new_name
        self.username_label.setText(f'User: {new_name}')
