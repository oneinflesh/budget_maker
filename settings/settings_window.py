from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Qt, Signal
from settings.backup_tab import BackupTab
from settings.restore_tab import RestoreTab
from config import Config


class SettingsWindow(QWidget):
    data_imported = Signal()  # Signal to notify when data is imported
    pastorates_changed = Signal()  # Signal when pastorates are added
    years_changed = Signal()  # Signal when years are added
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Settings')
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f'''
            QTabWidget::pane {{
                border: 1px solid #ccc;
                background: white;
            }}
            QTabBar::tab {{
                background: #f0f0f0;
                padding: 10px 20px;
                margin-right: 2px;
                font-family: {Config.FONT_FAMILY};
                font-size: {Config.FONT_SIZE_NORMAL}px;
            }}
            QTabBar::tab:selected {{
                background: white;
                border-bottom: 3px solid #4CAF50;
            }}
        ''')
        
        # Add tabs
        self.backup_tab = BackupTab(self.db)
        self.restore_tab = RestoreTab(self.db)
        
        # Connect restore signals
        self.restore_tab.data_imported.connect(self.data_imported.emit)
        self.restore_tab.pastorates_changed.connect(self.pastorates_changed.emit)
        self.restore_tab.years_changed.connect(self.years_changed.emit)
        
        self.tabs.addTab(self.backup_tab, 'Backup')
        self.tabs.addTab(self.restore_tab, 'Restore')
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
    
    def refresh_backup_pastorates(self):
        """Refresh pastorate dropdown in backup tab"""
        self.backup_tab.refresh_pastorates()
