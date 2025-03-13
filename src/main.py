import os.path
import sys
from typing import Optional, List

# Ensure the src directory is in the path for proper imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# PyQt imports
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

# Import local modules
from ui.components import GoogleTasksApp
from api.google_tasks import GoogleTasksAPI
from auth.google_auth import GoogleAuthManager

# Application constants
APP_TITLE = "Google Tasks Desktop"
ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                        "..", "asset", "Google_Tasks_2021.svg.png")


def main():
    # Initialize the application
    app = QApplication(sys.argv)
    
    # Set application-wide properties
    app.setApplicationName(APP_TITLE)
    app.setApplicationDisplayName(APP_TITLE)
    app.setWindowIcon(QIcon(ICON_PATH))
    
    # Create the authentication manager
    auth_manager = GoogleAuthManager()
    
    # Create the tasks API client
    tasks_api = GoogleTasksAPI(auth_manager)
    
    # Create the main application window
    window = GoogleTasksApp(tasks_api)
    window.setWindowTitle(APP_TITLE)
    window.setWindowIcon(QIcon(ICON_PATH))
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
