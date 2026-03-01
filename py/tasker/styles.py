# styles.py - VS Code Dark Theme Style
VS_CODE_DARK_STYLE = """
/* Main Application */
QMainWindow {
    background-color: #1e1e1e;
    color: #d4d4d4;
    font-family: 'Segoe UI', 'Consolas', monospace;
}

QWidget {
    background-color: #1e1e1e;
    color: #d4d4d4;
    font-family: 'Segoe UI', 'Consolas', monospace;
    font-size: 13px;
}

/* Frames and Panels */
QFrame {
    background-color: #252526;
    border: 1px solid #3e3e42;
    border-radius: 0px;
    margin: 0px;
    padding: 0px;
}

/* Labels */
QLabel {
    background-color: transparent;
    color: #cccccc;
    padding: 8px 5px;
    font-size: 13px;
    border: none;
}

QLabel[cssClass="title"] {
    font-size: 14px;
    font-weight: 600;
    color: #ffffff;
    background-color: #2d2d30;
    padding: 12px 8px;
    border-bottom: 1px solid #3e3e42;
}

/* Input Fields */
QLineEdit {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #464647;
    border-radius: 2px;
    padding: 8px;
    font-size: 13px;
    selection-background-color: #264f78;
    selection-color: #ffffff;
}

QLineEdit:focus {
    border: 1px solid #007acc;
    background-color: #2d2d30;
}

QLineEdit:hover {
    border: 1px solid #565656;
}

/* List Widgets */
QListWidget {
    background-color: #252526;
    color: #cccccc;
    border: 1px solid #3e3e42;
    border-radius: 0px;
    font-size: 13px;
    outline: none;
    padding: 2px;
}

QListWidget::item {
    background-color: transparent;
    color: #cccccc;
    padding: 8px 5px;
    border: none;
    border-radius: 0px;
    margin: 1px 0px;
}

QListWidget::item:selected {
    background-color: #094771;
    color: #ffffff;
    border: none;
}

QListWidget::item:hover {
    background-color: #2a2d2e;
    border: none;
}

/* Buttons */
QPushButton {
    background-color: #0e639c;
    color: #ffffff;
    border: 1px solid #007acc;
    border-radius: 2px;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 500;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #1177bb;
    border: 1px solid #0098ff;
}

QPushButton:pressed {
    background-color: #005a9e;
    border: 1px solid #005a9e;
}

QPushButton:disabled {
    background-color: #424242;
    color: #666666;
    border: 1px solid #5a5a5a;
}

QPushButton[cssClass="secondary"] {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #565656;
}

QPushButton[cssClass="secondary"]:hover {
    background-color: #464647;
    border: 1px solid #666666;
}

/* Calendar */
QCalendarWidget {
    background-color: #252526;
    color: #cccccc;
    border: 1px solid #3e3e42;
    border-radius: 0px;
    font-size: 13px;
}

QCalendarWidget QToolButton {
    background-color: #2d2d30;
    color: #cccccc;
    border: 1px solid #464647;
    border-radius: 2px;
    padding: 6px;
    font-size: 12px;
    font-weight: 500;
}

QCalendarWidget QToolButton:hover {
    background-color: #37373d;
}

QCalendarWidget QMenu {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #464647;
}

QCalendarWidget QSpinBox {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #464647;
    border-radius: 2px;
    padding: 4px;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #3e3e42;
    background-color: #252526;
    border-radius: 0px;
    top: 1px;
}

QTabWidget::pane:selected {
    background-color: #252526;
}

QTabBar::tab {
    background-color: #2d2d30;
    color: #969696;
    padding: 8px 16px;
    border: none;
    border-bottom: 2px solid transparent;
    margin-right: 1px;
    font-size: 12px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #252526;
    color: #ffffff;
    border-bottom: 2px solid #007acc;
}

QTabBar::tab:hover {
    background-color: #37373d;
    color: #ffffff;
}

QTabBar::tab:!selected {
    margin-top: 2px;
}

/* Tree Widget */
QTreeWidget {
    background-color: #252526;
    color: #cccccc;
    border: 1px solid #3e3e42;
    border-radius: 0px;
    font-size: 13px;
    outline: none;
}

QTreeWidget::item {
    background-color: transparent;
    color: #cccccc;
    padding: 6px 4px;
    border: none;
    height: 22px;
}

QTreeWidget::item:selected {
    background-color: #094771;
    color: #ffffff;
}

QTreeWidget::item:hover {
    background-color: #2a2d2e;
}

QTreeWidget::item:has-children {
    font-weight: 600;
}

/* Text Edit */
QTextEdit {
    background-color: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #464647;
    border-radius: 2px;
    font-size: 13px;
    padding: 8px;
    font-family: 'Consolas', monospace;
    selection-background-color: #264f78;
}

QTextEdit:focus {
    border: 1px solid #007acc;
}

/* Checkboxes */
QCheckBox {
    background-color: transparent;
    color: #cccccc;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #666666;
    background-color: #3c3c3c;
    border-radius: 2px;
}

QCheckBox::indicator:checked {
    background-color: #0e639c;
    border: 1px solid #007acc;
    image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="white" d="M14 4l-8 8-4-4 1.5-1.5L6 9.5l6.5-6.5z"/></svg>');
}

QCheckBox::indicator:hover {
    border: 1px solid #969696;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 12px;
    border-radius: 0px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #424242;
    border-radius: 6px;
    min-height: 20px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #565656;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background: none;
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #1e1e1e;
    height: 12px;
    border-radius: 0px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #424242;
    border-radius: 6px;
    min-width: 20px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #565656;
}

/* Splitter */
QSplitter::handle {
    background-color: #3e3e42;
    border: none;
}

QSplitter::handle:hover {
    background-color: #007acc;
}

QSplitter::handle:horizontal {
    width: 4px;
}

QSplitter::handle:vertical {
    height: 4px;
}

/* Message Box */
QMessageBox {
    background-color: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #3e3e42;
}

QInputDialog {
    background-color: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #3e3e42;
}

/* Progress Bar */
QProgressBar {
    background-color: #3c3c3c;
    border: 1px solid #464647;
    border-radius: 2px;
    text-align: center;
    color: #cccccc;
}

QProgressBar::chunk {
    background-color: #0e639c;
    border-radius: 1px;
}

/* Group Box */
QGroupBox {
    background-color: #252526;
    color: #cccccc;
    border: 1px solid #3e3e42;
    border-radius: 0px;
    margin-top: 1ex;
    padding-top: 1ex;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    background-color: #252526;
}

/* Tool Tips */
QToolTip {
    background-color: #252526;
    color: #cccccc;
    border: 1px solid #3e3e42;
    padding: 4px;
    border-radius: 2px;
    font-size: 12px;
}

/* Combo Box */
QComboBox {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #464647;
    border-radius: 2px;
    padding: 6px;
    min-width: 6em;
}

QComboBox:hover {
    border: 1px solid #565656;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="%23cccccc" d="M4 6l4 4 4-4z"/></svg>');
}

QComboBox QAbstractItemView {
    background-color: #252526;
    color: #cccccc;
    border: 1px solid #464647;
    selection-background-color: #094771;
}
"""