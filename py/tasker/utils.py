# utils.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer


class AutoCloseMessageBox(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Success")
        self.setFixedSize(300, 80)
        self.setStyleSheet("""
            QDialog {
                background-color: #252526;
                border: 1px solid #007acc;
            }
            QLabel {
                color: #cccccc;
                font-size: 13px;
                font-weight: 500;
                background: transparent;
            }
        """)
        
        layout = QVBoxLayout()
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)
        
        QTimer.singleShot(200, self.close)