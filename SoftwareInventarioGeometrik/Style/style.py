
BUTTON_ADD_MATERIAL= """
    QPushButton {
        background-color: transparent;
        border: 2px solid rgb(74,230,26); /* Green border */
        border-radius: 5px;
        color: Green; /* Green text */
        font-size: 16px;
        font-weight: bold;
        font-family: 'Arial';
        padding: 3px;
        text-align: center;
    }
    QPushButton:hover {
        border: 2px solid rgb(195,204,51); /* Red border */
        color: Green; /* Red text */
        background-color: rgba(255, 0, 0, 0.1); /* Slight red background */
    }
    QPushButton:pressed {
        background-color: rgba(0, 255, 0, 0.2); /* Slight green background */
        border: 2px solid rgb(74,230,26); /* Green border */
        color: Green; /* Green text */
    }
    """
BUTTON_DELETE_MATERIAL= """
    QPushButton {
        background-color: transparent;
        border: 2px solid rgb(217,38,38); /* Green border */
        border-radius: 5px;
        color: rgb(217,38,38); /* Green text */
        font-size: 16px;
        font-weight: bold;
        font-family: 'Arial';
        padding: 3px;
        text-align: center;
    }
    QPushButton:hover {
        border: 2px solid rgb(217,26,230); /* Red border */
        color: rgb(217,26,230); /* Red text */
        background-color: rgba(255, 0, 0, 0.1); /* Slight red background */
    }
    QPushButton:pressed {
        background-color: rgba(0, 255, 0, 0.2); /* Slight green background */
        border: 2px solid rgb(217,38,38); /* Green border */
        color: rgb(217,38,38); /* Green text */
    }
    """
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
ENTRY_ONLY_READ_DESIGN= """
        QLineEdit {
        text-align: center;
        font-size: 14px;
        padding: 5px;
        font-weight: 500;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #ecf0f1; /* Light gray text for contrast */
        background-color:RebeccaPurple; /* Dark blue-gray background */
        border: 2px solid #34495e; /* Slightly lighter b#1E22AAorder for subtle contrast */
        border-radius: 5px;

    } """

ENTRY_GENERAL_DESIGN= """
    QLineEdit {
        text-align: center;
        font-size: 14px;
        padding: 5px;
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
TAB_DESIGN_GENERAL= """
            QTabBar::tab {
            width: 160px;
            background:#dcdcdc;
            border: 1px solid #c0c0c0;
            padding: 10px;
            font-family: Arial, sans-serif;
            font-size: 14px;
            color: #333;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
            background: #99D6EA;
            font-weight: bold;
            color: #000;
            }
            QTabBar::tab:hover {
            font-weight: bold;
            background: #00BF6F;
            color:#F1E6B2;
            }
            QTabWidget::pane {
            border: 1px solid #c0c0c0;
            border-radius: 5px;
            }
        """
TAB_MAIN_DESIGN= """
            QTabBar::tab {
            width: 160px;
            background: #2c3e50; /* Dark blue-gray background */
            border: 1px solid #34495e; /* Slightly lighter gray-blue border */
            padding: 10px;
            font-family: Arial, sans-serif;
            font-size: 14px;
            color: #ecf0f1; /* Light gray text */
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
            background: rgb(94,191,64); /* Slightly lighter gray-blue for the selected tab */
            font-weight: bold;
            color: #ecf0f1; /* Light gray text for contrast */
            }
            QTabBar::tab:hover {
            font-weight: bold;
            background:rgb(80,217,38); /* Slightly brighter gray-blue for hover effect */
            color: #ecf0f1; /* Light gray text */
            }
            QTabWidget::pane {
            border: 1px solid #34495e; /* Slightly lighter gray-blue border */
            border-radius: 5px;
            }
        """

COMBOBOX_GENERAL_DESIGN= """
    QComboBox {
        text-align: center;
        font-size: 14px;
        padding: 5px;
        font-weight: 500;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #ecf0f1; /* Light gray text for contrast */
        background-color: #2c3e50; /* Dark blue-gray background */
        border: 2px solid #34495e; /* Slightly lighter b#1E22AAorder for subtle contrast */
        border-radius: 5px;} 
    QComboBox:focus {
        font-size: 16px; /* Slightly larger font size on focus */
        color: #BBDDE6; /* Neon aquamarine text color */
        border-radius: 8px;
        border: 3px solid #BBDDE6; /* Neon aquamarine border */
        background-color:#2c3e50; /* Slightly lighter background on focus */
    }
    QComboBox::drop-down {
        color : #2c3e50;
        border: none;
    }
    
    """
QDATEEDIT_GENERAL_DESIGN= """
    QDateEdit {
        text-align: center;
        font-size: 14px;
        padding: 5px;
        font-weight: 500;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #ecf0f1; /* Light gray text for contrast */
        background-color: #2c3e50; /* Dark blue-gray background */
        border: 2px solid #34495e; /* Slightly lighter b#1E22AAorder for subtle contrast */
        border-radius: 5px;} """
QTEXT_EDIT_GENERAL_DESIGN = """
    QTextEdit {
        text-align: left;
        font-size: 14px;
        padding: 8px;
        font-weight: 500;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #ecf0f1; /* Light gray text for contrast */
        background-color: #2c3e50; /* Dark blue-gray background */
        border: 2px solid #34495e; /* Slightly lighter border for subtle contrast */
        border-radius: 5px;
    }
    QTextEdit:focus {
        font-size: 16px; /* Slightly larger font size on focus */
        color: #BBDDE6; /* Neon aquamarine text color */
        border-radius: 8px;
        border: 3px solid #BBDDE6; /* Neon aquamarine border */
        background-color: #2c3e50; /* Keep background consistent */
    }
"""

TABLA_DESIGN_GENERAL = """
    QTableWidget {
        background-color: #2c3e50; /* Fondo azul oscuro */
        color: #ecf0f1; /* Texto gris claro */
        font-size: 14px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        border: 2px solid #34495e;
        border-radius: 5px;
        gridline-color: #34495e;
    }
    QHeaderView::section {
        background-color: #34495e; /* Encabezado ligeramente más claro */
        color: #BBDDE6; /* Texto azul claro */
        font-weight: bold;
        font-size: 15px;
        border: 1px solid #2c3e50;
        padding: 6px;
    }
    QTableWidget::item {
        selection-background-color: #99D6EA; /* Celeste para selección */
        selection-color: #2c3e50; /* Texto oscuro al seleccionar */
        padding: 4px;
    }
    QTableCornerButton::section {
        background-color: #34495e;
        border: 1px solid #2c3e50;
    }
"""