
from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Style import  *


def clear_entry(listaWidget: list) -> None:

    """Limpia el campo de entrada y establece un nuevo marcador de posición."""
    lista:list[QLineEdit] = listaWidget
    for i in lista:
        i.clear()
        i.setStyleSheet(ENTRY_GENERAL_DESIGN)
