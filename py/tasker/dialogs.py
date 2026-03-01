# dialogs.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QLineEdit, QPushButton, QLabel, 
                             QMessageBox, QTextEdit, QGroupBox, QCheckBox, 
                             QWidget, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QColor

from styles import VS_CODE_DARK_STYLE
from utils import AutoCloseMessageBox


class SubtasksDialog(QDialog):
    def __init__(self, task_text, task_id, db, parent=None):
        super().__init__(parent)
        self.task_text = task_text
        self.task_id = task_id
        self.db = db
        self.init_ui()
        self.load_subtasks()
        
    def init_ui(self):
        self.setWindowTitle(f"Subtasks: {self.task_text}")
        self.setGeometry(300, 300, 500, 400)
        self.setStyleSheet(VS_CODE_DARK_STYLE)
        
        layout = QVBoxLayout()
        
        # Add subtask section
        add_layout = QHBoxLayout()
        self.subtask_input = QLineEdit()
        self.subtask_input.setPlaceholderText("Enter new subtask...")
        self.subtask_input.returnPressed.connect(self.add_subtask)
        add_layout.addWidget(self.subtask_input)
        
        add_btn = QPushButton("Add Subtask")
        add_btn.setProperty("cssClass", "secondary")
        add_btn.clicked.connect(self.add_subtask)
        add_layout.addWidget(add_btn)
        
        layout.addLayout(add_layout)
        
        # Subtasks list
        self.subtasks_list = QListWidget()
        layout.addWidget(self.subtasks_list)
        
        buttons_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
    def load_subtasks(self):
        self.subtasks_list.clear()
        subtasks = self.db.get_subtasks(self.task_id)
        for subtask_id, text, completed in subtasks:
            item = QListWidgetItem()
            widget = QWidget()
            layout = QHBoxLayout(widget)
            
            checkbox = QCheckBox()
            checkbox.setChecked(bool(completed))
            checkbox.stateChanged.connect(lambda state, sid=subtask_id: self.toggle_subtask(sid, state))
            
            label = QLabel(text)
            if completed:
                label.setStyleSheet("color: #666666; text-decoration: line-through;")
            
            layout.addWidget(checkbox)
            layout.addWidget(label)
            layout.addStretch()
            
            delete_btn = QPushButton("✕")
            delete_btn.setFixedSize(20, 20)
            delete_btn.setProperty("cssClass", "secondary")
            delete_btn.clicked.connect(lambda checked, sid=subtask_id: self.delete_subtask(sid))
            layout.addWidget(delete_btn)
            
            layout.setContentsMargins(5, 2, 5, 2)
            widget.setLayout(layout)
            
            item.setSizeHint(widget.sizeHint())
            self.subtasks_list.addItem(item)
            self.subtasks_list.setItemWidget(item, widget)
            
    def add_subtask(self):
        text = self.subtask_input.text().strip()
        if text:
            self.db.add_subtask(self.task_id, text)
            self.subtask_input.clear()
            self.load_subtasks()
            
    def toggle_subtask(self, subtask_id, state):
        completed = bool(state)
        self.db.update_subtask(subtask_id, completed)
        self.load_subtasks()
        
    def delete_subtask(self, subtask_id):
        self.db.delete_subtask(subtask_id)
        self.load_subtasks()


class DescriptionDialog(QDialog):
    def __init__(self, task_text, description, task_id, db, parent=None):
        super().__init__(parent)
        self.task_text = task_text
        self.description = description
        self.task_id = task_id
        self.db = db
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f"Task Details: {self.task_text}")
        self.setGeometry(200, 200, 600, 500)
        self.setStyleSheet(VS_CODE_DARK_STYLE)
        
        layout = QVBoxLayout()
        
        # Description section
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout(desc_group)
        
        self.description_edit = QTextEdit()
        self.description_edit.setText(self.description)
        self.description_edit.setPlaceholderText("Enter task description...")
        desc_layout.addWidget(self.description_edit)
        
        layout.addWidget(desc_group)
        
        # Subtasks section
        subtasks_group = QGroupBox("Subtasks")
        subtasks_layout = QVBoxLayout(subtasks_group)
        
        subtasks_btn = QPushButton("Manage Subtasks")
        subtasks_btn.setProperty("cssClass", "secondary")
        subtasks_btn.clicked.connect(self.open_subtasks)
        subtasks_layout.addWidget(subtasks_btn)
        
        layout.addWidget(subtasks_group)
        
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_description)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("cssClass", "secondary")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        cursor = self.description_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.description_edit.setTextCursor(cursor)
        self.description_edit.setFocus()
        
    def save_description(self):
        self.description = self.description_edit.toPlainText()
        self.db.update_task(self.task_id, self.task_text, self.description)
        self.accept()
        
    def open_subtasks(self):
        dialog = SubtasksDialog(self.task_text, self.task_id, self.db, self)
        dialog.exec_()


class FolderDescriptionDialog(QDialog):
    def __init__(self, folder_name, description, folder_id, db, parent=None):
        super().__init__(parent)
        self.folder_name = folder_name
        self.description = description
        self.folder_id = folder_id
        self.db = db
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f"Folder Details: {self.folder_name}")
        self.setGeometry(200, 200, 500, 400)
        self.setStyleSheet(VS_CODE_DARK_STYLE)
        
        layout = QVBoxLayout()
        
        # Description section
        desc_group = QGroupBox("Folder Description")
        desc_layout = QVBoxLayout(desc_group)
        
        self.description_edit = QTextEdit()
        self.description_edit.setText(self.description)
        self.description_edit.setPlaceholderText("Enter folder description...")
        desc_layout.addWidget(self.description_edit)
        
        layout.addWidget(desc_group)
        
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_description)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("cssClass", "secondary")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
    def save_description(self):
        self.description = self.description_edit.toPlainText()
        self.db.update_folder_description(self.folder_id, self.description)
        self.accept()