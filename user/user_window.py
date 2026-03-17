from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from database.user_service import UserService
from config import Config
from components.loading_dialog import LoadingDialog, WorkerThread


class UserPage(QWidget):
    name_updated = Signal(str)
    username_updated = Signal(str)
    
    def __init__(self, username, db_manager):
        super().__init__()
        self.username = username
        self.db = db_manager
        self.user_service = UserService(db_manager)
        self.worker = None
        self.loading_dialog = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(Config.WINDOW_MARGIN, Config.WINDOW_MARGIN, 
                                 Config.WINDOW_MARGIN, Config.WINDOW_MARGIN)
        layout.setSpacing(Config.WIDGET_SPACING)
        
        title = QLabel('User Profile')
        title.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_HEADING, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Two column layout
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(40)
        
        # Left column - Change username and name
        left_column = QVBoxLayout()
        left_column.setSpacing(Config.WIDGET_SPACING)
        
        username_title = QLabel('Change Username')
        username_title.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_SUBHEADING, QFont.Bold))
        left_column.addWidget(username_title)
        
        new_username_label = QLabel('Username')
        left_column.addWidget(new_username_label)
        
        self.new_username_input = QLineEdit()
        self.new_username_input.setText(self.username)
        self.new_username_input.setPlaceholderText('Enter new username')
        left_column.addWidget(self.new_username_input)
        
        update_username_btn = QPushButton('Update Username')
        update_username_btn.clicked.connect(self.update_username)
        left_column.addWidget(update_username_btn)
        
        left_column.addSpacing(20)
        
        # Name section
        name_title = QLabel('Change Name')
        name_title.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_SUBHEADING, QFont.Bold))
        left_column.addWidget(name_title)
        
        new_name_label = QLabel('Display Name')
        left_column.addWidget(new_name_label)
        
        self.new_name_input = QLineEdit()
        current_name = self.db.get_user_name(self.username)
        self.new_name_input.setText(current_name)
        self.new_name_input.setPlaceholderText('Enter display name')
        left_column.addWidget(self.new_name_input)
        
        update_name_btn = QPushButton('Update Name')
        update_name_btn.clicked.connect(self.update_name)
        left_column.addWidget(update_name_btn)
        
        left_column.addStretch()
        
        # Right column - Change password
        right_column = QVBoxLayout()
        right_column.setSpacing(Config.WIDGET_SPACING)
        
        password_title = QLabel('Change Password')
        password_title.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_SUBHEADING, QFont.Bold))
        right_column.addWidget(password_title)
        
        new_password_label = QLabel('New Password')
        right_column.addWidget(new_password_label)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText('Enter new password')
        self.new_password_input.setEchoMode(QLineEdit.Password)
        right_column.addWidget(self.new_password_input)
        
        confirm_password_label = QLabel('Confirm Password')
        right_column.addWidget(confirm_password_label)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText('Confirm new password')
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        right_column.addWidget(self.confirm_password_input)
        
        update_password_btn = QPushButton('Update Password')
        update_password_btn.clicked.connect(self.update_password)
        right_column.addWidget(update_password_btn)
        
        right_column.addStretch()
        
        # Add columns to row
        columns_layout.addLayout(left_column)
        columns_layout.addLayout(right_column)
        
        layout.addLayout(columns_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def update_username(self):
        new_username = self.new_username_input.text().strip()
        
        if not new_username:
            QMessageBox.warning(self, 'Error', 'Please enter a username')
            return
        
        if new_username == self.username:
            QMessageBox.information(self, 'Info', 'Username is already set to this value')
            return
        
        try:
            self.user_service.update_username(self.username, new_username)
            old_username = self.username
            self.username = new_username
            self.new_username_input.setText(new_username)
            self.username_updated.emit(new_username)
            QMessageBox.information(self, 'Success', 'Username updated successfully! Please re-login.')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to update username: {str(e)}')
    
    def update_name(self):
        new_name = self.new_name_input.text().strip()
        
        if not new_name:
            QMessageBox.warning(self, 'Error', 'Please enter a display name')
            return
        
        try:
            self.user_service.update_name(self.username, new_name)
            self.name_updated.emit(new_name)
            self.new_name_input.setText(new_name)
            QMessageBox.information(self, 'Success', 'Display name updated successfully!')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to update name: {str(e)}')
    
    def update_password(self):
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        if not new_password or not confirm_password:
            QMessageBox.warning(self, 'Error', 'Please enter both password fields')
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, 'Error', 'Passwords do not match')
            return
        
        if len(new_password) < Config.MIN_PASSWORD_LENGTH:
            QMessageBox.warning(self, 'Error', f'Password must be at least {Config.MIN_PASSWORD_LENGTH} characters')
            return
        
        # Show loading dialog
        self.loading_dialog = LoadingDialog(self, "Updating password...")
        self.loading_dialog.show()
        
        # Run update in background thread
        self.worker = WorkerThread(self.user_service.update_password, self.username, new_password)
        self.worker.finished.connect(self.on_password_updated)
        self.worker.error.connect(lambda err: self.on_update_error(err, 'password'))
        self.worker.start()
    
    def on_password_updated(self, result):
        if self.loading_dialog:
            self.loading_dialog.close()
        QMessageBox.information(self, 'Success', 'Password updated successfully!')
        self.new_password_input.clear()
        self.confirm_password_input.clear()
    
    def on_update_error(self, error_msg, field_type):
        if self.loading_dialog:
            self.loading_dialog.close()
        QMessageBox.warning(self, 'Error', f'Failed to update {field_type}: {error_msg}')
