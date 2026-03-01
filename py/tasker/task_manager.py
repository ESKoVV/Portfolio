# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QListWidgetItem, 
                             QLineEdit, QPushButton, QLabel, QMessageBox, 
                             QInputDialog, QFrame, QSplitter, QTabWidget,
                             QGroupBox, QTreeWidgetItem)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QKeySequence, QColor, QFont, QPainter
from PyQt5.QtWidgets import QShortcut

from database import TaskDatabase
from styles import VS_CODE_DARK_STYLE
from widgets import (DraggableListWidget, FolderTreeWidget, CustomCalendar, 
                    GraphView, CustomListWidget)
from dialogs import DescriptionDialog, FolderDescriptionDialog
from utils import AutoCloseMessageBox


class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = TaskDatabase()
        self.current_folder_id = None
        self.selected_date = QDate.currentDate().addDays(1)  # Tomorrow by default
        self.init_ui()
        self.load_data()
        self.setup_shortcuts()
        
    def init_ui(self):
        self.setWindowTitle('Task Manager')
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet(VS_CODE_DARK_STYLE)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Tasks with tabs
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Center panel - Folders with tabs
        center_panel = self.create_center_panel()
        main_splitter.addWidget(center_panel)
        
        # Right panel - Calendar
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        main_splitter.setSizes([400, 500, 500])
        main_layout.addWidget(main_splitter)
        
    def create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create tab widget for left panel
        self.left_tabs = QTabWidget()
        
        # Current Tasks tab (first tab)
        current_tasks_tab = self.create_current_tasks_tab()
        self.left_tabs.addTab(current_tasks_tab, "Current Tasks")
        
        # All Tasks tab (second tab)
        all_tasks_tab = self.create_all_tasks_tab()
        self.left_tabs.addTab(all_tasks_tab, "All Tasks")
        
        # Completed Tasks tab (third tab)
        completed_tasks_tab = self.create_completed_tasks_tab()
        self.left_tabs.addTab(completed_tasks_tab, "Completed Tasks")
        
        layout.addWidget(self.left_tabs)
        return panel
        
    def create_current_tasks_tab(self):
        """Create the Current Tasks tab - temporary task creation area"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
    
        # Current Tasks section
        current_group = QGroupBox("Current Tasks - Quick Creation")
        current_layout = QVBoxLayout(current_group)
    
        # Input section
        input_layout = QHBoxLayout()
        self.current_task_input = QLineEdit()
        self.current_task_input.setPlaceholderText("Enter new task...")
        self.current_task_input.returnPressed.connect(self.add_current_task)
        input_layout.addWidget(self.current_task_input)
    
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_current_task)
        input_layout.addWidget(add_btn)
    
        current_layout.addLayout(input_layout)
    
        # Tasks list - ВКЛЮЧАЕМ ПЕРЕТАСКИВАНИЕ
        self.current_tasks_list = DraggableListWidget()
        self.current_tasks_list.setDragDropMode(QListWidget.DragOnly)  # Только drag
        self.current_tasks_list.itemDoubleClicked.connect(self.rename_current_task)
        current_layout.addWidget(self.current_tasks_list)
    
        # Buttons layout
        buttons_layout = QHBoxLayout()
    
        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("cssClass", "secondary")
        delete_btn.clicked.connect(self.delete_current_task)
    
        rename_btn = QPushButton("Rename")
        rename_btn.setProperty("cssClass", "secondary")
        rename_btn.clicked.connect(self.rename_current_task)
    
        distribute_btn = QPushButton("Distribute All")
        distribute_btn.clicked.connect(self.distribute_all_tasks)
    
        buttons_layout.addWidget(delete_btn)
        buttons_layout.addWidget(rename_btn)
        buttons_layout.addWidget(distribute_btn)
    
        current_layout.addLayout(buttons_layout)
    
        layout.addWidget(current_group)
        return tab
        
    def create_all_tasks_tab(self):
        """Create the All Tasks tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # All Tasks section
        tasks_group = QGroupBox("All Tasks")
        tasks_layout = QVBoxLayout(tasks_group)
        
        self.tasks_list = CustomListWidget()
        self.tasks_list.setDragDropMode(QListWidget.DragOnly)
        self.tasks_list.itemDoubleClicked.connect(self.show_task_details)
        self.tasks_list.db = self.db
        tasks_layout.addWidget(self.tasks_list)
        
        task_buttons_layout = QHBoxLayout()
        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("cssClass", "secondary")
        delete_btn.clicked.connect(self.delete_task)
        rename_btn = QPushButton("Rename")
        rename_btn.setProperty("cssClass", "secondary")
        rename_btn.clicked.connect(self.rename_selected_task)
        
        task_buttons_layout.addWidget(delete_btn)
        task_buttons_layout.addWidget(rename_btn)
        tasks_layout.addLayout(task_buttons_layout)
        
        layout.addWidget(tasks_group)
        return tab
        
    def create_completed_tasks_tab(self):
        """Create the Completed Tasks tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Completed Tasks section
        completed_group = QGroupBox("Completed Tasks")
        completed_layout = QVBoxLayout(completed_group)
        
        self.completed_tasks_list = QListWidget()
        self.completed_tasks_list.itemDoubleClicked.connect(self.restore_completed_task)
        completed_layout.addWidget(self.completed_tasks_list)
        
        # Add delete button for completed tasks
        completed_buttons_layout = QHBoxLayout()
        delete_completed_btn = QPushButton("Delete Completed")
        delete_completed_btn.setProperty("cssClass", "secondary")
        delete_completed_btn.clicked.connect(self.delete_completed_task)
        completed_buttons_layout.addWidget(delete_completed_btn)
        completed_layout.addLayout(completed_buttons_layout)
        
        layout.addWidget(completed_group)
        return tab
        
    def create_center_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
    
        # Folder tabs
        self.folder_tabs = QTabWidget()
    
        # Folders tab
        folders_tab = QWidget()
        folders_layout = QVBoxLayout(folders_tab)
        folders_layout.setContentsMargins(5, 5, 5, 5)
        folders_layout.setSpacing(5)
    
        folder_buttons_layout = QHBoxLayout()
        create_folder_btn = QPushButton("New Folder")
        create_folder_btn.clicked.connect(self.create_folder)
        create_subfolder_btn = QPushButton("New Subfolder")
        create_subfolder_btn.setProperty("cssClass", "secondary")
        create_subfolder_btn.clicked.connect(self.create_subfolder)
        delete_folder_btn = QPushButton("Delete Folder")
        delete_folder_btn.setProperty("cssClass", "secondary")
        delete_folder_btn.clicked.connect(self.delete_folder)
    
        folder_buttons_layout.addWidget(create_folder_btn)
        folder_buttons_layout.addWidget(create_subfolder_btn)
        folder_buttons_layout.addWidget(delete_folder_btn)
        folders_layout.addLayout(folder_buttons_layout)
    
        # Add folder description button
        folder_desc_btn = QPushButton("Folder Description")
        folder_desc_btn.setProperty("cssClass", "secondary")
        folder_desc_btn.clicked.connect(self.show_folder_description)
        folders_layout.addWidget(folder_desc_btn)
    
        self.folders_tree = FolderTreeWidget()
        self.folders_tree.setDragDropMode(QListWidget.NoDragDrop)
        self.folders_tree.itemClicked.connect(self.on_folder_selected)
        folders_layout.addWidget(self.folders_tree)
    
        self.folder_tasks_label = QLabel("Select a folder to view tasks")
        folders_layout.addWidget(self.folder_tasks_label)
    
        folder_tasks_buttons_layout = QHBoxLayout()
        self.add_to_folder_btn = QPushButton("Add Task")
        self.add_to_folder_btn.setProperty("cssClass", "secondary")
        self.add_to_folder_btn.clicked.connect(self.add_selected_task_to_folder)
        self.add_to_folder_btn.setEnabled(False)
    
        self.remove_from_folder_btn = QPushButton("Remove Task")
        self.remove_from_folder_btn.setProperty("cssClass", "secondary")
        self.remove_from_folder_btn.clicked.connect(self.remove_selected_task_from_folder)
        self.remove_from_folder_btn.setEnabled(False)
    
        folder_tasks_buttons_layout.addWidget(self.add_to_folder_btn)
        folder_tasks_buttons_layout.addWidget(self.remove_from_folder_btn)
        folders_layout.addLayout(folder_tasks_buttons_layout)
    
        # Save Folder button
        save_folder_layout = QHBoxLayout()
        save_folder_btn = QPushButton("Save Folder")
        save_folder_btn.clicked.connect(self.save_folder_tasks)
        save_folder_layout.addWidget(save_folder_btn)
        folders_layout.addLayout(save_folder_layout)
    
        self.folder_tasks_list = DraggableListWidget()
        self.folder_tasks_list.setAcceptDrops(True)
        self.folder_tasks_list.setDragDropMode(QListWidget.DropOnly)  # Только drop

        # Подключаем обработчик drop
        self.folder_tasks_list.dropEvent = self.handle_folder_drop_event

        self.folder_tasks_list.itemSelectionChanged.connect(self.on_folder_task_selected)
        self.folder_tasks_list.itemDoubleClicked.connect(self.show_task_details)
        folders_layout.addWidget(self.folder_tasks_list)
    
        # Graph tab
        graph_tab = GraphView(self.db)  # This now uses the new tabbed version
    
        self.folder_tabs.addTab(folders_tab, "Folders")
        self.folder_tabs.addTab(graph_tab, "Graph View")
    
        layout.addWidget(self.folder_tabs)
    
        return panel
        
    def create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
    
        # Calendar section
        calendar_group = QGroupBox("Calendar")
        calendar_layout = QVBoxLayout(calendar_group)
    
        self.calendar = CustomCalendar(self.db)
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_selected)
        calendar_layout.addWidget(self.calendar)
    
        # Set tomorrow as default selected date
        tomorrow = QDate.currentDate().addDays(1)
        self.calendar.setSelectedDate(tomorrow)
        self.selected_date = tomorrow
        self.date_tasks_label = QLabel(f"Tasks for {tomorrow.toString('dd.MM.yyyy')}:")
        calendar_layout.addWidget(self.date_tasks_label)
    
        calendar_buttons_layout = QHBoxLayout()
        self.add_to_date_btn = QPushButton("Add Task")
        self.add_to_date_btn.setProperty("cssClass", "secondary")
        self.add_to_date_btn.clicked.connect(self.add_selected_task_to_date)
        self.add_to_date_btn.setEnabled(True)
    
        self.remove_from_date_btn = QPushButton("Remove Task")
        self.remove_from_date_btn.setProperty("cssClass", "secondary")
        self.remove_from_date_btn.clicked.connect(self.remove_selected_task_from_date)
        self.remove_from_date_btn.setEnabled(False)
    
        self.complete_task_btn = QPushButton("Complete")
        self.complete_task_btn.clicked.connect(self.mark_task_completed)
        self.complete_task_btn.setEnabled(False)
    
        calendar_buttons_layout.addWidget(self.add_to_date_btn)
        calendar_buttons_layout.addWidget(self.remove_from_date_btn)
        calendar_buttons_layout.addWidget(self.complete_task_btn)
        calendar_layout.addLayout(calendar_buttons_layout)
    
        # Save Date button
        save_date_layout = QHBoxLayout()
        save_date_btn = QPushButton("Save Date")
        save_date_btn.clicked.connect(self.save_date_tasks)
        save_date_layout.addWidget(save_date_btn)
        calendar_layout.addLayout(save_date_layout)
    
        self.date_tasks_list = DraggableListWidget()
        self.date_tasks_list.setAcceptDrops(True)
        self.date_tasks_list.setDragDropMode(QListWidget.DropOnly)  # Только drop

        # Подключаем обработчик drop
        self.date_tasks_list.dropEvent = self.handle_date_drop_event

        self.date_tasks_list.itemSelectionChanged.connect(self.on_date_task_selected)
        self.date_tasks_list.itemDoubleClicked.connect(self.show_task_details)
        calendar_layout.addWidget(self.date_tasks_list)
    
        layout.addWidget(calendar_group)
    
        return panel
        
    def setup_shortcuts(self):
        self.minimize_shortcut = QShortcut(QKeySequence("Alt+O"), self)
        self.minimize_shortcut.activated.connect(self.toggle_minimize)
        
        self.show_shortcut = QShortcut(QKeySequence("Alt+L"), self)
        self.show_shortcut.activated.connect(self.toggle_show)
        
    def toggle_minimize(self):
        if self.isMinimized():
            self.showNormal()
        else:
            self.showMinimized()
            
    def toggle_show(self):
        if self.isHidden():
            self.show()
        self.raise_()
        self.activateWindow()
            
    def load_data(self):
        self.load_current_tasks()
        self.load_tasks()
        self.load_folders_tree()
        self.load_completed_tasks()
        self.calendar.update_dates()
        self.show_date_tasks(self.selected_date.toString("yyyy-MM-dd"))
        self.select_first_folder()
            
    def select_first_folder(self):
        """Select the first folder in the folders tree"""
        if self.folders_tree.topLevelItemCount() > 0:
            first_item = self.folders_tree.topLevelItem(0)
            self.folders_tree.setCurrentItem(first_item)
            self.on_folder_selected(first_item)
            
    def add_current_task(self):
        """Add task to Current Tasks (temporary)"""
        task_text = self.current_task_input.text().strip()
        if task_text:
            item = QListWidgetItem(f"📌 {task_text}")
            self.current_tasks_list.addItem(item)
            self.current_task_input.clear()
            self.current_task_input.setFocus()
            
    def delete_current_task(self):
        """Delete task from Current Tasks"""
        current_item = self.current_tasks_list.currentItem()
        if current_item:
            self.current_tasks_list.takeItem(self.current_tasks_list.row(current_item))
            
    def rename_current_task(self):
        """Rename task in Current Tasks"""
        current_item = self.current_tasks_list.currentItem()
        if current_item:
            old_text = current_item.text().replace("📌 ", "")
            new_text, ok = QInputDialog.getText(self, 'Rename Task', 'Enter new task text:', text=old_text)
            if ok and new_text and new_text != old_text:
                current_item.setText(f"📌 {new_text}")
                
    def distribute_all_tasks(self):
        """Distribute all current tasks to All Tasks (unassigned)"""
        if self.current_tasks_list.count() == 0:
            self.show_auto_message("No tasks to distribute!")
            return
        
        task_count = 0
        for i in range(self.current_tasks_list.count()):
            item = self.current_tasks_list.item(0)  # Always take first item
            task_text = item.text().replace("📌 ", "")
            
            # Add to database as single task
            task_id = self.db.add_task(task_text, "", "single")
            task_count += 1
            
            # Remove from current tasks
            self.current_tasks_list.takeItem(0)
    
        # Reload All Tasks
        self.load_tasks()
    
        self.show_auto_message(f"{task_count} tasks distributed to All Tasks!")
            
    def delete_task(self):
        """Delete task from All Tasks"""
        current_item = self.tasks_list.currentItem()
        if current_item:
            task_id = current_item.data(Qt.UserRole)
            reply = QMessageBox.question(self, 'Delete Task', 
                                       'Are you sure you want to delete this task?',
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.db.delete_task(task_id)
                self.tasks_list.takeItem(self.tasks_list.row(current_item))
                self.show_auto_message("Task deleted!")
            
    def restore_completed_task(self, item):
        """Restore task from completed"""
        task_id = item.data(Qt.UserRole)
        task_text = item.data(Qt.UserRole + 1)
        task_description = item.data(Qt.UserRole + 2)
        task_type = item.data(Qt.UserRole + 3)
        
        try:
            self.db.restore_task_from_completed(task_id, task_text, task_description, task_type)
            self.add_task_to_list(self.tasks_list, task_id, task_text, task_type)
            self.completed_tasks_list.takeItem(self.completed_tasks_list.row(item))
            self.show_auto_message("Task restored from completed!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to restore task: {str(e)}")
            
    def delete_completed_task(self):
        """Delete completed task permanently"""
        current_item = self.completed_tasks_list.currentItem()
        if current_item and current_item.data(Qt.UserRole):
            task_id = current_item.data(Qt.UserRole)
            reply = QMessageBox.question(self, 'Delete Completed Task', 
                                       'Are you sure you want to permanently delete this completed task?',
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.db.delete_completed_task(task_id)
                self.load_completed_tasks()
                self.show_auto_message("Completed task deleted permanently!")
            
    def rename_selected_task(self):
        """Rename selected task in All Tasks"""
        current_item = self.tasks_list.currentItem()
        if current_item:
            self.rename_task(current_item)
            
    def rename_task(self, item):
        """Rename task in database"""
        old_text = item.text()
        if old_text.startswith("📌 "):
            old_text = old_text.replace("📌 ", "")
        elif old_text.startswith("🔄 "):
            old_text = old_text.replace("🔄 ", "")
            
        new_text, ok = QInputDialog.getText(self, 'Rename Task', 'Enter new task text:', text=old_text)
        if ok and new_text and new_text != old_text:
            task_id = item.data(Qt.UserRole)
            task_type = item.data(Qt.UserRole + 1)
            self.db.update_task(task_id, new_text)
            
            # Update display
            if task_type == 'single':
                item.setText(f"📌 {new_text}")
            else:
                item.setText(f"🔄 {new_text}")
            
    def show_task_details(self, item):
        """Show task details dialog"""
        task_id = item.data(Qt.UserRole)
        tasks = self.db.get_all_tasks()
        description = ""
        for tid, text, desc, task_type in tasks:
            if tid == task_id:
                description = desc
                break
        
        dialog = DescriptionDialog(item.text(), description, task_id, self.db, self)
        dialog.exec_()
        self.load_data()
            
    def show_folder_description(self):
        """Show folder description dialog"""
        current_item = self.folders_tree.currentItem()
        if not current_item:
            self.show_auto_message("Please select a folder first")
            return
            
        folder_id = current_item.data(0, Qt.UserRole)
        folder_name = current_item.text(0)
        description = self.db.get_folder_description(folder_id)
        
        dialog = FolderDescriptionDialog(folder_name, description, folder_id, self.db, self)
        dialog.exec_()
            
    def create_folder(self):
        """Create new folder"""
        folder_name, ok = QInputDialog.getText(self, 'Create Folder', 'Enter folder name:')
        if ok and folder_name:
            folder_id = self.db.add_folder(folder_name)
            self.load_folders_tree()
            self.select_first_folder()
            
    def create_subfolder(self):
        """Create subfolder"""
        current_item = self.folders_tree.currentItem()
        if not current_item:
            self.show_auto_message("Please select a parent folder first")
            return
            
        parent_id = current_item.data(0, Qt.UserRole)
        folder_name, ok = QInputDialog.getText(self, 'Create Subfolder', 'Enter subfolder name:')
        if ok and folder_name:
            folder_id = self.db.add_folder(folder_name, parent_id)
            self.load_folders_tree()
            
    def delete_folder(self):
        """Delete folder"""
        current_item = self.folders_tree.currentItem()
        if not current_item:
            self.show_auto_message("Please select a folder to delete")
            return
            
        folder_id = current_item.data(0, Qt.UserRole)
        folder_name = current_item.text(0)
        
        reply = QMessageBox.question(self, 'Delete Folder', 
                                   f'Are you sure you want to delete folder "{folder_name}" and all its contents?',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_folder(folder_id)
                self.load_folders_tree()
                self.select_first_folder()
                self.show_auto_message("Folder deleted successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete folder: {str(e)}")
            
    def load_current_tasks(self):
        """Load current tasks - temporary storage"""
        self.current_tasks_list.clear()
        # Current tasks are stored temporarily in the UI, not in database
        
    def load_folders_tree(self):
        """Load folders tree"""
        self.folders_tree.clear()
        
        def add_folders_to_tree(parent_item, parent_id=0):
            folders = self.db.get_subfolders(parent_id)
            for folder_id, folder_name, folder_parent_id in folders:
                folder_item = QTreeWidgetItem(parent_item, [folder_name])
                folder_item.setData(0, Qt.UserRole, folder_id)
                add_folders_to_tree(folder_item, folder_id)
        
        add_folders_to_tree(self.folders_tree)
        self.folders_tree.expandAll()
            
    def on_folder_selected(self, item):
        """Handle folder selection"""
        folder_id = item.data(0, Qt.UserRole)
        folder_name = item.text(0)
        self.current_folder_id = folder_id
        self.folder_tasks_label.setText(f"Tasks in folder '{folder_name}':")
        self.add_to_folder_btn.setEnabled(True)
        self.show_folder_tasks(folder_id)
            
    def on_folder_task_selected(self):
        """Handle folder task selection"""
        self.remove_from_folder_btn.setEnabled(bool(self.folder_tasks_list.currentItem()))
            
    def show_folder_tasks(self, folder_id):
        """Show tasks in selected folder"""
        self.folder_tasks_list.clear()
        tasks = self.db.get_tasks_in_folder(folder_id)
        for task_id, task_text, description, task_type in tasks:
            item = self.add_task_to_list(self.folder_tasks_list, task_id, task_text, task_type)
            
    def add_selected_task_to_folder(self):
        """Add selected task to current folder - CORRECTED VERSION (COPY)"""
        if not self.current_folder_id:
            self.show_auto_message("No folder selected")
            return
            
        # Get task from current selection
        current_task_item = None
        current_tab_index = self.left_tabs.currentIndex()
        
        if current_tab_index == 0:  # Current Tasks tab
            current_task_item = self.current_tasks_list.currentItem()
            if current_task_item:
                # Create COPY of task in database (original stays in Current Tasks)
                task_text = current_task_item.text().replace("📌 ", "")
                task_id = self.db.add_task(task_text, "", "single")
                task_type = "single"
                
                # Add to folder tasks list (COPY)
                item = self.add_task_to_list(self.folder_tasks_list, task_id, task_text, task_type)
                
                # Update All Tasks
                self.load_tasks()
                
                self.show_auto_message("Task copied to folder! Click 'Save Folder' to save changes.")
                return
                
        elif current_tab_index == 1:  # All Tasks tab
            current_task_item = self.tasks_list.currentItem()
            if current_task_item:
                task_id = current_task_item.data(Qt.UserRole)
                task_text = current_task_item.text()
                if task_text.startswith("📌 "):
                    task_text = task_text.replace("📌 ", "")
                elif task_text.startswith("🔄 "):
                    task_text = task_text.replace("🔄 ", "")
                task_type = current_task_item.data(Qt.UserRole + 1)
                
                # Add to folder tasks list (original task from All Tasks)
                item = self.add_task_to_list(self.folder_tasks_list, task_id, task_text, task_type)
                self.show_auto_message("Task added to folder! Click 'Save Folder' to save changes.")
                return
        
        if not current_task_item:
            self.show_auto_message("No task selected")
            return
        
    def remove_selected_task_from_folder(self):
        """Remove selected task from current folder"""
        if not self.current_folder_id:
            return
            
        current_item = self.folder_tasks_list.currentItem()
        if current_item:
            task_id = current_item.data(Qt.UserRole)
            self.db.remove_task_from_folder(task_id, self.current_folder_id)
            self.folder_tasks_list.takeItem(self.folder_tasks_list.row(current_item))
            self.show_auto_message("Task removed from folder! Click 'Save Folder' to save changes.")
    
    def save_folder_tasks(self):
        """Save folder tasks to database"""
        if not self.current_folder_id:
            self.show_auto_message("No folder selected")
            return
            
        folder_task_ids = []
        for i in range(self.folder_tasks_list.count()):
            item = self.folder_tasks_list.item(i)
            folder_task_ids.append(item.data(Qt.UserRole))
        
        try:
            # Save to database - this will create the folder-task relationships
            self.db.save_folder_tasks(self.current_folder_id, folder_task_ids)
            
            # Update All Tasks to reflect new status
            self.load_tasks()
            
            self.show_auto_message("Folder tasks saved successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save folder tasks: {str(e)}")
            
    def handle_folder_drop_event(self, event):
            """Handle drop event for folder tasks list - UPDATED"""
            source = event.source()
    
            if source == self.current_tasks_list:
                # Get the dragged item
                items = source.selectedItems()
                if not items:
                    return
        
                dragged_item = items[0]
    
                # Task from Current Tasks - create COPY in database
                task_text = dragged_item.text().replace("📌 ", "")
                task_id = self.db.add_task(task_text, "", "single")
    
                # Add COPY to folder tasks list (original stays in Current Tasks)
                item = self.add_task_to_list(self.folder_tasks_list, task_id, task_text, "single")
    
                # Update All Tasks
                self.load_tasks()
    
                self.show_auto_message("Task copied to folder! Click 'Save Folder' to save.")
    
            elif source == self.tasks_list:
                # Get the dragged item from All Tasks
                items = source.selectedItems()
                if not items:
                    return
        
                dragged_item = items[0]
                task_id = dragged_item.data(Qt.UserRole)
                task_text = dragged_item.text()
                if task_text.startswith("📌 "):
                    task_text = task_text.replace("📌 ", "")
                elif task_text.startswith("🔄 "):
                    task_text = task_text.replace("🔄 ", "")
                task_type = dragged_item.data(Qt.UserRole + 1)
        
                # Add original task to folder tasks list
                item = self.add_task_to_list(self.folder_tasks_list, task_id, task_text, task_type)
        
                self.show_auto_message("Task added to folder! Click 'Save Folder' to save.")
    
            event.acceptProposedAction()
            
    def on_date_selected(self, date):
        """Handle date selection"""
        self.selected_date = date
        date_str = date.toString("yyyy-MM-dd")
        self.date_tasks_label.setText(f"Tasks for {date.toString('dd.MM.yyyy')}:")
        self.add_to_date_btn.setEnabled(True)
        self.show_date_tasks(date_str)
            
    def on_date_task_selected(self):
        """Handle date task selection"""
        has_selection = bool(self.date_tasks_list.currentItem())
        self.remove_from_date_btn.setEnabled(has_selection)
        self.complete_task_btn.setEnabled(has_selection)
            
    def show_date_tasks(self, date_str):
        """Show tasks for selected date"""
        self.date_tasks_list.clear()
        
        # Load tasks from database
        tasks = self.db.get_tasks_by_date(date_str)
    
        for task_id, task_text, description, task_type, completed in tasks:
            item = self.add_task_to_list(self.date_tasks_list, task_id, task_text, task_type)
            if completed:
                item.setBackground(QColor(76, 175, 80, 180))
                item.setForeground(QColor(220, 220, 220))
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)
            else:
                item.setBackground(QColor(255, 193, 7))
                item.setForeground(QColor(0, 0, 0))
                font = item.font()
                font.setStrikeOut(False)
                item.setFont(font)
                
    def handle_date_drop_event(self, event):
        """Handle drop event for date tasks list - UPDATED"""
        source = event.source()
    
        if source == self.current_tasks_list:
            # Get the dragged item
            items = source.selectedItems()
            if not items:
                return
        
            dragged_item = items[0]
            date_str = self.selected_date.toString("yyyy-MM-dd")
    
            # Task from Current Tasks - create COPY in database
            task_text = dragged_item.text().replace("📌 ", "")
            task_id = self.db.add_task(task_text, "", "single")
    
            # Add COPY to calendar (original stays in Current Tasks)
            self.db.add_task_to_calendar(task_id, date_str)
    
            # Update All Tasks
            self.load_tasks()
    
            # Reload date tasks
            self.show_date_tasks(date_str)
    
            # Update calendar
            self.calendar.update_dates()
    
            self.show_auto_message("Task copied to date!")
    
        elif source == self.tasks_list:
            # Get the dragged item from All Tasks
            items = source.selectedItems()
            if not items:
                return
        
            dragged_item = items[0]
            task_id = dragged_item.data(Qt.UserRole)
            date_str = self.selected_date.toString("yyyy-MM-dd")
        
            # Add original task to calendar
            self.db.add_task_to_calendar(task_id, date_str)
        
            # Update All Tasks
            self.load_tasks()
        
            # Reload date tasks
            self.show_date_tasks(date_str)
        
            # Update calendar
            self.calendar.update_dates()
        
            self.show_auto_message("Task added to date!")
    
        event.acceptProposedAction()
                
    def add_selected_task_to_date(self):
        """Add selected task to current date - COPY LOGIC"""
        if not self.selected_date:
            self.show_auto_message("No date selected")
            return
    
        current_task_item = None
        current_tab_index = self.left_tabs.currentIndex()

        if current_tab_index == 0:  # Current Tasks tab
            current_task_item = self.current_tasks_list.currentItem()
        elif current_tab_index == 1:  # All Tasks tab
            current_task_item = self.tasks_list.currentItem()

        if not current_task_item:
            self.show_auto_message("No task selected")
            return
    
        date_str = self.selected_date.toString("yyyy-MM-dd")
    
        if current_tab_index == 0:  # Current Tasks
            task_text = current_task_item.text().replace("📌 ", "")
        
            # Create COPY of task and add to calendar (original stays in Current Tasks)
            task_id = self.db.add_task(task_text, "", "single")
            self.db.add_task_to_calendar(task_id, date_str)
        
            self.show_auto_message("Task copied to date!")
        
        else:  # All Tasks
            task_id = current_task_item.data(Qt.UserRole)
            self.db.add_task_to_calendar(task_id, date_str)
            
            self.show_auto_message("Task added to date!")

        # Update All Tasks
        self.load_tasks()
        
        # Reload date tasks
        self.show_date_tasks(date_str)
    
        # Update calendar
        self.calendar.update_dates()
            
    def remove_selected_task_from_date(self):
        """Remove selected task from current date"""
        if not self.selected_date:
            return
        
        current_item = self.date_tasks_list.currentItem()
        if current_item:
            task_id = current_item.data(Qt.UserRole)
            date_str = self.selected_date.toString("yyyy-MM-dd")
        
            # Remove from database
            self.db.remove_task_from_date(task_id, date_str)
        
            # Remove from UI list
            self.date_tasks_list.takeItem(self.date_tasks_list.row(current_item))
        
            # Update calendar
            self.calendar.update_dates()
        
            self.show_auto_message("Task removed from date!")
            
    def save_date_tasks(self):
        """Save date tasks to database"""
        if not self.selected_date:
            self.show_auto_message("No date selected")
            return
            
        date_str = self.selected_date.toString("yyyy-MM-dd")
        
        # Get current task IDs from UI
        current_task_ids = []
        for i in range(self.date_tasks_list.count()):
            item = self.date_tasks_list.item(i)
            current_task_ids.append(item.data(Qt.UserRole))
        
        try:
            # Save to database
            self.db.save_date_tasks(date_str, current_task_ids)
            
            # Update calendar
            self.calendar.update_dates()
            
            self.show_auto_message("Date tasks saved successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save date tasks: {str(e)}")
            
    def mark_task_completed(self):
        """Mark task as completed"""
        if not self.selected_date:
            return
        
        current_item = self.date_tasks_list.currentItem()
        if current_item:
            task_id = current_item.data(Qt.UserRole)
            date_str = self.selected_date.toString("yyyy-MM-dd")
        
            try:
                # Mark as completed in database
                self.db.mark_task_completed(task_id, date_str)
            
                # Remove from date tasks list
                self.date_tasks_list.takeItem(self.date_tasks_list.row(current_item))
            
                # Update All Tasks
                self.load_tasks()
            
                # Update folder tasks list
                if self.current_folder_id:
                    self.show_folder_tasks(self.current_folder_id)
            
                # Reload completed tasks
                self.load_completed_tasks()
            
                # Update calendar
                self.calendar.update_dates()
            
                self.show_auto_message("Task marked as completed!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to mark task as completed: {str(e)}")
            
    def load_completed_tasks(self):
        """Load completed tasks"""
        self.completed_tasks_list.clear()
        completed_tasks = self.db.get_completed_tasks()
        
        current_date = ""
        for task_id, task_text, task_description, task_type, completed_date in completed_tasks:
            if completed_date != current_date:
                current_date = completed_date
                date_item = QListWidgetItem(f"{{{completed_date}}}")
                date_item.setBackground(QColor(66, 66, 66))
                date_item.setFlags(date_item.flags() & ~Qt.ItemIsSelectable)
                self.completed_tasks_list.addItem(date_item)
            
            task_item = QListWidgetItem(f"  {task_text}")
            task_item.setData(Qt.UserRole, task_id)
            task_item.setData(Qt.UserRole + 1, task_text)
            task_item.setData(Qt.UserRole + 2, task_description)
            task_item.setData(Qt.UserRole + 3, task_type)
            task_item.setBackground(QColor(76, 175, 80))
            self.completed_tasks_list.addItem(task_item)
            
    def load_tasks(self):
        """Load all tasks"""
        self.tasks_list.clear()
        tasks = self.db.get_all_tasks()
        for task_id, task_text, description, task_type in tasks:
            item = self.add_task_to_list(self.tasks_list, task_id, task_text, task_type)
            
    def add_task_to_list(self, list_widget, task_id, task_text, task_type):
        """Add task to list widget with appropriate formatting"""
        item = QListWidgetItem()
        item.setData(Qt.UserRole, task_id)
        item.setData(Qt.UserRole + 1, task_type)
        
        if task_type == 'single':
            item.setText(f"📌 {task_text}")
        else:
            item.setText(f"🔄 {task_text}")
            
        list_widget.addItem(item)
        return item

    def show_auto_message(self, message):
        """Show auto-closing message"""
        msg = AutoCloseMessageBox(message, self)
        msg.exec_()