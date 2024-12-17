
def checkBill(img):

    import google.generativeai as genai
    import pandas as pd
    import re
    from PIL import Image

    API_KEY = 'AIzaSyCbjnUU79z4mnAo4VVa7QxLSLuOiYNNjlo'
    prompt_cuenta = 'Extraer todos los datos'
    genai.configure(api_key=API_KEY)

    img = Image.open(img)
    model = genai.GenerativeModel(model_name='gemini-1.5-flash')
    response_Cuenta = model.generate_content([prompt_cuenta, img], stream=True)
        
    buffer_cuenta = []
    for chunk in response_Cuenta:
        for part in chunk.parts:
            buffer_cuenta.append(part.text)
    
    return buffer_cuenta

