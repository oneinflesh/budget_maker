from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Qt, Signal
from categories.pastorate_tab import PastorateTab
from categories.year_tab import YearTab
from categories.data_type_tab import DataTypeTab
from categories.category_tab import CategoryTab
from categories.item_tab import ItemTab


class CategoriesWindow(QWidget):
    pastorate_changed = Signal()  # Signal when pastorates change
    year_changed = Signal()  # Signal when years change
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()
    
    def refresh_pastorates(self):
        """Refresh pastorate tab data"""
        if hasattr(self, 'pastorate_tab'):
            self.pastorate_tab.load_data()
    
    def refresh_years(self):
        """Refresh year tab data"""
        if hasattr(self, 'year_tab'):
            self.year_tab.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        tab_widget = QTabWidget()
        
        # Create sub-tabs
        self.pastorate_tab = PastorateTab(self.db)
        self.year_tab = YearTab(self.db)
        self.data_type_tab = DataTypeTab(self.db)
        self.category_tab = CategoryTab(self.db)
        self.item_tab = ItemTab(self.db)
        
        tab_widget.addTab(self.pastorate_tab, "Pastorates")
        tab_widget.addTab(self.year_tab, "Years")
        tab_widget.addTab(self.data_type_tab, "Data Types")
        tab_widget.addTab(self.category_tab, "Categories")
        tab_widget.addTab(self.item_tab, "Items")
        
        # Connect category changes to item tab
        self.category_tab.category_changed.connect(self.item_tab.refresh_data)
        
        # Connect pastorate changes signal
        self.pastorate_tab.pastorate_changed.connect(self.pastorate_changed.emit)
        
        # Connect year changes signal
        self.year_tab.year_changed.connect(self.year_changed.emit)
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)
