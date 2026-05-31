import re
import sys
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# TOKEN
class Token:
    def __init__(self, tipo_token, valor, linea):
        self.tipo = tipo_token
        self.valor = valor
        self.linea = linea

    def __repr__(self):
        return f"{self.tipo}('{self.valor}')"

# LEXER
TOKEN_REGEX = [
    ('L_CORCHETE', r'\['),
    ('R_CORCHETE', r'\]'),
    ('L_LLAVE', r'\{'),
    ('R_LLAVE', r'\}'),
    ('COMA', r','),
    ('DOS_PUNTOS', r':'),
    ('PR_TRUE', r'(true|TRUE)\b'),
    ('PR_FALSE', r'(false|FALSE)\b'),
    ('PR_NULL', r'(null|NULL)\b'),
    ('LITERAL_NUM', r'\d+(\.\d+)?([eE][+-]?\d+)?'),
    ('LITERAL_CADENA', r'"[^"]*"'),
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t\r]+')
]


def lex(source_code):
    tokens = []
    line_num = 1
    master_regex = '|'.join(f'(?P<{name}>{regex})'for name, regex in TOKEN_REGEX)
    last_match_end = 0

    for match in re.finditer(master_regex, source_code):
        start, end = match.span()

        if start > last_match_end:
            error_text = source_code[last_match_end:start]
            if error_text.strip():
                print(f"ERROR LEXICO [Linea {line_num}] "
                    f"Secuencia inválida: '{error_text.strip()}'",
                    file=sys.stderr
                )

        tipo_token = match.lastgroup
        token_value = match.group(tipo_token)

        if tipo_token == 'NEWLINE':
            line_num += 1

        elif tipo_token == 'SKIP':
            pass

        else:
            tokens.append(Token(tipo_token,token_value,line_num))

        last_match_end = end

    if last_match_end < len(source_code):
        remaining = source_code[last_match_end:]
        if remaining.strip():
            print(
                f"ERROR LEXICO [Linea {line_num}] "
                f"Secuencia invalida: '{remaining.strip()}'",
                file=sys.stderr
            )

    tokens.append(Token('EOF', 'eof', line_num))
    return tokens

# PARSER + TRADUCTOR
class JSONParser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.had_error = False
        self.sync_tokens = {'COMA','R_LLAVE','R_CORCHETE','EOF'}

    def current(self):
        return self.tokens[self.pos]

    def error(self, message):
        self.had_error = True
        print(
            f"ERROR SINTACTICO [Línea {self.current().linea}] {message}",
            file=sys.stderr
        )

    def panic_recover(self):

        while self.current().tipo != 'EOF':

            if self.current().tipo in self.sync_tokens:
                return

            self.pos += 1

    def match(self, expected):

        if self.current().tipo == expected:

            token = self.current()
            self.pos += 1
            return token

        self.error(f"Se esperaba {expected}, se encontro {self.current().tipo}")
        self.panic_recover()
        return None

    # json => element eof
    def parse_json(self):
        xml = self.parse_element()
        self.match('EOF')
        return xml

    # element => object | array
    def parse_element(self):

        if self.current().tipo == 'L_LLAVE':
            return self.parse_object()

        elif self.current().tipo == 'L_CORCHETE':
            return self.parse_array()

        self.error("Se esperaba '{' o '['")
        self.panic_recover()
        return ""

    # object => { attributes-list } | {}
    def parse_object(self):
        self.match('L_LLAVE')
        xml = ""

        if self.current().tipo != 'R_LLAVE':
            xml += self.parse_attributes_list()

        self.match('R_LLAVE')
        return xml

    # attributes-list
    def parse_attributes_list(self):

        xml = self.parse_attribute()

        while self.current().tipo == 'COMA':
            self.match('COMA')
            xml += self.parse_attribute()

        return xml

    # attribute
    def parse_attribute(self):
        attr_token = self.match('LITERAL_CADENA')
        tag_name = "unknown"
        if attr_token: tag_name = attr_token.valor.strip('"')
        self.match('DOS_PUNTOS')

        # Caso especial para arrays
        if self.current().tipo == 'L_CORCHETE':
            value_xml = self.parse_array()

            if value_xml.strip() == "":
                return f"<{tag_name}/>\n"

            return (f"<{tag_name}>\n"f"{value_xml}"f"</{tag_name}>\n")

        value_xml = self.parse_attribute_value()

        if value_xml.strip() == "":
            return f"<{tag_name}/>\n"

        return (f"<{tag_name}>"f"{value_xml}"f"</{tag_name}>\n")

    # attribute-value
    def parse_attribute_value(self):

        token = self.current()

        if token.tipo == 'LITERAL_CADENA':
            self.match('LITERAL_CADENA')
            return token.valor

        elif token.tipo == 'LITERAL_NUM':
            self.match('LITERAL_NUM')
            return token.valor

        elif token.tipo == 'PR_TRUE':
            self.match('PR_TRUE')
            return "true"

        elif token.tipo == 'PR_FALSE':
            self.match('PR_FALSE')
            return "false"

        elif token.tipo == 'PR_NULL':
            self.match('PR_NULL')
            return "null"

        elif token.tipo == 'L_LLAVE':
            return self.parse_object()

        elif token.tipo == 'L_CORCHETE':
            return self.parse_array()

        self.error("Valor inválido")
        self.panic_recover()
        return ""

    # array => [ element-list ] | []
    def parse_array(self):

        self.match('L_CORCHETE')

        if self.current().tipo == 'R_CORCHETE':
            self.match('R_CORCHETE')
            return ""

        xml = self.parse_element_list()
        self.match('R_CORCHETE')
        return xml

    # element-list
    def parse_element_list(self):
        xml = ""
        item_xml = self.parse_element()
        xml += ("<item>\n"f"{item_xml}""</item>\n")

        while self.current().tipo == 'COMA':
            self.match('COMA')
            item_xml = self.parse_element()
            xml += ("<item>\n"f"{item_xml}""</item>\n")
        return xml

# SELECCION DE ARCHIVO
def seleccionar_archivo():
    Tk().withdraw()
    ruta = askopenfilename(
        title="Seleccione un archivo",
        filetypes=[
            ("Archivos JSON", "*.json"),
            ("Archivos de Texto", "*.txt"),
            ("Todos los archivos", "*.*")
        ]
    )
    return ruta

# MAIN
def main():
    ruta = seleccionar_archivo()

    if not (ruta.lower().endswith(".json") or
        ruta.lower().endswith(".txt")):
        print("Debe seleccionar un archivo .json o .txt")
        return

    try:
        with open(ruta, "r", encoding="utf-8") as file:
            source = file.read()

        print("\nAnalizando:")
        print(ruta)
        tokens = lex(source)
        parser = JSONParser(tokens)
        xml = parser.parse_json()

        if parser.had_error:
            print("\nSe encontraron errores.""\nNo se genero XML.")
            return

        salida = ruta.rsplit(".", 1)[0] + ".xml"

        with open(salida,"w",encoding="utf-8") as out:
            out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            out.write(xml)

        print("\nXML generado correctamente:")
        print(salida)

    except FileNotFoundError:
        print("Archivo no encontrado.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()