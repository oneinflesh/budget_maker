"""Loading dialog for async operations"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from config import Config


class LoadingDialog(QDialog):
    def __init__(self, parent=None, message="Loading..."):
        super().__init__(parent)
        self.setWindowTitle("Please Wait")
        self.setModal(True)
        self.setFixedSize(300, 100)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        
        layout = QVBoxLayout()
        
        label = QLabel(message)
        label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        progress = QProgressBar()
        progress.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(progress)
        
        self.setLayout(layout)


class WorkerThread(QThread):
    """Generic worker thread for database operations"""
    finished = Signal(object)
    error = Signal(str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
