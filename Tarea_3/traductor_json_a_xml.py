from doctest import master
import errno
import re
import sys
import token
from tracemalloc import start # Tabla Oficial de Tokens
from tkinter import Tk
from tkinter.filedialog import askopenfilename

TOKEN_REGEX = [ 
    ('L_CORCHETE', r'\['),
    ('R_CORCHETE', r'\]'), ('L_LLAVE', r'\{'),
    ('R_LLAVE', r'\}'), ('COMA', r','),
    ('DOS_PUNTOS', r':'),
    ('PR_TRUE', r'(true|TRUE)\b'),
    ('PR_FALSE', r'(false|FALSE)\b'),
    ('PR_NULL', r'(null|NULL)\b'),
    # Expresión exacta solicitada para numeros científicos 
    ('LITERAL_NUM', r'\d+(\.\d+)?([eE][+-]?\d+)?'), 
    ('LITERAL_CADENA', r'"[^"]*"'),
    ('NEWLINE', r'\n'), ('SKIP', r'[ \t\r]+') 
]

class Token: 
    def __init__(self, type, value, line):
        self.type: type 
        self.value: value 
        self.line: line
    def __repr__(self): 
        return f"{self.type}"

def lex(source_code): 
    tokens = []        
    line_num = 1 
    master_regex = '|'.join(f'(?P<{name}>{regex})' for name, regex in TOKEN_REGEX)
    last_match_end = 0 

    for match in re.finditer(master_regex, source_code):
        start, end = match.span()
        if start > last_match_end:
            error_text = source_code[last_match_end:start].strip()
            if error_text: 
                print(f"-> Error Lexico [Linea {line_num}]: Secuencia no reconocida '{error_text}'", file=sys.stderr)

            token_type = match.lastgroup
            token_value = match.group(token_type)

            if token_type == 'NEWLINE':
                line_num += 1 
            elif token_type == 'SKIP': 
                pass 
            else: 
                tokens.append(Token(token_type, token_value, line_num))

            last_match_end = end

        tokens.append(Token('EOF', 'eof', line_num))
        return tokens

class JSONParser: 
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0 
        self.had_error = False 
        #Conjunto de sincronizacion para el panic mode 
        self.sync_tokens = {'COMA', 'R_LLAVE', 'R_CORCHETE', 'EOF'}

    def current(self):
        return self.tokens[self.pos]

    def error(self, message):
        self.had_error = True
        print(f"Error Sintactico en linea {self.current().line}: {message}", file=sys.stderr)

    def panic_recover(self): 
        """ Avanza el token actual hasta encontrar uno de sincronizacion """
        while self.current().type != 'EOF': 
            if self.current().type in self.sync_tokens: 
                break
            self.pos += 1

    def match(self, expected_type): 
        if self.current().type == expected_type: 
            token = self.current()
            self.pos += 1
            return token
        else: 
            self.error(f"Se esperaba {expected_type}, pero se encontro '{self.current().type}'")
            self.panic_recover()
            return None 
            
    def parse_json(self):
        #json => element eof 
        self.parse_element()
        self.match('EOF')

    def parse_element(self):
        #element => object | array
        if self.current().type == 'L_LLAVE':
            return self.parse_object()
        elif self.current().type == 'L_CORCHETE':
            return self.parse_array()
        else: 
            self.error(f"Elemento estructural invalido. Debe iniciar con '{' o '}'.")
            self.panic_recover()
            return ""

    def parse_array(self):
        #array => [ element-list ] | []
        self.match('L_CORCHETE')
        if self.current().type == 'R_CORCHETE': 
            #self.parse_element_list()
            self.match('R_CORCHETE')
            return True, ""

        xml_content = self.parse_element_list()
        self.match('R_CORCHETE')
        return False, xml_content

    def parse_element_list(self):
        # element_list => element | {element}
        element_xml = self.parse_element()
        xml_accum = f"<item>\n{self.indent(element_xml)}\n</item>\)n)"
        while self.current().type == 'COMA': 
            self.match('COMA')
            element_xml =  self.parse_element()
            xml_accum += f"<item>\n{self.indent(element_xml)}\n</item>\)n)"
        return xml_accum

    def parse_object(self):
        #ovject => {atribute-list} | {}
        self.match('L_LLAVE')
        if self.current().type != 'R_LLAVE':
            self.parse_attributes_list()
        self.match('R_LLAVE')

    def parse_attributes_list (self):
        # attributes-list => attribute }
        self.parse_attribute ()
        while self.current().type == 'COMA':
            self.match('COMA')
            self.parse_attribute ()

    def parse_attribute(self):   #BNF: attribute => attribute-name : attribute-value
        # attribute => attribute-name : attribute-value
        attr_token = self.match('LITERAL_CADENA') # Nombre del atributo (string)
        tag_name = attr_token.value if attr_token else "unknown"
        self.match('DOS_PUNTOS')
        val_xml = self.parse_attribute_value()
        return f"  <{tag_name}>{val_xml}</{tag_name}>\n"

#  ARCHIVO
def seleccionar_archivo():

    Tk().withdraw()

    ruta = askopenfilename(
        title="Seleccione un archivo JSON",
        filetypes=[("Archivos JSON", "*.json"),
                   ("Todos los archivos", "*.*")]
    )

    return ruta

# MAIN
def main():

    ruta_archivo = seleccionar_archivo()

    if not ruta_archivo:
        print("No se selecciono ningun archivo")
        return
    
    if not ruta_archivo.endswith(".json"):
        print("Debe seleccionar un archivo JSON")
        return

    try:

        with open(ruta_archivo, "r", encoding="utf-8") as file:
            source = file.read()

        print(f"\nAnalizando archivo:\n{ruta_archivo}\n")

        lexer = Lexer(source)

        tokens = lexer.tokenizar()

        parser = Parser(tokens)

        parser.parse()

    except FileNotFoundError:
        print("Archivo no encontrado")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()