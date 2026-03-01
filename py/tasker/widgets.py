# widgets.py
from PyQt5.QtWidgets import (QListWidget, QTreeWidget, QCalendarWidget, 
                             QWidget, QDialog, QVBoxLayout, QLabel, QTreeWidgetItem,
                             QPushButton, QHBoxLayout, QMessageBox, QListWidgetItem,
                             QComboBox, QTabWidget)
from PyQt5.QtCore import Qt, QDate, QTimer, QPoint, QPointF
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QMouseEvent, QPainterPath
import math
from datetime import datetime, timedelta

from utils import AutoCloseMessageBox


class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setDefaultDropAction(Qt.CopyAction)


class FolderTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("Folders")
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setDropIndicatorShown(False)


class GraphTabWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Tab 1: Folder Tasks
        self.folder_graph = FolderGraphView(self.db)
        self.tab_widget.addTab(self.folder_graph, "Folder Tasks")
        
        # Tab 2: Unassigned Tasks
        self.unassigned_graph = UnassignedGraphView(self.db)
        self.tab_widget.addTab(self.unassigned_graph, "Unassigned Tasks")
        
        # Tab 3: Calendar Tasks
        self.calendar_graph = CalendarGraphView(self.db)
        self.tab_widget.addTab(self.calendar_graph, "Calendar Tasks")
        
        layout.addWidget(self.tab_widget)


class FolderGraphView(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.nodes = []
        self.edges = []
        self.scale = 1.0
        self.offset = QPointF(0, 0)
        self.last_mouse_pos = QPoint()
        self.dragging = False
        self.setMinimumSize(800, 600)
        self.init_ui()
        
    def init_ui(self):
        self.zoom_in_btn = QPushButton("+", self)
        self.zoom_out_btn = QPushButton("-", self)
        self.zoom_in_btn.setFixedSize(30, 30)
        self.zoom_out_btn.setFixedSize(30, 30)
        self.zoom_in_btn.move(10, 10)
        self.zoom_out_btn.move(10, 50)
        
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        
        self.reset_btn = QPushButton("Reset", self)
        self.reset_btn.setFixedSize(50, 30)
        self.reset_btn.move(10, 90)
        self.reset_btn.clicked.connect(self.reset_view)
        
    def zoom_in(self):
        self.scale *= 1.2
        self.update()
        
    def zoom_out(self):
        self.scale /= 1.2
        self.update()
        
    def reset_view(self):
        self.scale = 1.0
        self.offset = QPointF(0, 0)
        self.update()
        
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()
            self.dragging = True
            
            pos = self.mapToScene(event.pos())
            for node in self.nodes:
                node_pos = QPointF(node["x"], node["y"])
                distance = math.sqrt((pos.x() - node_pos.x())**2 + (pos.y() - node_pos.y())**2)
                
                radius = 25 if node["type"] == "root" else 20 if node["type"] == "folder" else 15
                if distance <= radius * self.scale:
                    self.on_node_clicked(node)
                    break
                    
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.last_mouse_pos
            self.offset += QPointF(delta.x() / self.scale, delta.y() / self.scale)
            self.last_mouse_pos = event.pos()
            self.update()
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
        super().mouseReleaseEvent(event)
        
    def mapToScene(self, point):
        return QPointF(
            (point.x() - self.width() / 2) / self.scale - self.offset.x(),
            (point.y() - self.height() / 2) / self.scale - self.offset.y()
        )
        
    def on_node_clicked(self, node):
        if node["type"] == "folder":
            self.show_folder_contents(node["id"])
        elif node["type"] == "task":
            self.show_task_details(node["id"])
            
    def show_folder_contents(self, folder_id):
        folder_id = int(folder_id.replace("folder_", ""))
        tasks = self.db.get_tasks_in_folder(folder_id)
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Folder Contents")
        dialog.setGeometry(300, 300, 400, 300)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QListWidget {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #3e3e42;
            }
            QPushButton {
                background-color: #0e639c;
                color: #ffffff;
                border: 1px solid #007acc;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout()
        list_widget = QListWidget()
        
        if tasks:
            for task_id, task_text, description, task_type in tasks:
                item_text = f"📌 {task_text}" if task_type == 'single' else f"🔄 {task_text}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, task_id)
                list_widget.addItem(item)
        else:
            list_widget.addItem("No tasks in this folder")
            
        layout.addWidget(list_widget)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()
        
    def show_task_details(self, task_id):
        task_id = int(task_id.replace("task_", ""))
        tasks = self.db.get_all_tasks()
        description = ""
        task_text = ""
        
        for tid, text, desc, task_type in tasks:
            if tid == task_id:
                description = desc
                task_text = text
                break
        
        from dialogs import DescriptionDialog
        dialog = DescriptionDialog(task_text, description, task_id, self.db, self)
        dialog.exec_()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(30, 30, 30))
        
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(self.scale, self.scale)
        painter.translate(self.offset.x(), self.offset.y())
        
        # Generate graph data
        self.generate_graph_data()
        
        if not self.nodes:
            painter.setPen(QColor(102, 102, 102))
            painter.setFont(QFont("Segoe UI", 12))
            painter.drawText(-100, 0, "No folder tasks to display")
            return
        
        # Draw edges
        painter.setPen(QPen(QColor(86, 156, 214, 180), 1.5))
        for start_id, end_id in self.edges:
            start_node = next((n for n in self.nodes if n["id"] == start_id), None)
            end_node = next((n for n in self.nodes if n["id"] == end_id), None)
            
            if start_node and end_node:
                painter.drawLine(int(start_node["x"]), int(start_node["y"]), 
                               int(end_node["x"]), int(end_node["y"]))
        
        # Draw nodes
        for node in self.nodes:
            if node["type"] == "root":
                color = QColor(0, 122, 204)
                radius = 25
            elif node["type"] == "folder":
                color = QColor(86, 156, 214)
                radius = 20
            else:  # task
                color = QColor(78, 201, 176)
                radius = 15
            
            painter.setBrush(color)
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.drawEllipse(int(node["x"] - radius), int(node["y"] - radius), 
                              radius * 2, radius * 2)
            
            painter.setPen(QColor(255, 255, 255))
            font = QFont("Segoe UI", 9 if node["type"] == "task" else 10)
            font.setBold(node["type"] != "task")
            painter.setFont(font)
            
            text = node["text"]
            text_rect = painter.boundingRect(0, 0, 200, 50, Qt.AlignCenter, text)
            painter.drawText(int(node["x"] - 100), int(node["y"] + radius + 20), 200, 50, 
                           Qt.AlignCenter | Qt.TextWordWrap, text)
    
    def generate_graph_data(self):
        self.nodes.clear()
        self.edges.clear()
        
        root_node = {"id": "root", "text": "FOLDER TASKS", "x": 0, "y": 0, "type": "root"}
        self.nodes.append(root_node)
        
        folders = self.db.get_all_folders()
        folder_tasks = []
        
        # Get all tasks that are in folders
        for folder_id, folder_name, parent_id in folders:
            tasks = self.db.get_tasks_in_folder(folder_id)
            folder_tasks.extend([(task_id, task_text, folder_id) for task_id, task_text, _, _ in tasks])
        
        if folder_tasks:
            angle_step = 2 * math.pi / len(folder_tasks)
            radius = 200
            
            for i, (task_id, task_text, folder_id) in enumerate(folder_tasks):
                angle = i * angle_step
                random_offset = (hash(task_text) % 20 - 10) / 50.0
                x = radius * math.cos(angle + random_offset)
                y = radius * math.sin(angle + random_offset)
                
                task_node = {"id": f"task_{task_id}", "text": task_text,
                           "x": x, "y": y, "type": "task"}
                self.nodes.append(task_node)
                self.edges.append(("root", f"task_{task_id}"))


class UnassignedGraphView(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.nodes = []
        self.edges = []
        self.scale = 1.0
        self.offset = QPointF(0, 0)
        self.last_mouse_pos = QPoint()
        self.dragging = False
        self.setMinimumSize(800, 600)
        self.init_ui()
        
    def init_ui(self):
        self.zoom_in_btn = QPushButton("+", self)
        self.zoom_out_btn = QPushButton("-", self)
        self.zoom_in_btn.setFixedSize(30, 30)
        self.zoom_out_btn.setFixedSize(30, 30)
        self.zoom_in_btn.move(10, 10)
        self.zoom_out_btn.move(10, 50)
        
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        
        self.reset_btn = QPushButton("Reset", self)
        self.reset_btn.setFixedSize(50, 30)
        self.reset_btn.move(10, 90)
        self.reset_btn.clicked.connect(self.reset_view)
    
    def zoom_in(self):
        self.scale *= 1.2
        self.update()
        
    def zoom_out(self):
        self.scale /= 1.2
        self.update()
        
    def reset_view(self):
        self.scale = 1.0
        self.offset = QPointF(0, 0)
        self.update()
        
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()
            self.dragging = True
            
            pos = self.mapToScene(event.pos())
            for node in self.nodes:
                node_pos = QPointF(node["x"], node["y"])
                distance = math.sqrt((pos.x() - node_pos.x())**2 + (pos.y() - node_pos.y())**2)
                
                radius = 25 if node["type"] == "root" else 15
                if distance <= radius * self.scale:
                    self.on_node_clicked(node)
                    break
                    
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.last_mouse_pos
            self.offset += QPointF(delta.x() / self.scale, delta.y() / self.scale)
            self.last_mouse_pos = event.pos()
            self.update()
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
        super().mouseReleaseEvent(event)
    
    def mapToScene(self, point):
        return QPointF(
            (point.x() - self.width() / 2) / self.scale - self.offset.x(),
            (point.y() - self.height() / 2) / self.scale - self.offset.y()
        )
    
    def on_node_clicked(self, node):
        self.show_task_details(node["id"])
        
    def show_task_details(self, task_id):
        task_id = int(task_id.replace("task_", ""))
        tasks = self.db.get_all_tasks()
        description = ""
        task_text = ""
        
        for tid, text, desc, task_type in tasks:
            if tid == task_id:
                description = desc
                task_text = text
                break
        
        from dialogs import DescriptionDialog
        dialog = DescriptionDialog(task_text, description, task_id, self.db, self)
        dialog.exec_()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(30, 30, 30))
        
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(self.scale, self.scale)
        painter.translate(self.offset.x(), self.offset.y())
        
        # Generate graph data
        self.generate_graph_data()
        
        if not self.nodes:
            painter.setPen(QColor(102, 102, 102))
            painter.setFont(QFont("Segoe UI", 12))
            painter.drawText(-100, 0, "No unassigned tasks to display")
            return
        
        # Draw edges
        painter.setPen(QPen(QColor(255, 193, 7, 180), 1.5))
        for start_id, end_id in self.edges:
            start_node = next((n for n in self.nodes if n["id"] == start_id), None)
            end_node = next((n for n in self.nodes if n["id"] == end_id), None)
            
            if start_node and end_node:
                painter.drawLine(int(start_node["x"]), int(start_node["y"]), 
                               int(end_node["x"]), int(end_node["y"]))
        
        # Draw nodes
        for node in self.nodes:
            if node["type"] == "root":
                color = QColor(255, 193, 7)
                radius = 25
            else:  # task
                color = QColor(255, 213, 79)
                radius = 15
            
            painter.setBrush(color)
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.drawEllipse(int(node["x"] - radius), int(node["y"] - radius), 
                              radius * 2, radius * 2)
            
            painter.setPen(QColor(255, 255, 255))
            font = QFont("Segoe UI", 9 if node["type"] == "task" else 10)
            font.setBold(node["type"] != "task")
            painter.setFont(font)
            
            text = node["text"]
            text_rect = painter.boundingRect(0, 0, 200, 50, Qt.AlignCenter, text)
            painter.drawText(int(node["x"] - 100), int(node["y"] + radius + 20), 200, 50, 
                           Qt.AlignCenter | Qt.TextWordWrap, text)
    
    def generate_graph_data(self):
        self.nodes.clear()
        self.edges.clear()
        
        root_node = {"id": "root", "text": "UNASSIGNED TASKS", "x": 0, "y": 0, "type": "root"}
        self.nodes.append(root_node)
        
        # Get tasks without folders and not in calendar
        unassigned_tasks = self.db.get_unassigned_tasks()
        
        if unassigned_tasks:
            angle_step = 2 * math.pi / len(unassigned_tasks)
            radius = 200
            
            for i, (task_id, task_text, description, task_type) in enumerate(unassigned_tasks):
                angle = i * angle_step
                random_offset = (hash(task_text) % 20 - 10) / 50.0
                x = radius * math.cos(angle + random_offset)
                y = radius * math.sin(angle + random_offset)
                
                task_node = {"id": f"task_{task_id}", "text": task_text,
                           "x": x, "y": y, "type": "task"}
                self.nodes.append(task_node)
                self.edges.append(("root", f"task_{task_id}"))


class CalendarGraphView(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.nodes = []
        self.edges = []
        self.scale = 2.0  # Увеличиваем начальный масштаб
        self.offset = QPointF(0, 0)
        self.last_mouse_pos = QPoint()
        self.dragging = False
        self.setMinimumSize(800, 600)
        self.init_ui()
        
    def init_ui(self):
        self.zoom_in_btn = QPushButton("+", self)
        self.zoom_out_btn = QPushButton("-", self)
        self.zoom_in_btn.setFixedSize(30, 30)
        self.zoom_out_btn.setFixedSize(30, 30)
        self.zoom_in_btn.move(10, 10)
        self.zoom_out_btn.move(10, 50)
        
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        
        self.reset_btn = QPushButton("Reset", self)
        self.reset_btn.setFixedSize(50, 30)
        self.reset_btn.move(10, 90)
        self.reset_btn.clicked.connect(self.reset_view)
        
        # Кнопка для центрирования на сегодняшней дате
        self.today_btn = QPushButton("Today", self)
        self.today_btn.setFixedSize(50, 30)
        self.today_btn.move(10, 130)
        self.today_btn.clicked.connect(self.center_on_today)
    
    def center_on_today(self):
        """Центрировать вид на сегодняшней дате"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        dates = self.get_date_range()
        
        if today_str in dates:
            today_index = dates.index(today_str)
            total_dates = len(dates)
            date_spacing = self.calculate_date_spacing(dates)
            timeline_width = total_dates * date_spacing
            today_x = -timeline_width / 2 + today_index * date_spacing
            
            # Центрируем на сегодняшней дате
            self.offset = QPointF(-today_x, 0)
            self.update()
    
    def zoom_in(self):
        self.scale *= 1.2
        self.update()
        
    def zoom_out(self):
        self.scale /= 1.2
        self.update()
        
    def reset_view(self):
        self.scale = 2.0
        self.offset = QPointF(0, 0)
        self.update()
        
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()
            self.dragging = True
            
            pos = self.mapToScene(event.pos())
            for node in self.nodes:
                node_pos = QPointF(node["x"], node["y"])
                distance = math.sqrt((pos.x() - node_pos.x())**2 + (pos.y() - node_pos.y())**2)
                
                radius = 20 if node["type"] == "date" else 15
                if distance <= radius * self.scale:
                    self.on_node_clicked(node)
                    break
                    
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.last_mouse_pos
            self.offset += QPointF(delta.x() / self.scale, delta.y() / self.scale)
            self.last_mouse_pos = event.pos()
            self.update()
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
        super().mouseReleaseEvent(event)
    
    def mapToScene(self, point):
        return QPointF(
            (point.x() - self.width() / 2) / self.scale - self.offset.x(),
            (point.y() - self.height() / 2) / self.scale - self.offset.y()
        )
    
    def on_node_clicked(self, node):
        if node["type"] == "date":
            self.show_date_contents(node["id"])
        elif node["type"] == "task":
            self.show_task_details(node["id"])
        
    def show_date_contents(self, date_str):
        tasks = self.db.get_tasks_by_date(date_str)
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Tasks for {date_str}")
        dialog.setGeometry(300, 300, 400, 300)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QListWidget {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #3e3e42;
            }
            QPushButton {
                background-color: #0e639c;
                color: #ffffff;
                border: 1px solid #007acc;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout()
        list_widget = QListWidget()
        
        if tasks:
            for task_id, task_text, description, task_type, completed in tasks:
                item_text = f"📌 {task_text}" if task_type == 'single' else f"🔄 {task_text}"
                if completed:
                    item_text = f"✓ {item_text}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, task_id)
                list_widget.addItem(item)
        else:
            list_widget.addItem("No tasks for this date")
            
        layout.addWidget(list_widget)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()
        
    def show_task_details(self, task_id):
        task_id = int(task_id.replace("task_", ""))
        tasks = self.db.get_all_tasks()
        description = ""
        task_text = ""
        
        for tid, text, desc, task_type in tasks:
            if tid == task_id:
                description = desc
                task_text = text
                break
        
        from dialogs import DescriptionDialog
        dialog = DescriptionDialog(task_text, description, task_id, self.db, self)
        dialog.exec_()
    
    def get_date_range(self):
        """Получить диапазон дат: 10 дней назад и 10 дней вперед от сегодня"""
        today = datetime.now()
        date_range = []
        
        # 10 дней назад
        for i in range(10, 0, -1):
            date = today - timedelta(days=i)
            date_range.append(date.strftime("%Y-%m-%d"))
        
        # Сегодня
        date_range.append(today.strftime("%Y-%m-%d"))
        
        # 10 дней вперед
        for i in range(1, 11):
            date = today + timedelta(days=i)
            date_range.append(date.strftime("%Y-%m-%d"))
        
        return date_range
    
    def calculate_date_spacing(self, dates):
        """Рассчитать расстояние между датами с учетом перекрывающихся задач"""
        base_spacing = 120  # Базовое расстояние между датами
        max_spacing = 300   # Максимальное расстояние
        
        # Получить количество задач для каждой даты
        date_task_counts = {}
        for date_str in dates:
            tasks = self.db.get_tasks_by_date(date_str)
            uncompleted_tasks = [task for task in tasks if not task[4]]
            date_task_counts[date_str] = len(uncompleted_tasks)
        
        # Рассчитать необходимое расстояние на основе количества задач
        spacing = base_spacing
        for date_str, task_count in date_task_counts.items():
            if task_count > 3:
                # Увеличиваем расстояние для дат с большим количеством задач
                required_spacing = base_spacing + (task_count - 3) * 20
                spacing = max(spacing, min(required_spacing, max_spacing))
        
        return spacing
    
    def showEvent(self, event):
        """При показе виджета центрируем на сегодняшней дате"""
        super().showEvent(event)
        self.center_on_today()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(30, 30, 30))
        
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(self.scale, self.scale)
        painter.translate(self.offset.x(), self.offset.y())
        
        # Generate graph data
        self.generate_graph_data()
        
        if not self.nodes:
            painter.setPen(QColor(102, 102, 102))
            painter.setFont(QFont("Segoe UI", 12))
            painter.drawText(-100, 0, "No calendar tasks to display")
            return
        
        # Draw timeline
        painter.setPen(QPen(QColor(156, 39, 176), 3))
        
        # Найти минимальную и максимальную X координату для дат
        date_nodes = [n for n in self.nodes if n["type"] == "date"]
        if date_nodes:
            min_x = min(node["x"] for node in date_nodes)
            max_x = max(node["x"] for node in date_nodes)
            painter.drawLine(int(min_x - 50), 0, int(max_x + 50), 0)
        
        # Draw edges (from dates to tasks)
        painter.setPen(QPen(QColor(156, 39, 176, 180), 1.5))
        for start_id, end_id in self.edges:
            start_node = next((n for n in self.nodes if n["id"] == start_id), None)
            end_node = next((n for n in self.nodes if n["id"] == end_id), None)
            
            if start_node and end_node:
                # Рисуем изогнутые линии чтобы избежать наложений
                start_x, start_y = start_node["x"], start_node["y"]
                end_x, end_y = end_node["x"], end_node["y"]
                
                # Контрольные точки для кривой Безье
                control_x = (start_x + end_x) / 2
                control_y = min(start_y, end_y) - 40
                
                # Рисуем кривую Безье
                path = QPainterPath()
                path.moveTo(start_x, start_y)
                path.quadTo(control_x, control_y, end_x, end_y)
                painter.drawPath(path)
        
        # Draw separator lines between dates
        painter.setPen(QPen(QColor(100, 100, 100), 1, Qt.DashLine))
        for node in self.nodes:
            if node.get("separator"):
                painter.drawLine(int(node["x"]), -200, int(node["x"]), 200)
        
        # Draw nodes (сначала задачи, потом даты чтобы даты были поверх)
        # Рисуем задачи
        for node in self.nodes:
            if node["type"] == "task":
                color = QColor(233, 30, 99)
                radius = 15
                
                painter.setBrush(color)
                painter.setPen(QPen(QColor(255, 255, 255), 2))
                painter.drawEllipse(int(node["x"] - radius), int(node["y"] - radius), 
                                  radius * 2, radius * 2)
                
                painter.setPen(QColor(255, 255, 255))
                font = QFont("Segoe UI", 8)
                painter.setFont(font)
                
                text = node["text"]
                # Обрезаем длинный текст
                if len(text) > 20:
                    text = text[:17] + "..."
                
                text_rect = painter.boundingRect(0, 0, 120, 40, Qt.AlignCenter, text)
                painter.drawText(int(node["x"] - 60), int(node["y"] + radius + 15), 120, 40, 
                               Qt.AlignCenter | Qt.TextWordWrap, text)
        
        # Рисуем даты
        for node in self.nodes:
            if node["type"] == "date":
                color = QColor(156, 39, 176)
                radius = 20
                
                # Подсвечиваем сегодняшнюю дату
                today_str = datetime.now().strftime("%Y-%m-%d")
                if node["id"] == f"date_{today_str}":
                    painter.setBrush(QColor(255, 193, 7))
                    painter.setPen(QPen(QColor(255, 255, 255), 3))
                else:
                    painter.setBrush(color)
                    painter.setPen(QPen(QColor(255, 255, 255), 2))
                
                painter.drawEllipse(int(node["x"] - radius), int(node["y"] - radius), 
                                  radius * 2, radius * 2)
                
                painter.setPen(QColor(255, 255, 255))
                font = QFont("Segoe UI", 9)
                font.setBold(True)
                painter.setFont(font)
                
                text = node["text"]
                text_rect = painter.boundingRect(0, 0, 100, 30, Qt.AlignCenter, text)
                painter.drawText(int(node["x"] - 50), int(node["y"] + radius + 25), 100, 30, 
                               Qt.AlignCenter, text)
    
    def generate_graph_data(self):
        self.nodes.clear()
        self.edges.clear()
        
        # Получаем диапазон дат: 10 дней назад и 10 дней вперед
        dates = self.get_date_range()
        
        if not dates:
            return
        
        # Рассчитываем расстояние между датами
        date_spacing = self.calculate_date_spacing(dates)
        total_dates = len(dates)
        timeline_width = total_dates * date_spacing
        start_x = -timeline_width / 2 + date_spacing / 2
        
        # Словарь для хранения позиций задач по Y координате
        task_y_positions = {}
        
        for i, date_str in enumerate(dates):
            # Создаем узел даты
            date_x = start_x + i * date_spacing
            date_node = {
                "id": f"date_{date_str}", 
                "text": date_str, 
                "x": date_x, 
                "y": 0, 
                "type": "date"
            }
            self.nodes.append(date_node)
            
            # Добавляем разделитель между датами (кроме последней)
            if i < len(dates) - 1:
                separator_x = start_x + (i + 0.5) * date_spacing
                separator_node = {
                    "id": f"separator_{i}", 
                    "text": "", 
                    "x": separator_x, 
                    "y": 0, 
                    "type": "separator",
                    "separator": True
                }
                self.nodes.append(separator_node)
            
            # Получаем задачи для этой даты (только незавершенные)
            tasks = self.db.get_tasks_by_date(date_str)
            uncompleted_tasks = [task for task in tasks if not task[4]]
            
            # Располагаем задачи вокруг даты
            if uncompleted_tasks:
                # Используем спиральное расположение чтобы избежать наложений
                spiral_radius = 60
                spiral_step = 15
                
                for j, (task_id, task_text, description, task_type, completed) in enumerate(uncompleted_tasks):
                    # Спиральное расположение
                    spiral_angle = j * (2 * math.pi / 6)  # 6 задач на круг
                    spiral_distance = spiral_radius + (j // 6) * spiral_step
                    
                    task_x = date_x + spiral_distance * math.cos(spiral_angle)
                    task_y = -80 + spiral_distance * math.sin(spiral_angle)
                    
                    # Проверяем и корректируем позицию чтобы избежать наложений
                    attempts = 0
                    while self.is_task_position_overlapping(task_x, task_y, task_y_positions) and attempts < 10:
                        spiral_distance += spiral_step
                        spiral_angle += 0.5
                        task_x = date_x + spiral_distance * math.cos(spiral_angle)
                        task_y = -80 + spiral_distance * math.sin(spiral_angle)
                        attempts += 1
                    
                    # Сохраняем позицию задачи
                    task_key = f"{task_x:.1f}_{task_y:.1f}"
                    task_y_positions[task_key] = True
                    
                    task_node = {
                        "id": f"task_{task_id}", 
                        "text": task_text,
                        "x": task_x, 
                        "y": task_y, 
                        "type": "task"
                    }
                    self.nodes.append(task_node)
                    self.edges.append((f"date_{date_str}", f"task_{task_id}"))
    
    def is_task_position_overlapping(self, x, y, existing_positions, min_distance=40):
        """Проверить, перекрывается ли позиция задачи с существующими"""
        for pos_key in existing_positions.keys():
            existing_x, existing_y = map(float, pos_key.split('_'))
            distance = math.sqrt((x - existing_x)**2 + (y - existing_y)**2)
            if distance < min_distance:
                return True
        return False


class GraphView(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Use the new tabbed graph widget
        self.graph_tabs = GraphTabWidget(self.db)
        layout.addWidget(self.graph_tabs)


class CustomCalendar(QCalendarWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.dates_with_tasks = set()
        self.update_dates()
        
        self.setStyleSheet("""
            QCalendarWidget QAbstractItemView:enabled {
                color: #d4d4d4;
                background-color: #252526;
                selection-background-color: #094771;
                selection-color: #ffffff;
            }
            QCalendarWidget QWidget {
                alternate-background-color: #2d2d30;
            }
            QCalendarWidget QToolButton {
                color: #cccccc;
                background-color: #2d2d30;
                font-weight: bold;
                font-size: 12px;
            }
            QCalendarWidget QMenu {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #3e3e42;
            }
            QCalendarWidget QSpinBox {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #464647;
                selection-background-color: #094771;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #2d2d30;
                color: #cccccc;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #969696;
                background-color: #1e1e1e;
                font-weight: bold;
            }
        """)
        
    def update_dates(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT date FROM calendar_tasks WHERE completed = 0
        ''')
        dates = [row[0] for row in cursor.fetchall()]
        conn.close()
        self.dates_with_tasks = set(dates)
        self.updateCells()
        
    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)
        
        if date.day() == 1 or date.dayOfWeek() == 1:
            painter.save()
            if date.day() == 1:
                painter.fillRect(rect, QColor(45, 45, 48))
            painter.setPen(QColor(204, 204, 204))
            painter.drawText(rect, Qt.AlignCenter, str(date.day()))
            painter.restore()
        
        date_str = date.toString("yyyy-MM-dd")
        if date_str in self.dates_with_tasks:
            painter.save()
            painter.setBrush(QColor(0, 122, 204))
            painter.setPen(Qt.NoPen)
            dot_size = 6
            dot_x = rect.right() - dot_size - 3
            dot_y = rect.top() + 3
            painter.drawEllipse(dot_x, dot_y, dot_size, dot_size)
            painter.restore()


class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = None
        
    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.db:
            return
            
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        
        for i in range(self.count()):
            item = self.item(i)
            if not item:
                continue
                
            task_id = item.data(Qt.UserRole)
            if not task_id:
                continue
                
            status = self.db.get_task_status(task_id)
            
            if status == "completed":
                color = QColor(76, 175, 80)
            elif status == "assigned":
                color = QColor(255, 193, 7)
            elif status == "overdue":
                color = QColor(244, 67, 54)
            else:
                color = QColor(244, 67, 54)
                
            rect = self.visualItemRect(item)
            dot_size = 6
            dot_x = int(rect.right() - dot_size - 5)
            dot_y = int(rect.top() + (rect.height() - dot_size) / 2)
            
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(dot_x, dot_y, dot_size, dot_size)