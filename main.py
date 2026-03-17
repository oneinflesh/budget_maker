import sys
from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from database.db_manager import DatabaseManager
from login.login_window import LoginWindow
from dashboard.dashboard_window import DashboardWindow
from config import Config


class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # Force light theme using config
        self.app.setStyle(QStyleFactory.create('Fusion'))
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(*Config.WINDOW_BG))
        palette.setColor(QPalette.WindowText, QColor(*Config.WINDOW_TEXT))
        palette.setColor(QPalette.Base, QColor(*Config.BASE_BG))
        palette.setColor(QPalette.AlternateBase, QColor(*Config.ALTERNATE_BASE))
        palette.setColor(QPalette.ToolTipBase, QColor(*Config.BASE_BG))
        palette.setColor(QPalette.ToolTipText, QColor(*Config.WINDOW_TEXT))
        palette.setColor(QPalette.Text, QColor(*Config.WINDOW_TEXT))
        palette.setColor(QPalette.Button, QColor(*Config.BUTTON_BG))
        palette.setColor(QPalette.ButtonText, QColor(*Config.WINDOW_TEXT))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(*Config.LINK_COLOR))
        palette.setColor(QPalette.Highlight, QColor(*Config.HIGHLIGHT_COLOR))
        palette.setColor(QPalette.HighlightedText, QColor(*Config.HIGHLIGHT_TEXT))
        self.app.setPalette(palette)
        
        self.db = DatabaseManager(Config.DB_NAME)
        self.db.init_database()
        
        self.login_window = None
        self.dashboard_window = None
        
        self.show_login()
    
    def show_login(self):
        self.login_window = LoginWindow(self.db)
        self.login_window.login_successful.connect(self.show_dashboard)
        self.login_window.setWindowState(Qt.WindowState.WindowMaximized)
        self.login_window.show()
    
    def show_dashboard(self, username):
        if self.login_window:
            self.login_window.hide()  # Hide instead of close
        
        self.dashboard_window = DashboardWindow(username, self.db)
        self.dashboard_window.logout_signal.connect(self.handle_logout)
        self.dashboard_window.setWindowState(Qt.WindowState.WindowMaximized)
        self.dashboard_window.show()
    
    def handle_logout(self):
        if self.dashboard_window:
            self.dashboard_window.hide()  # Hide instead of close
        if self.login_window:
            # Clear login fields before showing
            self.login_window.username_input.clear()
            self.login_window.password_input.clear()
            self.login_window.remember_checkbox.setChecked(False)
            self.login_window.show()
        else:
            self.show_login()
    
    def run(self):
        try:
            return self.app.exec()
        finally:
            # Cleanup database connection on exit
            self.db.close()


if __name__ == '__main__':
    app = App()
    sys.exit(app.run())
