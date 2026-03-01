# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSharedMemory
from task_manager import TaskManager

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Single instance check
    shared_memory = QSharedMemory("advanced_task_manager")
    if not shared_memory.create(1):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.warning(None, "Warning", "Application is already running! Use Alt+L to show it")
        sys.exit(1)
    
    window = TaskManager()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()