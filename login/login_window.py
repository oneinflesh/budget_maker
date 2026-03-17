from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont
from config import Config
from components.loading_dialog import LoadingDialog, WorkerThread


class LoginWindow(QWidget):
    login_successful = Signal(str)
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.worker = None
        self.loading_dialog = None
        self.init_ui()
    
    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(Config.SESSION_CHECK_DELAY, self.check_saved_session)
    
    def init_ui(self):
        self.setWindowTitle('Budget Maker - Login')
        
        layout = QVBoxLayout()
        layout.setContentsMargins(Config.WINDOW_MARGIN, Config.WINDOW_MARGIN, 
                                 Config.WINDOW_MARGIN, Config.WINDOW_MARGIN)
        layout.setSpacing(Config.WIDGET_SPACING)
        
        layout.addStretch()
        
        # App name
        app_name = QLabel('Budget Maker')
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_TITLE, QFont.Bold))
        layout.addWidget(app_name)
        
        layout.addSpacing(50)
        
        # Username label
        username_label = QLabel('Username')
        username_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_LABEL))
        layout.addWidget(username_label, 0, Qt.AlignCenter)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Enter your username')
        self.username_input.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL))
        layout.addWidget(self.username_input, 0, Qt.AlignCenter)
        
        # Password label
        password_label = QLabel('Password')
        password_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_LABEL))
        layout.addWidget(password_label, 0, Qt.AlignCenter)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Enter your password')
        self.password_input.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL))
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.password_input, 0, Qt.AlignCenter)
        
        self.remember_checkbox = QCheckBox('Remember me')
        layout.addWidget(self.remember_checkbox, 0, Qt.AlignCenter)
        
        layout.addSpacing(10)
        
        login_btn = QPushButton('Login')
        login_btn.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
        login_btn.setMinimumHeight(40)
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn, 0, Qt.AlignCenter)
        
        # Reset password button
        reset_btn = QPushButton('Reset Password')
        reset_btn.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL))
        reset_btn.clicked.connect(self.show_reset_dialog)
        layout.addWidget(reset_btn, 0, Qt.AlignCenter)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        width = int(self.width() * Config.INPUT_WIDTH_RATIO)
        width = min(width, Config.INPUT_MAX_WIDTH)
        
        self.username_input.setFixedWidth(width)
        self.password_input.setFixedWidth(width)
        
        # Left align labels and checkbox to match input fields
        for label in self.findChildren(QLabel):
            if label.text() in ['Username', 'Password']:
                label.setFixedWidth(width)
                label.setAlignment(Qt.AlignLeft)
        
        self.remember_checkbox.setFixedWidth(width)
        
        for btn in self.findChildren(QPushButton):
            btn.setFixedWidth(width)
    
    def check_saved_session(self):
        saved_username = self.db.get_saved_session()
        if saved_username:
            self.hide()  # Hide login window immediately
            self.login_successful.emit(saved_username)
    
    def show_reset_dialog(self):
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle('Reset Password')
        dialog.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        title = QLabel('Enter Reset Code')
        title.setFont(QFont('Arial', 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        code_input = QLineEdit()
        code_input.setPlaceholderText('Enter reset code')
        code_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(code_input)
        
        reset_btn = QPushButton('Reset')
        reset_btn.clicked.connect(lambda: self.handle_reset(code_input.text(), dialog))
        layout.addWidget(reset_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def handle_reset(self, code, dialog):
        if code == Config.RESET_CODE:
            try:
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Reset to default admin/1234
                    hashed_password = self.db.hash_password('1234')
                    cursor.execute('DELETE FROM users')
                    cursor.execute('INSERT INTO users (username, password, name) VALUES (?, ?, ?)', 
                                 ('admin', hashed_password, 'Administrator'))
                    cursor.execute('DELETE FROM sessions')
                
                dialog.close()
                QMessageBox.information(self, 'Success', 
                    'Password reset successfully!\nUsername: admin\nPassword: 1234')
                
                # Clear login fields
                self.username_input.clear()
                self.password_input.clear()
                self.remember_checkbox.setChecked(False)
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to reset: {str(e)}')
        else:
            QMessageBox.warning(self, 'Error', 'Invalid reset code')
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Please enter username and password')
            return
        
        # Show loading dialog
        self.loading_dialog = LoadingDialog(self, "Logging in...")
        self.loading_dialog.show()
        
        # Run login in background thread
        self.worker = WorkerThread(self.db.verify_login, username, password)
        self.worker.finished.connect(lambda success: self.on_login_complete(success, username))
        self.worker.error.connect(self.on_login_error)
        self.worker.start()
    
    def on_login_complete(self, success, username):
        if self.loading_dialog:
            self.loading_dialog.close()
        
        if success:
            remember_me = self.remember_checkbox.isChecked()
            self.db.save_session(username, remember_me)
            self.login_successful.emit(username)
        else:
            QMessageBox.warning(self, 'Error', 'Invalid username or password')
            self.password_input.clear()
    
    def on_login_error(self, error_msg):
        if self.loading_dialog:
            self.loading_dialog.close()
        QMessageBox.warning(self, 'Error', f'Login failed: {error_msg}')
