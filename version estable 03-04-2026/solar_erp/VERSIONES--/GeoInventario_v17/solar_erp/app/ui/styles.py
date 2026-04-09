STYLESHEET = """
QMainWindow, QWidget {
    background-color: #F5F6FA;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    color: #2C3E50;
}

/* SIDEBAR */
#sidebar {
    background-color: #1E3A5F;
    min-width: 64px;
    max-width: 230px;
}
QPushButton#nav_btn {
    background-color: transparent;
    color: #BDC3C7;
    text-align: left;
    padding: 12px 20px;
    border: none;
    border-radius: 0px;
    font-size: 12px;
}
QPushButton#nav_btn:hover {
    background-color: #2980B9;
    color: white;
}
QPushButton#nav_btn:checked {
    background-color: #2ECC71;
    color: white;
    font-weight: bold;
    border-left: 4px solid #27AE60;
}

/* CARDS */
QFrame#card {
    background-color: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #DDE2E8;
}
QLabel#card_number {
    font-size: 32px;
    font-weight: bold;
    color: #1E3A5F;
}
QLabel#card_title {
    font-size: 12px;
    color: #7F8C8D;
}

/* TABLES */
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #DDE2E8;
    border-radius: 8px;
    gridline-color: #EEF0F3;
    alternate-background-color: #F8F9FB;
    selection-background-color: #D5E8F8;
    selection-color: #2C3E50;
}
QTableWidget::item {
    padding: 8px 10px;
    border: none;
}
QHeaderView::section {
    background-color: #1E3A5F;
    color: white;
    padding: 10px;
    border: none;
    font-weight: bold;
    font-size: 12px;
}
QHeaderView::section:first {
    border-top-left-radius: 8px;
}
QHeaderView::section:last {
    border-top-right-radius: 8px;
}

/* FORMS */
QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
    background-color: #FFFFFF;
    border: 1px solid #DDE2E8;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #2C3E50;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #2ECC71;
    outline: none;
}
QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}
QComboBox QAbstractItemView {
    background-color: white;
    border: 1px solid #DDE2E8;
    selection-background-color: #2ECC71;
    color: #2C3E50;
}

/* BUTTONS */
QPushButton#btn_primary {
    background-color: #1E3A5F;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 9px 20px;
    font-weight: bold;
}
QPushButton#btn_primary:hover { background-color: #2980B9; }
QPushButton#btn_primary:pressed { background-color: #1A5276; }

QPushButton#btn_success {
    background-color: #2ECC71;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 9px 20px;
    font-weight: bold;
}
QPushButton#btn_success:hover { background-color: #27AE60; }

QPushButton#btn_danger {
    background-color: #E74C3C;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 9px 20px;
    font-weight: bold;
}
QPushButton#btn_danger:hover { background-color: #C0392B; }

QPushButton#btn_warning {
    background-color: #F39C12;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 9px 20px;
    font-weight: bold;
}
QPushButton#btn_warning:hover { background-color: #D68910; }

QPushButton#btn_secondary {
    background-color: #ECF0F1;
    color: #2C3E50;
    border: 1px solid #DDE2E8;
    border-radius: 6px;
    padding: 9px 20px;
}
QPushButton#btn_secondary:hover { background-color: #D5DBDB; }

/* LABELS */
QLabel#page_title {
    font-size: 22px;
    font-weight: bold;
    color: #1E3A5F;
}
QLabel#section_title {
    font-size: 15px;
    font-weight: bold;
    color: #2C3E50;
}
QLabel#badge_danger {
    background-color: #E74C3C;
    color: white;
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: bold;
}
QLabel#badge_success {
    background-color: #2ECC71;
    color: white;
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: bold;
}
QLabel#badge_warning {
    background-color: #F39C12;
    color: white;
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
}
QLabel#badge_info {
    background-color: #3498DB;
    color: white;
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
}

/* SEARCH BAR */
QLineEdit#search_bar {
    background-color: #FFFFFF;
    border: 1px solid #DDE2E8;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 13px;
}
QLineEdit#search_bar:focus {
    border: 2px solid #2ECC71;
}

/* DIALOG */
QDialog {
    background-color: #F5F6FA;
}

/* SCROLLBAR */
QScrollBar:vertical {
    background: #F5F6FA;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #BDC3C7;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #95A5A6;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""
