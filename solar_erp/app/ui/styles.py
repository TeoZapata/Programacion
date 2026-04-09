STYLESHEET = """
QMainWindow, QWidget {
    background-color: #F3F0E8;
    font-family: 'Segoe UI', 'Trebuchet MS', sans-serif;
    font-size: 13px;
    color: #24313A;
}

#sidebar {
    background-color: #14222C;
    min-width: 64px;
    max-width: 230px;
    border-right: 1px solid rgba(201, 182, 142, 0.18);
}
QPushButton#nav_btn {
    background-color: transparent;
    color: #C9D2D8;
    text-align: left;
    padding: 13px 20px;
    border: none;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    margin: 3px 10px;
}
QPushButton#nav_btn:hover {
    background-color: rgba(201, 182, 142, 0.14);
    color: #F7F2E7;
}
QPushButton#nav_btn:checked {
    background-color: #C9B68E;
    color: #14222C;
    font-weight: bold;
    border: 1px solid rgba(20, 34, 44, 0.12);
}

QFrame#card {
    background-color: #FCFAF5;
    border-radius: 18px;
    border: 1px solid #DED6C8;
}
QLabel#card_number {
    font-size: 32px;
    font-weight: 700;
    color: #14222C;
}
QLabel#card_title {
    font-size: 12px;
    color: #7A7468;
}

QTableWidget {
    background-color: #FFFCF7;
    border: 1px solid #DED6C8;
    border-radius: 14px;
    gridline-color: #EEE6D9;
    alternate-background-color: #F7F2E8;
    selection-background-color: #E4D7BC;
    selection-color: #14222C;
}
QTableWidget::item {
    padding: 8px 10px;
    border: none;
}
QHeaderView::section {
    background-color: #1D313C;
    color: #F7F2E7;
    padding: 12px 10px;
    border: none;
    font-weight: bold;
    font-size: 12px;
}
QHeaderView::section:first {
    border-top-left-radius: 14px;
}
QHeaderView::section:last {
    border-top-right-radius: 14px;
}

QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
    background-color: #FFFDF9;
    border: 1px solid #D8CFC0;
    border-radius: 10px;
    padding: 9px 12px;
    font-size: 13px;
    color: #24313A;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #A3875A;
    outline: none;
    background-color: #FFFFFF;
}
QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}
QComboBox QAbstractItemView {
    background-color: #FFFDF9;
    border: 1px solid #D8CFC0;
    selection-background-color: #DCCBAB;
    color: #24313A;
}

QPushButton#btn_primary {
    background-color: #14222C;
    color: #F8F5EE;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: bold;
}
QPushButton#btn_primary:hover { background-color: #1D313C; }
QPushButton#btn_primary:pressed { background-color: #101B22; }

QPushButton#btn_success {
    background-color: #7C8F63;
    color: #F8F5EE;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: bold;
}
QPushButton#btn_success:hover { background-color: #6F8158; }

QPushButton#btn_danger {
    background-color: #A6584B;
    color: #FFF8F5;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: bold;
}
QPushButton#btn_danger:hover { background-color: #954B3F; }

QPushButton#btn_warning {
    background-color: #B78A48;
    color: #FFF9F0;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: bold;
}
QPushButton#btn_warning:hover { background-color: #A97D41; }

QPushButton#btn_secondary {
    background-color: #F6F1E6;
    color: #24313A;
    border: 1px solid #D7CBB9;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
}
QPushButton#btn_secondary:hover { background-color: #ECE2D1; }

QLabel#page_title {
    font-size: 24px;
    font-weight: 700;
    color: #16252F;
}
QLabel#section_title {
    font-size: 15px;
    font-weight: bold;
    color: #24313A;
}
QLabel#badge_danger {
    background-color: #A6584B;
    color: #FFF8F5;
    border-radius: 12px;
    padding: 3px 9px;
    font-size: 11px;
    font-weight: bold;
}
QLabel#badge_success {
    background-color: #7C8F63;
    color: #F8F5EE;
    border-radius: 12px;
    padding: 3px 9px;
    font-size: 11px;
    font-weight: bold;
}
QLabel#badge_warning {
    background-color: #B78A48;
    color: #FFF9F0;
    border-radius: 12px;
    padding: 3px 9px;
    font-size: 11px;
}
QLabel#badge_info {
    background-color: #48697A;
    color: #F6F2EA;
    border-radius: 12px;
    padding: 3px 9px;
    font-size: 11px;
}

QLineEdit#search_bar {
    background-color: #FFFDF9;
    border: 1px solid #D7CBB9;
    border-radius: 22px;
    padding: 9px 16px;
    font-size: 13px;
}
QLineEdit#search_bar:focus {
    border: 2px solid #A3875A;
}

QDialog {
    background-color: #F3F0E8;
}

QScrollBar:vertical {
    background: #EEE6D8;
    width: 10px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #B8AA92;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #9F9078;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""
