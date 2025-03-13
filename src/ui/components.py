import os
import sys
from typing import List, Dict, Any, Optional

# Add the parent directory to sys.path to fix import issues
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, 
                            QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton,
                            QStatusBar, QProgressBar, QStyle, QMenu, QAction, 
                            QCheckBox, QMessageBox, QInputDialog, QLineEdit,
                            QComboBox, QDialog, QAbstractItemView, QFrame, QSplitter,
                            QToolButton, QSlider, QDialogButtonBox)
from PyQt5.QtCore import Qt, QSize, QMargins, QSettings, QTimer, QPoint
from PyQt5.QtGui import QIcon, QFont, QColor

from googleapiclient.errors import HttpError
from utils.constants import (APP_TITLE, APP_SETTINGS, SETTING_THEME, THEME_LIGHT,
                                THEME_DARK, ICON_PATH, UI_FONT_FAMILY, UI_BUTTON_HEIGHT,
                                UI_BUTTON_MAX_WIDTH, UI_TASK_FONT_SIZE, UI_LIST_FONT_SIZE,
                                UI_TITLE_FONT_SIZE, UI_SMALL_ICON_SIZE, UI_TREE_INDENTATION,
                                UI_PIN_BUTTON_SIZE, UI_ANCHOR_BUTTON_SIZE, UI_OPACITY_BUTTON_SIZE)
# Import our theme styles
from ui.style.themes import Themes

class TaskTreeItem(QTreeWidgetItem):
    """Custom tree item class to store task data."""
    def __init__(self, title, task_id=None, status=None, parent=None):
        super().__init__(parent, [title])
        self.task_id = task_id
        self.status = status
        


class DragDropTreeWidget(QTreeWidget):
    """Custom tree widget that supports drag and drop for reordering tasks."""
    def __init__(self, parent=None):
        super(DragDropTreeWidget, self).__init__(parent)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.task_moved_callback = None  # Callback to execute when task is moved
        
    def dropEvent(self, event):
        # Store current selection to restore after drop
        current_item = self.currentItem()
        # Get drop position info
        drop_indicator = self.dropIndicatorPosition()
        target_item = self.itemAt(event.pos())
        
        # Only allow dropping on task lists or between tasks with the same parent
        if target_item:
            if self.is_valid_drop(target_item, drop_indicator, current_item):
                # Call parent class implementation for the actual move
                super(DragDropTreeWidget, self).dropEvent(event)
                
                # After move, notify callback if it exists
                if self.task_moved_callback and current_item and current_item.parent():
                    self.task_moved_callback(current_item)
            else:
                event.ignore()
        else:
            event.ignore()
    
    def is_valid_drop(self, target_item, drop_indicator, current_item):
        """Check if this is a valid drop operation."""
        if not current_item or not target_item:
            return False
            
        # Only allow task reordering, not task list reordering
        if not current_item.parent():
            return False
            
        # Task can only be moved within its own task list
        if drop_indicator == QAbstractItemView.OnItem:
            # Don't allow dropping a task onto a task list directly
            if not target_item.parent():
                return False
                
            # Make sure both items are in the same task list
            return target_item.parent() == current_item.parent()
        elif drop_indicator in (QAbstractItemView.AboveItem, QAbstractItemView.BelowItem):
            # If dropping between task list items
            if not target_item.parent():
                return False
                
            # Make sure target is in the same task list
            return target_item.parent() == current_item.parent()
            
        return False


class ResponsiveButton(QPushButton):
    """A button that adjusts its text based on window size."""
    def __init__(self, full_text, compact_text="", icon=None, parent=None):
        super().__init__(full_text, parent)
        self.full_text = full_text
        self.compact_text = compact_text if compact_text else full_text[0]  # First letter as default
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(UI_SMALL_ICON_SIZE, UI_SMALL_ICON_SIZE))
        # Set a fixed height for ultra compact appearance
        self.setFixedHeight(UI_BUTTON_HEIGHT)
        # Set a maximum width to avoid overly large buttons
        self.setMaximumWidth(UI_BUTTON_MAX_WIDTH)
            
    def set_responsive_mode(self, compact=False):
        """Set the display mode of the button based on window size."""
        if compact:
            self.setText(self.compact_text)
            self.setToolTip(self.full_text)  # Show full text as tooltip in compact mode
        else:
            self.setText(self.full_text)
            self.setToolTip("")  # Clear tooltip in full mode


class GoogleTasksApp(QMainWindow):
    def __init__(self, tasks_api=None):
        super().__init__()
        # Initialize managers and API clients
        self.settings = QSettings(APP_SETTINGS, APP_SETTINGS)
        self.current_theme = self.settings.value(SETTING_THEME, THEME_LIGHT)
        
        # Store the tasks API client
        self.tasks_api = tasks_api
        
        # UI state variables
        self.responsive_elements = [] 
        self.compact_mode_width_threshold = 650
        self.is_pinned = False
        self.is_anchored = False
        self.is_transparent = False
        self.opacity = 1.0
        self.draggable = True
        self.drag_position = None
        
        # Initialize UI components
        self._init_ui_components()
        self.init_ui()
        self.load_tasks_data()
        
        # Setup window resize monitoring
        self._setup_resize_monitoring()
    
    def _init_ui_components(self):
        """Initialize reusable UI components."""
        self.tree = None
        self.status_bar = None
        self.progress_bar = None
        self.search_hint = None
        self.theme_button = None
    
    def _setup_resize_monitoring(self):
        """Setup window resize monitoring."""
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.handle_resize)
        
    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        # Using timer to prevent excessive updates during resize
        self.resize_timer.start(100)
        
    def handle_resize(self):
        """Update UI elements based on window size."""
        width = self.width()
        compact_mode = width < self.compact_mode_width_threshold
        
        for element in self.responsive_elements:
            if isinstance(element, ResponsiveButton):
                element.set_responsive_mode(compact=compact_mode)
        
        if hasattr(self, 'search_hint'):
            self.search_hint.setVisible(not compact_mode)
    
    def _create_buttons(self, layout):
        """Create and add action buttons to the layout."""
        # Theme toggle button
        theme_icon = QApplication.style().standardIcon(QStyle.SP_DialogYesButton)
        theme_button = self._create_button("Dark", "🌙", theme_icon, "themeButton", self.toggle_theme)
        self.theme_button = theme_button
        layout.addWidget(theme_button)
        
        # Refresh button
        refresh_icon = QApplication.style().standardIcon(QStyle.SP_BrowserReload)
        refresh_button = self._create_button("Refresh", "↻", refresh_icon, "actionButton", self.load_tasks_data)
        layout.addWidget(refresh_button)
        
        # Add task button
        add_icon = QApplication.style().standardIcon(QStyle.SP_FileDialogNewFolder)
        add_button = self._create_button("Add", "+", add_icon, "primaryButton", self.add_new_task)
        layout.addWidget(add_button)
        
        # Delete task button
        delete_icon = QApplication.style().standardIcon(QStyle.SP_TrashIcon)
        delete_button = self._create_button("Delete", "✕", delete_icon, "dangerButton", self.delete_selected_task)
        layout.addWidget(delete_button)
    
    def _create_button(self, text, compact_text, icon, object_name, callback):
        """Create a responsive button with the given properties."""
        button = ResponsiveButton(text, compact_text, icon)
        button.setObjectName(object_name)
        button.clicked.connect(callback)
        self.responsive_elements.append(button)
        return button
    
    def _setup_tree_widget(self):
        """Configure the tree widget."""
        self.tree = DragDropTreeWidget()
        self.tree.setObjectName("taskTree")
        self.tree.setHeaderLabels(["Tasks"])
        self.tree.setHeaderHidden(True)
        self.tree.setIconSize(QSize(UI_SMALL_ICON_SIZE, UI_SMALL_ICON_SIZE))
        # Remove alternating row colors for a cleaner look
        self.tree.setAlternatingRowColors(False)
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.task_moved_callback = self.on_task_dragged
        self.tree.setIndentation(UI_TREE_INDENTATION)
        self.tree.setAnimated(True)
        
        # Set compact tree item style
        self.tree.setStyleSheet("""
            QTreeWidget::item {
                padding-right: 1px;
                padding-left: 1px;
                border-bottom: 1px solid transparent;
            }
        """)

    def init_ui(self):
        """Initialize the user interface with an ultra-compact design."""
        # Window setup
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(300, 100)
        self._load_window_icon()
        
        # Set application-wide font
        app_font = QFont(UI_FONT_FAMILY, UI_TASK_FONT_SIZE)
        QApplication.setFont(app_font)
        
        # Main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 2, 4)
        main_layout.setSpacing(2)
        
        # Header section
        header_frame, header_layout = self._create_header_section()
        main_layout.addWidget(header_frame)
        
        # Separator
        separator = self._create_separator()
        main_layout.addWidget(separator)
        
        # Content section
        content_layout = self._create_content_section()
        main_layout.addLayout(content_layout)
        
        # Status bar
        self._setup_status_bar()
        
        self.setCentralWidget(central_widget)
        self.apply_theme(self.current_theme)
        QTimer.singleShot(0, self.handle_resize)
        QTimer.singleShot(100, self.restore_window_state)
    
    def _create_header_section(self):
        """Create the header section with title and buttons."""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 1)
        
        # Create a container for control buttons
        title_container = QFrame()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)
        
        # Pin button (always on top)
        self.pin_button = QToolButton()
        self.pin_button.setObjectName("pinButton")
        self.pin_button.setCheckable(True)
        self.pin_button.setFixedSize(UI_PIN_BUTTON_SIZE, UI_PIN_BUTTON_SIZE)
        self.pin_button.setIcon(QIcon.fromTheme("window-pin", 
                            QApplication.style().standardIcon(QStyle.SP_DialogApplyButton)))
        self.pin_button.setToolTip("Keep window on top")
        self.pin_button.clicked.connect(self.toggle_pin_window)
        title_layout.addWidget(self.pin_button)
        
        # Anchor button (fix position)
        self.anchor_button = QToolButton()
        self.anchor_button.setObjectName("anchorButton")
        self.anchor_button.setCheckable(True)
        self.anchor_button.setFixedSize(UI_ANCHOR_BUTTON_SIZE, UI_ANCHOR_BUTTON_SIZE)
        self.anchor_button.setIcon(QIcon.fromTheme("anchor", 
                            QApplication.style().standardIcon(QStyle.SP_DialogSaveButton)))
        self.anchor_button.setToolTip("Fix window position")
        self.anchor_button.clicked.connect(self.toggle_anchor_window)
        title_layout.addWidget(self.anchor_button)
        
        # Transparency button
        self.transparency_button = QToolButton()
        self.transparency_button.setObjectName("transparencyButton")
        self.transparency_button.setCheckable(True)
        self.transparency_button.setFixedSize(UI_OPACITY_BUTTON_SIZE, UI_OPACITY_BUTTON_SIZE)
        self.transparency_button.setIcon(QIcon.fromTheme("transparency", 
                                      QApplication.style().standardIcon(QStyle.SP_ToolBarHorizontalExtensionButton)))
        self.transparency_button.setToolTip("Toggle transparency")
        self.transparency_button.clicked.connect(self.toggle_transparency)
        title_layout.addWidget(self.transparency_button)
        
        header_layout.addWidget(title_container)
        
        # Button container
        button_container = QFrame()
        button_container.setObjectName("buttonContainer")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(1)
        
        # Search hint
        self.search_hint = QLabel("Drag to reorder")
        self.search_hint.setObjectName("searchHint")
        self.search_hint.setFont(QFont(UI_FONT_FAMILY, UI_TASK_FONT_SIZE, QFont.Light))
        self.search_hint.setVisible(False)
        button_layout.addWidget(self.search_hint)
        
        button_layout.addStretch(1)
        self._create_buttons(button_layout)
        header_layout.addWidget(button_container)
        
        return header_frame, header_layout
    
    def _create_separator(self):
        """Create a separator line."""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setObjectName("separator")
        return separator
    
    def _create_content_section(self):
        """Create the content section with tree widget."""
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 1, 0, 0)
        
        self._setup_tree_widget()
        content_layout.addWidget(self.tree)
        
        return content_layout
    
    def _setup_status_bar(self):
        """Setup the status bar with progress indicator."""
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("statusBar")
        self.status_bar.setMaximumHeight(18)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setMaximumWidth(120)
        self.progress_bar.setVisible(False)
        self.progress_bar.setObjectName("progressBar")
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        self.setStatusBar(self.status_bar)

    def _load_window_icon(self):
        """Load the application icon with fallback options."""
        try:
            # Try primary path
            if os.path.exists(ICON_PATH):
                self._set_app_icon(ICON_PATH)
            else:
                # Try alternative paths
                alt_paths = [
                    "asset/Google_Tasks_2021.svg.png",
                    os.path.join(os.getcwd(), "asset", "Google_Tasks_2021.svg.png")
                ]
                
                icon_loaded = False
                for path in alt_paths:
                    if os.path.exists(path):
                        self._set_app_icon(path)
                        icon_loaded = True
                        break
                        
                if not icon_loaded:
                    # Fall back to a system icon
                    self._set_fallback_icon()
        except Exception:
            self._set_fallback_icon()
    
    def _set_app_icon(self, path):
        """Set the application icon from a file path."""
        app_icon = QIcon(path)
        self.setWindowIcon(app_icon)
        QApplication.setWindowIcon(app_icon)
    
    def _set_fallback_icon(self):
        """Set a fallback system icon when no custom icon is available."""
        app_icon = QApplication.style().standardIcon(QStyle.SP_TitleBarMenuButton)
        self.setWindowIcon(app_icon)
        QApplication.setWindowIcon(app_icon)

    # Theme management
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        new_theme = THEME_DARK if self.current_theme == THEME_LIGHT else THEME_LIGHT
        
        # Save theme setting
        self.current_theme = new_theme
        self.settings.setValue(SETTING_THEME, new_theme)
        
        # Apply the new theme
        self.apply_theme(new_theme)
        self.update_theme_button(self.theme_button)
        self.refresh_task_colors()
        self.update_title_color()
        self.update_status_bar()
        
        theme_name = "Dark" if new_theme == THEME_DARK else "Light"
        self.status_bar.showMessage(f"Switched to {theme_name} theme")
    
    def update_theme_button(self, button):
        """Update the theme button icon and tooltip based on current theme."""
        if self.current_theme == THEME_LIGHT:
            button.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogYesButton))
            button.full_text = "Dark"  # Shortened text
            button.compact_text = "🌙"  # Moon emoji for dark mode
        else:
            button.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogNoButton))
            button.full_text = "Light"  # Shortened text
            button.compact_text = "☀️"  # Sun emoji for light mode
            
        # Update the button text based on current mode
        is_compact = self.width() < self.compact_mode_width_threshold
        button.set_responsive_mode(compact=is_compact)

    def apply_theme(self, theme):
        """Apply the specified theme to the application."""
        if theme == THEME_DARK:
            self.apply_dark_style()
        else:
            self.apply_light_style()
            
        # Re-apply rounded corners if window is anchored
        if self.is_anchored:
            self.setStyleSheet(self.styleSheet() + Themes.get_anchored_style(
                "dark" if theme == THEME_DARK else "light"))

    def apply_light_style(self):
        """Apply a light/white modern style with ultra-compact elements."""
        self.setStyleSheet(Themes.get_light_style())

    def apply_dark_style(self):
        """Apply a dark modern style with ultra-compact elements."""
        self.setStyleSheet(Themes.get_dark_style())
    
    def load_tasks_data(self):
        """Load task lists and tasks from Google Tasks API."""
        try:
            self.tree.clear()
            self.status_bar.showMessage("Loading tasks...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(10)
            
            try:
                # Get task lists
                self.progress_bar.setValue(30)
                task_lists = self.tasks_api.get_task_lists()
                self.progress_bar.setValue(70)
            except Exception as e:
                self.progress_bar.setVisible(False)
                self.status_bar.showMessage(f"Error loading task lists: {e}")
                self.show_error_message("API Error", f"Could not load task lists: {e}")
                return
            
            if not task_lists:
                no_lists_item = QTreeWidgetItem(["No task lists found"])
                self.tree.addTopLevelItem(no_lists_item)
                self.status_bar.showMessage("No task lists found")
                self.progress_bar.setVisible(False)
                return
            
            # Update the way tasks are displayed for better readability with smaller font
            for task_list in task_lists:
                list_item = TaskTreeItem(task_list['title'], task_list['id'])
                
                # Use simple folder icon for lists
                folder_icon = QApplication.style().standardIcon(QStyle.SP_DirOpenIcon)
                list_item.setIcon(0, folder_icon)
                list_item.setFont(0, QFont("Segoe UI", 9, QFont.Bold))
                self.tree.addTopLevelItem(list_item)
                
                # Get and add tasks for this task list
                try:
                    tasks = self.tasks_api.get_tasks(task_list['id'])
                    self._create_task_items(tasks, list_item)
                except Exception as e:
                    # If one task list fails, continue with others
                    self.status_bar.showMessage(f"Error loading tasks for list {task_list['title']}: {e}")
                    no_tasks_item = QTreeWidgetItem([f" Error loading tasks: {e}"])
                    no_tasks_item.setForeground(0, QColor("#ff0000"))
                    list_item.addChild(no_tasks_item)
            
            self.tree.expandAll()
            self.progress_bar.setValue(100)
            self.status_bar.showMessage("Tasks loaded successfully")
            
        except Exception as e:
            self.status_bar.showMessage(f"Error: {e}")
        finally:
            self.progress_bar.setVisible(False)
    
    def _create_task_items(self, tasks, list_item):
        """Create task items for a task list."""
        if not tasks:
            self._create_empty_list_indicator(list_item)
            return
            
        for task in tasks:
            task_title = task['title']
            task_status = task.get('status', 'needsAction')
            task_item = TaskTreeItem(task_title, task['id'], task_status, list_item)
            
            # Apply appropriate styling based on status
            self._style_task_item(task_item, task_status)
    
    def _style_task_item(self, task_item, status):
        """Apply appropriate styling to a task item based on its status."""
        icon = QApplication.style().standardIcon(
            QStyle.SP_DialogApplyButton if status == 'completed' else QStyle.SP_FileIcon)
        task_item.setIcon(0, icon)
        
        # Set font and color
        task_item.setFont(0, QFont(UI_FONT_FAMILY, UI_TASK_FONT_SIZE, QFont.Normal))
        
        if status == 'completed':
            task_item.setForeground(0, QColor("#9AA0A6"))
            task_item.setText(0, f"✓ {task_item.text(0)}")
        else:
            # Set color based on theme
            color = QColor("#E8EAED") if self.current_theme == THEME_DARK else QColor("#202124")
            task_item.setForeground(0, color)
    
    def _create_empty_list_indicator(self, list_item):
        """Create an indicator that a list has no tasks."""
        no_tasks_item = QTreeWidgetItem([" No tasks in this list"])
        no_tasks_item.setForeground(0, QColor("#9AA0A6"))
        no_tasks_item.setFont(0, QFont(UI_FONT_FAMILY, UI_TASK_FONT_SIZE, QFont.Italic))
        list_item.addChild(no_tasks_item)
    
    def toggle_task_status(self, item):
        """Toggle the completion status of a task."""
        if not isinstance(item, TaskTreeItem) or item.task_id is None:
            return
            
        parent_item = item.parent()
        if not parent_item or not isinstance(parent_item, TaskTreeItem):
            return  # Not a task item
            
        tasklist_id = parent_item.task_id
        task_id = item.task_id
        
        try:
            # Get the current task using tasks API
            task = self.tasks_api.get_task(tasklist_id, task_id)
            
            # Toggle status
            new_status = 'completed' if task.get('status') == 'needsAction' else 'needsAction'
            task['status'] = new_status
            
            # Update the task using tasks API
            self.tasks_api.update_task(tasklist_id, task_id, task)
            
            # Update UI with theme-aware colors
            item.status = new_status
            
            if new_status == 'completed':
                item.setForeground(0, QColor("#9AA0A6"))  # Gray for completed tasks
                item.setText(0, f"✓ {item.text(0).replace('✓ ', '')}")
                item.setIcon(0, QApplication.style().standardIcon(QStyle.SP_DialogApplyButton))
            else:
                # Different colors based on theme
                if self.current_theme == THEME_DARK:
                    item.setForeground(0, QColor("#E8EAED"))
                else:
                    item.setForeground(0, QColor("#202124"))
                    
                item.setText(0, item.text(0).replace('✓ ', ''))
                item.setIcon(0, QApplication.style().standardIcon(QStyle.SP_FileIcon))
                
            self.status_bar.showMessage(f"Task marked as {new_status}")
            
        except HttpError as e:
            error_details = f"Error {e.resp.status}: {e.content.decode()}"
            
            # If it's a 403 error, try to refresh credentials
            if e.resp.status == 403:
                self.status_bar.showMessage("Permission denied. Refreshing credentials...")
                try:
                    # Try the operation again with refreshed credentials
                    self.tasks_api.refresh_service()
                    
                    # Get the task again
                    task = self.tasks_api.get_task(tasklist_id, task_id)
                    new_status = 'completed' if task.get('status') == 'needsAction' else 'needsAction'
                    task['status'] = new_status
                    self.tasks_api.update_task(tasklist_id, task_id, task)
                    
                    # Update UI
                    item.status = new_status
                    if new_status == 'completed':
                        item.setForeground(0, QColor("#9AA0A6"))
                        item.setText(0, f"✓ {item.text(0).replace('✓ ', '')}")
                        item.setIcon(0, QApplication.style().standardIcon(QStyle.SP_DialogApplyButton))
                    else:
                        if self.current_theme == THEME_DARK:
                            item.setForeground(0, QColor("#E8EAED"))
                        else:
                            item.setForeground(0, QColor("#202124"))
                        item.setText(0, item.text(0).replace('✓ ', ''))
                        item.setIcon(0, QApplication.style().standardIcon(QStyle.SP_FileIcon))
                    
                    self.status_bar.showMessage(f"Task marked as {new_status} after refreshing credentials")
                    
                except Exception as refresh_error:
                    self.status_bar.showMessage(f"Couldn't refresh credentials: {refresh_error}")
                    self.show_error_message("Authentication Error",
                                           "Your credentials need to be updated. The application will restart.")
                    QApplication.quit()
            else:
                self.status_bar.showMessage(f"API error: {error_details}")
                
        except Exception as e:
            self.status_bar.showMessage(f"Error updating task: {e}")
    
    def create_custom_dialog(self, title, message, icon_type=QMessageBox.Question):
        """Create a custom confirmation dialog with guaranteed visible buttons."""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        
        # Set layout
        layout = QVBoxLayout(dialog)
        
        # Create a horizontal layout for icon and message
        hbox = QHBoxLayout()
        
        # Add appropriate icon
        icon_label = QLabel()
        if icon_type == QMessageBox.Question:
            icon = self.style().standardIcon(QStyle.SP_MessageBoxQuestion)
        elif icon_type == QMessageBox.Critical:
            icon = self.style().standardIcon(QStyle.SP_MessageBoxCritical)
        else:
            icon = self.style().standardIcon(QStyle.SP_MessageBoxInformation)
        
        icon_label.setPixmap(icon.pixmap(32, 32))
        hbox.addWidget(icon_label)
        
        # Add message
        msg_label = QLabel(message)
        # Make sure the label text uses the correct color based on theme
        if self.current_theme == THEME_DARK:
            msg_label.setStyleSheet("color: #e8eaed;")
        else:
            msg_label.setStyleSheet("color: #202124;")
        hbox.addWidget(msg_label, 1)
        
        layout.addLayout(hbox)
        
        # Add spacer
        layout.addSpacing(10)
        
        # Create button box
        button_box = QDialogButtonBox()
        yes_button = button_box.addButton(QDialogButtonBox.Yes)
        no_button = button_box.addButton(QDialogButtonBox.No)
        
        # Set default button
        no_button.setDefault(True)
        
        # Style the buttons based on theme
        button_style = Themes.get_dialog_button_style(
            "dark" if self.current_theme == THEME_DARK else "light")
        button_box.setStyleSheet(button_style)
        layout.addWidget(button_box)
        
        # Apply overall dialog styling
        dialog_style = Themes.get_dialog_style(
            "dark" if self.current_theme == THEME_DARK else "light")
        dialog.setStyleSheet(dialog_style)
        
        # Connect signals
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        # Set fixed size to ensure buttons are visible
        dialog.setMinimumWidth(300)
        
        return dialog, button_box
    
    def delete_selected_task(self):
        """Delete the currently selected task or task list."""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            self.status_bar.showMessage("No task or task list selected")
            return
            
        item = selected_items[0]
        if not isinstance(item, TaskTreeItem):
            return
        
        # If it's a tasklist (no parent)
        if item.parent() is None:
            tasklist_id = item.task_id
            
            dialog, _ = self.create_custom_dialog(
                'Confirm Deletion',
                f"Are you sure you want to delete the task list '{item.text(0)}' and all its tasks?",
                QMessageBox.Question
            )
            
            result = dialog.exec_()
            
            if result == QDialog.Accepted:
                try:
                    # Delete using tasks API
                    self.tasks_api.delete_tasklist(tasklist_id)
                    self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(item))
                    self.status_bar.showMessage("Task list deleted successfully")
                except Exception as e:
                    self.status_bar.showMessage(f"Error deleting task list: {e}")
            return
        
        # It's a task
        parent_item = item.parent()
        if not isinstance(parent_item, TaskTreeItem):
            return
        
        tasklist_id = parent_item.task_id
        task_id = item.task_id
        
        dialog, _ = self.create_custom_dialog(
            'Confirm Deletion',
            f"Are you sure you want to delete task '{item.text(0).replace('✓ ', '')}'?",
            QMessageBox.Question
        )
        
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            try:
                # Delete using tasks API
                self.tasks_api.delete_task(tasklist_id, task_id)
                parent_item.removeChild(item)
                self.status_bar.showMessage("Task deleted successfully")
            except Exception as e:
                self.status_bar.showMessage(f"Error deleting task: {e}")
    
    def on_item_clicked(self, item, column):
        """Handle item clicks in the tree."""
        if item.parent() and isinstance(item, TaskTreeItem) and item.task_id:
            # It's a task, not a tasklist
            self.toggle_task_status(item)
    
    def add_new_task(self):
        """Add a new task to the selected task list."""
        # Get the currently selected item
        selected_items = self.tree.selectedItems()
        if not selected_items:
            self.status_bar.showMessage("Select a task list first")
            return
            
        selected_item = selected_items[0]
        
        # Determine which task list to add to
        if isinstance(selected_item, TaskTreeItem):
            # If it's a task, get its parent (the task list)
            if selected_item.parent():
                tasklist_item = selected_item.parent()
            else:
                tasklist_item = selected_item  # It's already a task list
        else:
            self.status_bar.showMessage("Invalid selection")
            return
            
        if not isinstance(tasklist_item, TaskTreeItem) or not tasklist_item.task_id:
            self.status_bar.showMessage("Invalid task list")
            return
            
        # Get task name from user
        task_title, ok = QInputDialog.getText(
            self, "Add Task", "Enter task title:", QLineEdit.Normal, ""
        )
        
        if ok and task_title:
            tasklist_id = tasklist_item.task_id
            
            # Create the task
            try:
                new_task = {
                    'title': task_title,
                    'status': 'needsAction'
                }
                
                # Create task using tasks API
                result = self.tasks_api.create_task(tasklist_id, new_task)
                
                # Add to the tree
                task_item = TaskTreeItem(task_title, result['id'], 'needsAction', tasklist_item)
                task_item.setIcon(0, QApplication.style().standardIcon(QStyle.SP_FileIcon))
                
                self.status_bar.showMessage(f"Task '{task_title}' added successfully")
                
            except Exception as e:
                self.status_bar.showMessage(f"Error creating task: {e}")
    
    def on_task_dragged(self, task_item):
        """Handle drag-and-drop reordering of tasks."""
        if not isinstance(task_item, TaskTreeItem) or not task_item.task_id:
            return
            
        parent_item = task_item.parent()
        if not parent_item or not isinstance(parent_item, TaskTreeItem):
            return
            
        tasklist_id = parent_item.task_id
        task_id = task_item.task_id
        
        # Find the previous item (if any)
        current_index = parent_item.indexOfChild(task_item)
        previous_id = None
        if current_index > 0:
            previous_item = parent_item.child(current_index - 1)
            if isinstance(previous_item, TaskTreeItem) and previous_item.task_id:
                previous_id = previous_item.task_id
        
        # Update the task position using tasks API
        try:
            self.status_bar.showMessage("Updating task position...")
            self.tasks_api.move_task(tasklist_id, task_id, previous_id)
            self.status_bar.showMessage("Task position updated successfully")
        except Exception as e:
            self.status_bar.showMessage(f"Error updating task position: {e}")
            self.load_tasks_data()  # Refresh the whole list on error to restore proper order
    
    def show_context_menu(self, position):
        """Show a context menu for items in the tree."""
        item = self.tree.itemAt(position)
        if not item:
            return
            
        context_menu = QMenu(self)
        
        # For task lists
        if isinstance(item, TaskTreeItem) and item.task_id and not item.parent():
            add_action = QAction("Add Task", self)
            add_action.triggered.connect(self.add_new_task)
            context_menu.addAction(add_action)
            
            delete_action = QAction("Delete Task List", self)
            delete_action.triggered.connect(lambda: self.delete_selected_task())
            context_menu.addAction(delete_action)
        
        # For individual tasks
        if item.parent() and isinstance(item, TaskTreeItem) and item.task_id:
            toggle_action = QAction("Mark as " + 
                ("Incomplete" if item.status == 'completed' else "Complete"), self)
            toggle_action.triggered.connect(lambda: self.toggle_task_status(item))
            context_menu.addAction(toggle_action)
            
            delete_action = QAction("Delete Task", self)
            delete_action.triggered.connect(lambda: self.delete_selected_task())
            context_menu.addAction(delete_action)
            
        context_menu.exec_(self.tree.mapToGlobal(position))
    
    def refresh_task_colors(self):
        """Refresh task colors based on current theme with better contrast."""
        # Update all task items with proper theme colors
        for i in range(self.tree.topLevelItemCount()):
            task_list_item = self.tree.topLevelItem(i)
            
            if not isinstance(task_list_item, TaskTreeItem):
                continue
                
            # Also update task list item colors based on theme with better contrast
            if self.current_theme == THEME_DARK:
                task_list_item.setForeground(0, QColor("#E8EAED"))  # Light color for dark mode
            else:
                task_list_item.setForeground(0, QColor("#1f1f1f"))  # Almost black for better contrast
                
            # Update each task in this list
            for j in range(task_list_item.childCount()):
                task_item = task_list_item.child(j)
                if not isinstance(task_item, TaskTreeItem):
                    # Handle non-task items like "No tasks in this list" messages
                    task_item.setForeground(0, QColor("#9AA0A6"))  # Gray for empty state
                    continue
                
                if not task_item.task_id:
                    continue
                    
                # Update colors based on completion status and current theme
                if task_item.status == 'completed':
                    task_item.setForeground(0, QColor("#9AA0A6"))  # Gray for completed tasks
                else:
                    if self.current_theme == THEME_DARK:
                        task_item.setForeground(0, QColor("#E8EAED"))  # Light text for dark mode
                    else:
                        task_item.setForeground(0, QColor("#202124"))  # Dark text for light mode
    
    def update_title_color(self):
        """Update application title color based on theme with better contrast."""
        # Find and update the title label if it exists
        for child in self.findChildren(QLabel):
            if child.objectName() == "titleLabel":
                if self.current_theme == THEME_DARK:
                    child.setStyleSheet("color: #8ab4f8;")
                else:
                    child.setStyleSheet("color: #0b57d0;")  # Darker blue for better contrast
                break
    
    def update_status_bar(self):
        """Update the status bar content for theme compatibility."""
        current_message = self.status_bar.currentMessage()
        # Clear and reset the message to force a style update
        self.status_bar.clearMessage()
        self.status_bar.showMessage(current_message)

    def toggle_pin_window(self):
        """Toggle the window's always-on-top state."""
        self.is_pinned = not self.is_pinned
        
        # Set window flags
        if self.is_pinned:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.pin_button.setIcon(QIcon.fromTheme("window-unpin", 
                                   QApplication.style().standardIcon(QStyle.SP_DialogApplyButton)))
            self.pin_button.setStyleSheet("background-color: #8ab4f8; border-radius: 2px;")
            self.pin_button.setToolTip("Unpin window")
            self.status_bar.showMessage("Window pinned - always on top")
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.pin_button.setIcon(QIcon.fromTheme("window-pin", 
                                   QApplication.style().standardIcon(QStyle.SP_DialogHelpButton)))
            self.pin_button.setStyleSheet("")
            self.pin_button.setToolTip("Keep window on top")
            self.status_bar.showMessage("Window unpinned")
        
        # Show the window again after changing flags
        self.show()

    def toggle_anchor_window(self):
        """Toggle the window's fixed position state."""
        self.is_anchored = not self.is_anchored
        
        if self.is_anchored:
            # Store current position
            self.settings.setValue("window_position", self.pos())
            
            # Make window frameless to hide window decorations when anchored
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
            
            # Apply rounded corners when the window is fixed
            anchored_style = Themes.get_anchored_style(
                "dark" if self.current_theme == THEME_DARK else "light")
            self.setStyleSheet(self.styleSheet() + anchored_style)
            
            # Update the anchor button to show it's active
            self.anchor_button.setIcon(QIcon.fromTheme("anchor-on", 
                                     QApplication.style().standardIcon(QStyle.SP_DialogApplyButton)))
            self.anchor_button.setStyleSheet("background-color: #4caf50; border-radius: 2px;")
            self.anchor_button.setToolTip("Unfix window position")
            self.status_bar.showMessage("Window position fixed")
            
            # Set the draggable state
            self.draggable = False
        else:
            # Restore window frame
            self.setWindowFlags(self.windowFlags() & ~Qt.FramelessWindowHint)
            
            # Restore original styling without custom border radius
            self.apply_theme(self.current_theme)
            
            # Update anchor button to inactive state
            self.anchor_button.setIcon(QIcon.fromTheme("anchor-off", 
                                     QApplication.style().standardIcon(QStyle.SP_DialogSaveButton)))
            self.anchor_button.setStyleSheet("")
            self.anchor_button.setToolTip("Fix window position")
            self.status_bar.showMessage("Window position unfixed")
            
            # Re-enable dragging
            self.draggable = True
        
        # Preserve the always-on-top state
        if self.is_pinned:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # Show the window again after changing flags
        self.show()
    
    def toggle_transparency(self):
        """Toggle window transparency."""
        self.is_transparent = not self.is_transparent
        
        if self.is_transparent:
            # Make window transparent
            self.setWindowOpacity(0.85)  # Initial transparency level
            self.transparency_button.setIcon(QIcon.fromTheme("transparency-on", 
                                         QApplication.style().standardIcon(QStyle.SP_ToolBarHorizontalExtensionButton)))
            self.transparency_button.setStyleSheet("background-color: #8ab4f8; border-radius: 2px;")
            self.transparency_button.setToolTip("Adjust transparency")
            self.status_bar.showMessage("Window transparency enabled")
            # Show the opacity slider dialog
            self.show_opacity_slider()
        else:
            # Restore full opacity
            self.setWindowOpacity(1.0)
            self.transparency_button.setIcon(QIcon.fromTheme("transparency-off", 
                                         QApplication.style().standardIcon(QStyle.SP_ToolBarHorizontalExtensionButton)))
            self.transparency_button.setStyleSheet("")
            self.transparency_button.setToolTip("Toggle transparency")
            self.status_bar.showMessage("Window transparency disabled")
    
    def show_opacity_slider(self):
        """Show a dialog with a slider to adjust opacity."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Adjust Transparency")
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setModal(False)  # Non-modal dialog
        
        # Apply current theme to dialog
        dialog.setStyleSheet(Themes.get_transparency_dialog_style(
            "dark" if self.current_theme == THEME_DARK else "light"))
        
        # Create layout
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add a label
        label = QLabel("Adjust Window Transparency:")
        layout.addWidget(label)
        
        # Create a slider for opacity
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(40)  # 40% minimum opacity
        slider.setMaximum(100)  # 100% maximum opacity
        slider.setValue(int(self.windowOpacity() * 100))  # Current opacity
        
        # Connect slider to opacity adjustment
        def update_opacity(value):
            opacity = value / 100
            self.setWindowOpacity(opacity)
            # Save the opacity value for later restoration
            self.opacity = opacity
            self.settings.setValue("window_opacity", opacity)
            
        slider.valueChanged.connect(update_opacity)
        layout.addWidget(slider)
        
        # Set dialog size
        dialog.setFixedSize(300, 100)
        
        # Position near the transparency button
        button_pos = self.transparency_button.mapToGlobal(QPoint(0, 0))
        dialog.move(button_pos.x() - 150, button_pos.y() + 30)
        
        # Show the dialog
        dialog.show()
    
    def mousePressEvent(self, event):
        """Handle mouse press events for dragging when window is frameless."""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for custom window dragging."""
        # Only allow dragging if not anchored
        if event.buttons() == Qt.LeftButton and self.drag_position and self.draggable:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Reset drag position when mouse is released."""
        self.drag_position = None
        event.accept()

    def closeEvent(self, event):
        """Save window position and state when closing."""
        # Save window geometry, state, and transparency
        self.settings.setValue("window_geometry", self.saveGeometry())
        self.settings.setValue("window_state", self.saveState())
        self.settings.setValue("is_anchored", self.is_anchored)
        self.settings.setValue("is_pinned", self.is_pinned)
        self.settings.setValue("is_transparent", self.is_transparent)
        self.settings.setValue("window_opacity", self.opacity)
        
        # Continue with normal close event
        super().closeEvent(event)
    
    def restore_window_state(self):
        """Restore window position and state."""
        # Restore geometry if available
        if self.settings.contains("window_geometry"):
            self.restoreGeometry(self.settings.value("window_geometry"))
        
        # Restore state if available
        if self.settings.contains("window_state"):
            self.restoreState(self.settings.value("window_state"))
        
        # Restore pinned state
        if self.settings.value("is_pinned", False, type=bool):
            self.toggle_pin_window()
        
        # Restore anchored state
        if self.settings.value("is_anchored", False, type=bool):
            self.toggle_anchor_window()
        
        # Restore transparency
        if self.settings.value("is_transparent", False, type=bool):
            self.is_transparent = not self.is_transparent  # Toggle will flip this
            self.toggle_transparency()
            # Set saved opacity if available
            if self.settings.contains("window_opacity"):
                opacity = float(self.settings.value("window_opacity", 0.85))
                self.setWindowOpacity(opacity)
                self.opacity = opacity

    def show_error_message(self, title, message):
        """Show an error message to the user."""
        # Use our custom dialog for error messages too
        dialog, button_box = self.create_custom_dialog(title, message, QMessageBox.Critical)
        
        # For error messages, we only need an OK button
        button_box.clear()
        button_box.addButton(QDialogButtonBox.Ok)
        
        dialog.exec_()

