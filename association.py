import pdfplumber
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
from collections import defaultdict
import re

def configurar_laparams():
    return LAParams(
        line_overlap=0.5,  
        char_margin=2.0,
        word_margin=0.1,   
        line_margin=0.5,   
        boxes_flow=0.5     
    )

def configurar_laparams_t():
    return {
        "line_overlap":0.1,
        "char_margin":50.0,
        "word_margin":0.9,
        "line_margin":0.5,
        "boxes_flow":None,  
        "detect_vertical":False,  
        "all_texts":False  
    }

def cargar_documento(ruta):
    doc = pdfplumber.open(ruta)
    laparams = configurar_laparams()
    texto = extract_text(ruta, laparams=laparams)
    return doc, texto

def extraer_palabras_y_lineas(page):
    lines = page.extract_text_lines(layout=True, strip=True, return_chars=False, x_tolerance=3)
    words = page.extract_words(extra_attrs=['size'])
    return lines, words

def agrupar_por_posicion(words):
    grupos = defaultdict(list)
    for item in words:
        grupos[item['bottom']].append(item)

    resultado = []
    for bottom in sorted(grupos.keys()):
        grupo_ordenado = sorted(grupos[bottom], key=lambda x: x['x0'])
        resultado.append(grupo_ordenado)

    return [item for grupo in resultado for item in grupo]

def format_float(number):
    return float("{:.1f}".format(number))

def create_key(init, words):
    key = ''
    limit = -1 
    step_by = -1 
    init = init - 1 

    for i in range(init, limit, step_by): 
        current_word_pos = format_float(words[i+1].get('x0', 0))
        prev_word_pos = format_float(words[i].get('x0', 0))
        prev_word_width = format_float(words[i].get('width', 0) + 2.4)
        expected_prev_word_pos = format_float(current_word_pos - prev_word_width) 
        
        if abs(expected_prev_word_pos - prev_word_pos) < 0.5:
            key = words[i].get('text', '') + ' ' + key
        else:
            break
        
    return key.strip()

def create_value(init, words):
    value = ''
    limit = init + 10
    step_by = 1
    init = init + 1

    for i in range(init, limit, step_by): 
        current_word_pos = format_float(words[i].get('x0', 0))
        current_word_width = format_float(words[i].get('width', 0) + 2.4)
        next_word_pos = format_float(words[i+1].get('x0', 0))

        expected_next_word_pos = format_float(current_word_pos + current_word_width)
        value += ' ' + words[i].get('text', '')

        if not abs(expected_next_word_pos - next_word_pos) < 0.5:
            break
            
    return value.strip()

def procesar_documento(document_path):
    doc, texto = cargar_documento(document_path)
    page = doc.pages[0]
    lines, words = extraer_palabras_y_lineas(page)
    words = agrupar_por_posicion(words)
    
    keys = dict()
    
    for index, word in enumerate(words):
        if ':' not in word.get('text', '') or word.get('text', '').count(':') != 1: 
            continue

        key = create_key(index, words) + ' ' + word.get('text', '')
        value = create_value(index, words)
        keys[key.strip()] = value.strip()

    print(keys)

procesar_documento("./samples/id.pdf")