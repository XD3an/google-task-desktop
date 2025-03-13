"""
Theme definitions for the Google Tasks Desktop application.
Contains light and dark style definitions.
"""

class Themes:
    """Class containing style definitions for different application themes."""
    
    @staticmethod
    def get_light_style():
        """Return the light theme stylesheet."""
        return """
            /* Main Window */
            QMainWindow {
                background-color: #f8f9fa;
            }
            
            /* Header styles - more compact */
            #headerFrame {
                border: none;
                background-color: transparent;
            }
            
            #titleLabel {
                color: #0b57d0;
                padding: 0px;
            }
            
            #searchHint {
                color: #555;
                font-style: italic;
                font-size: 8pt;
            }
            
            /* Button styles with ultra-compact sizing */
            #buttonContainer {
                background-color: transparent;
                border: none;
            }
            
            QPushButton {
                border: none;
                border-radius: 2px;
                padding: 2px 4px;  /* Minimal padding */
                font-weight: 600;
                color: white;
                min-width: 50px;  /* Extremely small minimum width */
                max-width: 80px;  /* Very small maximum width */
                font-size: 8pt;  /* Smallest readable button text */
            }
            
            #actionButton {
                background-color: #444a50;  /* Darker for better contrast */
            }
            
            #actionButton:hover {
                background-color: #303438;
            }
            
            #primaryButton {
                background-color: #0b57d0;  /* Darker blue for better contrast */
            }
            
            #primaryButton:hover {
                background-color: #0842a0;
            }
            
            #dangerButton {
                background-color: #d93025;  /* Darker red for better contrast */
            }
            
            #dangerButton:hover {
                background-color: #b31412;
            }
            
            #themeButton {
                background-color: #444a50;
            }
            
            #themeButton:hover {
                background-color: #303438;
            }
            
            /* Separator */
            #separator {
                color: #e0e0e0;
                height: 1px;
            }
            
            /* Tree Widget with ultra-compact styling */
            #taskTree {
                border: 1px solid #e0e0e0;
                border-radius: 2px;  /* Nearly square corners */
                background-color: white;
                selection-background-color: #d2e3fc;
                selection-color: #0b57d0;
                padding: 2px 1px 2px 2px;  /* Minimal padding */
                font-size: 8pt;  /* Smaller tree text */
            }
            
            #taskTree::item {
                padding: 2px 1px 2px 2px;  /* Minimal padding on items */
                border-bottom: 1px solid #f5f5f5;  /* Very subtle separator */
                min-height: 18px;  /* Minimal height of tree items */
            }
            
            #taskTree::item:selected {
                background-color: #d2e3fc;
                color: #0b57d0;
                border-left: 2px solid #0b57d0;  /* Thinner selection border */
            }
            
            #taskTree::item:hover:!selected {
                background-color: #f8f9fa;  /* Very subtle hover effect */
            }
            
            /* Status Bar */
            #statusBar {
                background-color: #f8f9fa;
                color: #5f6368;
                border-top: 1px solid #e0e0e0;
                padding: 0px;
                font-size: 7pt;  /* Smallest readable status text */
                max-height: 18px;
            }
            
            /* Progress Bar */
            #progressBar {
                border-radius: 3px;
                background-color: #f0f0f0;
            }
            
            #progressBar::chunk {
                background-color: #1a73e8;
                border-radius: 3px;
            }
            
            /* Context Menu */
            QMenu {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 4px;
            }
            
            QMenu::item {
                padding: 4px 16px 4px 10px;  /* Minimal padding in context menu */
                font-size: 8pt;
            }
            
            QMenu::item:selected {
                background-color: #e8f0fe;
                color: #1a73e8;
            }
            
            /* Dialog styling */
            QDialog {
                background-color: #ffffff;
                border-radius: 8px;
            }
            
            QDialog QLabel {
                color: #202124;
            }
            
            QLineEdit {
                padding: 4px;  /* Smaller input fields */
                border: 1px solid #dadce0;
                border-radius: 4px;
                background-color: #ffffff;
                font-size: 8pt;
            }
            
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                outline: none;
            }
            
            /* Status Bar */
            #statusBar QLabel {
                padding-right: 2px;  /* Reduce right padding in status messages */
            }
            
            /* Pin button style */
            #pinButton, #anchorButton, #transparencyButton {
                border: none;
                background-color: transparent;
                padding: 1px;
            }
            
            #pinButton:hover, #anchorButton:hover, #transparencyButton:hover {
                background-color: #e8f0fe;
                border-radius: 2px;
            }
            
            #pinButton:checked, #anchorButton:checked, #transparencyButton:checked {
                background-color: #d2e3fc;
                border-radius: 2px;
            }
            
            /* Additional style for frameless mode */
            QMainWindow {
                border: 1px solid #e0e0e0; /* Visible border when frameless */
            }
        """
    
    @staticmethod
    def get_dark_style():
        """Return the dark theme stylesheet."""
        return """
            /* Main Window */
            QMainWindow {
                background-color: #1e1e1e;  /* Darker background */
            }
            
            /* Header styles - more compact */
            #headerFrame {
                border: none;
                background-color: transparent;
            }
            
            #titleLabel {
                color: #8ab4f8;
                padding: 0px;
            }
            
            #searchHint {
                color: #aeb9c2;  /* Lighter text for better contrast */
                font-style: italic;
                font-size: 8pt;
            }
            
            /* Button styles with ultra-compact sizing */
            #buttonContainer {
                background-color: transparent;
                border: none;
            }
            
            QPushButton {
                border: none;
                border-radius: 2px;
                padding: 2px 4px;  /* Minimal padding */
                font-weight: 600;  /* Slightly bolder text */
                color: white;
                min-width: 50px;  /* Extremely small minimum width */
                max-width: 80px;  /* Very small maximum width */
                font-size: 8pt;  /* Smallest readable button text */
            }
            
            #actionButton {
                background-color: #5a6069;  /* Brighter for better visibility */
            }
            
            #actionButton:hover {
                background-color: #7b7e82;
            }
            
            #primaryButton {
                background-color: #669df6;  /* Brighter blue for better visibility */
                color: #202124;
            }
            
            #primaryButton:hover {
                background-color: #8ab4f8;
            }
            
            #dangerButton {
                background-color: #f28b82;  /* Brighter red for better visibility */
                color: #202124;
            }
            
            #dangerButton:hover {
                background-color: #f6aea8;
            }
            
            #themeButton {
                background-color: #5a6069;
            }
            
            #themeButton:hover {
                background-color: #7b7e82;
            }
            
            /* Main window background */
            QMainWindow, QDialog {
                background-color: #1e1e1e;  /* Darker for better contrast */
            }
            
            /* Tree Widget with ultra-compact styling */
            #taskTree {
                border: 1px solid #5f6368;
                border-radius: 2px;  /* Nearly square corners */
                background-color: #292a2d;  /* Slightly darker */
                selection-background-color: #4d5156;  /* Higher contrast selection */
                selection-color: #8ab4f8;
                padding: 2px 1px 2px 2px;  /* Minimal padding */
                color: #e8eaed;
                font-size: 8pt;  /* Smaller tree text */
            }
            
            #taskTree::item {
                padding: 2px 1px 2px 2px;  /* Minimal padding on items */
                border-bottom: 1px solid #313236;  /* Very subtle separator */
                min-height: 18px;  /* Minimal height of tree items */
            }
            
            #taskTree::item:selected {
                background-color: #4d5156;
                color: #8ab4f8;
                border-left: 2px solid #8ab4f8;  /* Thinner selection border */
            }
            
            #taskTree::item:hover:!selected {
                background-color: #35363a;  /* Very subtle hover effect */
            }
            
            /* Status Bar */
            #statusBar {
                background-color: #202124;
                color: #9aa0a6;
                border-top: 1px solid #3c4043;
                padding: 0px;
                font-size: 7pt;  /* Smallest readable status text */
                max-height: 18px;
            }
            
            /* Progress Bar */
            #progressBar {
                border-radius: 3px;
                background-color: #3c4043;
            }
            
            #progressBar::chunk {
                background-color: #8ab4f8;
                border-radius: 3px;
            }
            
            /* Context Menu */
            QMenu {
                background-color: #303134;
                border: 1px solid #5f6368;
                border-radius: 4px;
                padding: 4px;
                color: #e8eaed;
            }
            
            QMenu::item {
                padding: 4px 16px 4px 10px;  /* Minimal padding in context menu */
                font-size: 8pt;
            }
            
            QMenu::item:selected {
                background-color: #3c4043;
                color: #8ab4f8;
            }
            
            /* Dialog styling */
            QDialog {
                background-color: #303134;
                border-radius: 8px;
                color: #e8eaed;
            }
            
            QDialog QLabel {
                color: #e8eaed;
            }
            
            QLineEdit {
                padding: 4px;  /* Smaller input fields */
                border: 1px solid #5f6368;
                border-radius: 4px;
                background-color: #303134;
                color: #e8eaed;
                font-size: 8pt;
            }
            
            QLineEdit:focus {
                border: 2px solid #8ab4f8;
                outline: none;
            }
            
            /* Status Bar */
            #statusBar QLabel {
                padding-right: 2px;  /* Reduce right padding in status messages */
            }
            
            /* Pin button style */
            #pinButton, #anchorButton, #transparencyButton {
                border: none;
                background-color: transparent;
                padding: 1px;
            }
            
            #pinButton:hover, #anchorButton:hover, #transparencyButton:hover {
                background-color: #3c4043;
                border-radius: 2px;
            }
            
            #pinButton:checked, #anchorButton:checked, #transparencyButton:checked {
                background-color: #4d5156;
                border-radius: 2px;
            }
            
            /* Additional style for frameless mode */
            QMainWindow {
                border: 1px solid #5f6368; /* Visible border when frameless */
            }
        """

    @staticmethod
    def get_dialog_button_style(theme):
        """Get the button style for dialogs based on theme."""
        if theme == "dark":
            return """
                QPushButton {
                    background-color: #5a6069;
                    color: white;
                    min-width: 80px;
                    min-height: 25px;
                    padding: 6px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #7b7e82;
                }
                QPushButton:default {
                    background-color: #8ab4f8;
                    color: #202124;
                    font-weight: bold;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #e8eaed;
                    color: #202124;
                    min-width: 80px;
                    min-height: 25px;
                    padding: 6px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #d2e3fc;
                }
                QPushButton:default {
                    background-color: #1a73e8;
                    color: white;
                    font-weight: bold;
                }
            """

    @staticmethod
    def get_dialog_style(theme):
        """Get the dialog style based on theme."""
        if theme == "dark":
            return """
                QDialog {
                    background-color: #303134;
                    color: #e8eaed;
                    border: 1px solid #5f6368;
                }
            """
        else:
            return """
                QDialog {
                    background-color: white;
                    color: #202124;
                }
            """
            
    @staticmethod
    def get_anchored_style(theme):
        """Get the style for anchored (frameless) window."""
        if theme == "dark":
            return """
                QMainWindow {
                    border: 1px solid #5f6368;
                    border-radius: 12px;
                    background-clip: border;
                }
            """
        else:
            return """
                QMainWindow {
                    border: 1px solid #e0e0e0;
                    border-radius: 12px;
                    background-clip: border;
                }
            """
    
    @staticmethod
    def get_transparency_dialog_style(theme):
        """Get the style for transparency adjustment dialog."""
        if theme == "dark":
            return """
                QDialog {
                    background-color: #303134;
                    color: #e8eaed;
                    border: 1px solid #5f6368;
                    border-radius: 4px;
                }
                QLabel { color: #e8eaed; }
                QSlider::handle { background-color: #8ab4f8; }
            """
        else:
            return """
                QDialog {
                    background-color: #ffffff;
                    color: #202124;
                    border: 1px solid #dadce0;
                    border-radius: 4px;
                }
                QLabel { color: #202124; }
                QSlider::handle { background-color: #1a73e8; }
            """
