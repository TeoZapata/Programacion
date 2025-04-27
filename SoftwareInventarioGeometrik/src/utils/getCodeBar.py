from random import randint
from barcode import Code128
from barcode.writer import ImageWriter
from random import choice
from string import ascii_uppercase
def getCodeBar():
    """Genera un código de barras en formato letra-números-letra (ejemplo: X785163A)."""

    code = (
        choice(ascii_uppercase)  # Primera letra
        + "".join(str(randint(0, 9)) for _ in range(6))  # Seis dígitos
        + choice(ascii_uppercase)  # Última letra
    )
    
    return code
