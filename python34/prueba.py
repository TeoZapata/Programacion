import PyPDF2
with open('13.pdf', 'rb') as file:
    reader = PyPDF2.PdfReader(file)

    print(reader.pages.extract_text())
    