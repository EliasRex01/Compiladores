from doctest import master
import re
import sys
import token
from tracemalloc import start # Tabla Oficial de Tokens
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
            