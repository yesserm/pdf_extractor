import pdfplumber
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
from collections import defaultdict
import re
document_path = "./samples/id.pdf"


# Configurar parámetros para mejorar la alineación

laparams = LAParams(
    line_overlap=0.5,  # Ajusta detección de líneas superpuestas
    char_margin=2.0,
    word_margin=0.1,   # Espaciado entre palabras para mantener estructura
    line_margin=0.5,   # Controla cómo se agrupan líneas en párrafos
    boxes_flow=0.5     # Controla la direccionalidad del texto
)

laparams_t = {
    "line_overlap":0.1,
    "char_margin":50.0,
    "word_margin":0.9,
    "line_margin":0.5,
    "boxes_flow":None,  # No fuerza ninguna orientación de texto
    "detect_vertical":False,  # No trata de detectar texto vertical
    "all_texts":False  # No extrae texto de todas las áreas del PDF
}
doc = pdfplumber.open(document_path)
texto = extract_text(document_path, laparams=laparams)#.splitlines()

page = doc.pages[0]
words = []
sizes = set()
fontfaces = set()
pattern = r"(\b[\D\s]+):\s+(.+)"

#text = page.extract_text(layout=True)
#print(page.extract_text_simple().split('\n')[2:30])
#print(page.extract_tables()[0])
lines = page.extract_text_lines(layout=True, strip=True, return_chars=False, x_tolerance=3)
words = page.extract_words(extra_attrs=['size'])


    
[print(line.get('text')) for i, line in enumerate(lines) if i > 8 and i < 50]
#print(texto)

#[print(re.split(r"\s{2,}", line.get('text').strip()) ) for line in lines]
#print(page.extract_words(keep_blank_chars=True, extra_attrs=['size', 'fontname', 'stroking_pattern'])[2:6])

#sizes = {word.get('size', 0) for word in words}
#fontfaces = {word.get('fontname', '0') for word in words}
#print(fontfaces)
#{'AAAAAB+Gotham_Book', 'AAAAAD+Gotham_Medium', 'AAAAAF+Arial'}
#[print(word.get('text', '')) for word in words if word.get('fontname') == 'AAAAAF+Arial']

#print(list(sizes))

#[print(word.get('text', '')) for word in words if word.get('size') == 8.950000000000003]
"""
im = doc.pages[0].to_image(resolution=150)
im.draw_rects(doc.pages[0].extract_words())
im.save('object.jpg')
"""

# Agrupar por 'bottom'
grupos = defaultdict(list)
for item in words:
    grupos[item['bottom']].append(item)

# Ordenar cada grupo por 'x0'
resultado = []
for bottom in sorted(grupos.keys()):
    grupo_ordenado = sorted(grupos[bottom], key=lambda x: x['x0'])
    resultado.append(grupo_ordenado)

# Si querés una sola lista aplanada:
words = [item for grupo in resultado for item in grupo]

# Mostrar resultado
#print(resultado_aplanado)

#[print(word) for i, word  in enumerate(resultado_aplanado) if i < 15 and i > 8 ]
#[print(word.get('text', ''), "{:.1f}".format(word.get('x0', 0)), "{:.1f}".format(word.get('width', 0)+2.4), "{:.1f}".format(word.get('y0', 0))) for i, word  in enumerate(words) if i < 30]
space_size = 2.4
min_tolerance = 0.5
keys = dict()

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
        prev_word_width = format_float(words[i].get('width', 0) + space_size)
        expected_prev_word_pos = format_float(current_word_pos - prev_word_width) 
        
        if  abs(expected_prev_word_pos - prev_word_pos) < min_tolerance:
            key = words[i].get('text', '') + ' ' + key
            
        else:
            break
        
    return key

def create_value(init, words):
    value = ''
    limit = init + 10
    step_by = 1
    init = init + 1
    
    #print(words[init].get('text', '0'))
    for i in range(init, limit, step_by): 
        current_word_pos = format_float(words[i].get('x0', 0))
        current_word_width = format_float(words[i].get('width', 0) + space_size)
        next_word_pos = format_float(words[i+1].get('x0', 0))

        expected_next_word_pos = format_float(current_word_pos + current_word_width)
        
        #print (current_word_pos,', ', current_word_width,', ', next_word_pos,', ', expected_next_word_pos,', ',abs(expected_next_word_pos - next_word_pos) < min_tolerance,', ',words[i].get('text', '0'),', ',abs(expected_next_word_pos - next_word_pos))
        value = value +' '+ words[i].get('text', '')
        if not abs(expected_next_word_pos - next_word_pos) < min_tolerance:
            break
            
    return value

def move(last_word, current_index, words, move_backwards=True):
    #print(last_word)
    
    key =''
    value = ''
    key = create_key(current_index, words ) + last_word
    #print('The key '+key)
    value = create_value(current_index, words)
    #print('The value '+value)
    keys[key.strip()] = value.strip()

#last_title = 0
for index, word in enumerate(words):
    """
    if word.get('width', 0) > last_title:
        print(word.get('text', ''), '\n') 
        last_title = word.get('width', 0)"
    """

    if ':' not in word.get('text', '') or word.get('text', '').count(':') != 1: 
        continue

    move(word.get('text', ''), index, words)
    #print(word.get('text', ''), index)
    

print (keys)