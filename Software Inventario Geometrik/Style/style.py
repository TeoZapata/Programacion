
BUTTON_TAB_MAIN= """
    QPushButton {
        color: white;
        border-radius: 5px;
        padding: 12px 20px;
        text-align: center;
        font-size: 16px;
        font-weight: bold;
        font-family: 'Arial';
        min-width: 120px;
        background-color: #2c3e50;
        border: none;
    }
    QPushButton:hover {
        color: white;
        border: 2px solid #39ff14; /* Neon green border */
    }
    QPushButton:checked {
        color: white;
        border: 2px solid #7fffd4; /* Neon aquamarine border */
    }
    """

BUTTON_GENERAL_DESIGN= """
    QPushButton {
        border-radius: 5px;
        padding: 12px 20px;
        text-align: center;
        font-size: 16px;
        font-weight: bold;
        font-family: 'Arial';
        min-width: 120px;
        background-color: transparent;
        border: 2px solid #2c3e50; /* Dark blue border */
        border: none;
    }
    QPushButton:hover {
        color: #00B140;
        border: 2px solid #00B140; /* Neon aquamarine border */
    }
    QPushButton:pressed {
        color: #97D700;
        border: 2px solid #39ff14; /* Neon green border */
    }
    """

LABEL_GENERAL_DESIGN= """
    QLabel {
        padding: 5px 5px;
        text-align: center;
        font-size: 16px;
        font-weight: 500;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #2c3e50; /* Dark blue-gray text */
    }
    """


ENTRY_GENERAL_DESIGN= """
    QLineEdit {
        text-align: center;
        font-size: 14px;
        font-weight: 500;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #ecf0f1; /* Light gray text for contrast */
        background-color: #2c3e50; /* Dark blue-gray background */
        border: 2px solid #34495e; /* Slightly lighter b#1E22AAorder for subtle contrast */
        border-radius: 5px;
    }
    QLineEdit:focus {
        font-size: 16px; /* Slightly larger font size on focus */
        color: #BBDDE6; /* Neon aquamarine text color */
        border-radius: 8px;
        border: 3px solid #BBDDE6; /* Neon aquamarine border */aw
        background-color:#2c3e50; /* Slightly lighter background on focus */
    }
    """