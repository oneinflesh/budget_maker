from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Qt
from entries.entry_tab import EntryTab
from database.category_service import CategoryService


class EntriesWindow(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.service = CategoryService(db_manager)
        self.init_ui()
    
    def refresh_all_tabs(self):
        """Refresh all entry tabs to show updated data"""
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if hasattr(tab, 'load_entries'):
                tab.load_entries()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tab_widget = QTabWidget()
        
        # Dynamically create tabs based on data types
        self.load_data_type_tabs()
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def load_data_type_tabs(self):
        """Load tabs dynamically based on data types in database"""
        data_types = self.service.get_all_data_types()
        
        for data_type_id, data_type_name in data_types:
            entry_tab = EntryTab(self.db, data_type_id, data_type_name)
            self.tab_widget.addTab(entry_tab, data_type_name)
