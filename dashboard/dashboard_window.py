from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedWidget
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from components.topbar import TopBar
from components.statusbar import StatusBar
from user.user_window import UserPage
from categories.categories_window import CategoriesWindow
from entries.entries_window import EntriesWindow
from settings.settings_window import SettingsWindow
from budget.tentative_budget_window import TentativeBudgetWindow
from budget.revised_budget_window import RevisedBudgetWindow
from config import Config


class DashboardPage(QWidget):
    def __init__(self, username, db_manager):
        super().__init__()
        self.username = username
        self.db = db_manager
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        user_name = self.db.get_user_name(self.username)
        
        self.welcome_label = QLabel(f'Welcome, {user_name}')
        self.welcome_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_HEADING, QFont.Bold))
        self.welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.welcome_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def update_welcome(self, new_name):
        """Update welcome message when name changes"""
        self.welcome_label.setText(f'Welcome, {new_name}')


class DashboardWindow(QWidget):
    logout_signal = Signal()
    
    def __init__(self, username, db_manager):
        super().__init__()
        self.username = username
        self.db = db_manager
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Budget Maker - Dashboard')
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        user_name = self.db.get_user_name(self.username)
        
        self.topbar = TopBar(self.username, user_name, self.db)
        self.topbar.logout_clicked.connect(self.handle_logout)
        self.topbar.dashboard_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.topbar.categories_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.topbar.user_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.topbar.entries_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        self.topbar.settings_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        self.topbar.tentative_budget_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(5))
        self.topbar.revised_budget_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(6))
        main_layout.addWidget(self.topbar)
        
        self.stacked_widget = QStackedWidget()
        
        # Index 0: Dashboard
        self.dashboard_page = DashboardPage(self.username, self.db)
        self.stacked_widget.addWidget(self.dashboard_page)
        
        # Index 1: Categories
        self.categories_window = CategoriesWindow(self.db)
        self.categories_window.pastorate_changed.connect(self.on_pastorate_changed)
        self.categories_window.year_changed.connect(self.on_year_changed)
        self.stacked_widget.addWidget(self.categories_window)
        
        # Index 2: User
        self.user_page = UserPage(self.username, self.db)
        self.user_page.name_updated.connect(self.dashboard_page.update_welcome)
        self.stacked_widget.addWidget(self.user_page)
        
        # Index 3: Entries
        self.entries_window = EntriesWindow(self.db)
        self.stacked_widget.addWidget(self.entries_window)
        
        # Index 4: Settings
        self.settings_window = SettingsWindow(self.db)
        self.settings_window.data_imported.connect(self.entries_window.refresh_all_tabs)
        self.settings_window.pastorates_changed.connect(self.categories_window.refresh_pastorates)
        self.settings_window.years_changed.connect(self.categories_window.refresh_years)
        self.stacked_widget.addWidget(self.settings_window)
        
        # Index 5: Tentative Budget
        self.tentative_budget_window = TentativeBudgetWindow(self.db)
        self.settings_window.pastorates_changed.connect(self.tentative_budget_window.refresh_dropdowns)
        self.settings_window.years_changed.connect(self.tentative_budget_window.refresh_dropdowns)
        self.stacked_widget.addWidget(self.tentative_budget_window)
        
        # Index 6: Revised Budget
        self.revised_budget_window = RevisedBudgetWindow(self.db)
        self.stacked_widget.addWidget(self.revised_budget_window)
        
        main_layout.addWidget(self.stacked_widget)
        
        # Add status bar at bottom (create it first, then connect signals)
        self.statusbar = StatusBar(self.username, self.db)
        self.user_page.name_updated.connect(self.statusbar.update_name)
        self.user_page.username_updated.connect(self.statusbar.update_username)
        main_layout.addWidget(self.statusbar)
        
        self.setLayout(main_layout)
    
    def on_pastorate_changed(self):
        """Handle pastorate changes - refresh backup dropdown and tentative budget"""
        self.settings_window.refresh_backup_pastorates()
        self.tentative_budget_window.refresh_dropdowns()
    
    def on_year_changed(self):
        """Handle year changes - refresh tentative budget"""
        self.tentative_budget_window.refresh_dropdowns()
    
    def handle_logout(self):
        self.db.clear_session()
        self.logout_signal.emit()
