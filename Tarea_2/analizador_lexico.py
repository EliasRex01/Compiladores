import re
from enum import Enum

# TOKEN TYPES
class TokenType(Enum):
    L_CORCHETE = "["
    R_CORCHETE = "]"
    L_LLAVE = "{"
    R_LLAVE = "}"
    COMA = ","
    DOS_PUNTOS = ":"

    LITERAL_CADENA = "STRING"
    LITERAL_NUM = "NUMBER"

    PR_TRUE = "TRUE"
    PR_FALSE = "FALSE"
    PR_NULL = "NULL"
    
    EOF = "EOF"


# TOKEN
class Token:
    def __init__(self, type_, lexeme, line):
        self.type = type_
        self.lexeme = lexeme
        self.line = line

    def __str__(self):
        return f"{self.type.name}('{self.lexeme}')"


# LEXER
class Lexer:

    token_specification = [
        ('STRING', r'"[^"]*"'),
        ('NUMBER', r'\d+(\.\d+)?((e|E)(\+|-)?\d+)?'),

        ('TRUE', r'true|TRUE'),
        ('FALSE', r'false|FALSE'),
        ('NULL', r'null|NULL'),

        ('L_CORCHETE', r'\['),
        ('R_CORCHETE', r'\]'),

        ('L_LLAVE', r'\{'),
        ('R_LLAVE', r'\}'),

        ('COMA', r','),
        ('DOS_PUNTOS', r':'),

        ('SKIP', r'[ \t]+'),
        ('NEWLINE', r'\n'),

        ('MISMATCH', r'.'),
    ]

    def __init__(self, text):
        self.text = text

    def tokenize(self):

        tokens = []
        line_num = 1

        tok_regex = '|'.join(
            f'(?P<{name}>{regex})'
            for name, regex in self.token_specification
        )

        for mo in re.finditer(tok_regex, self.text):

            kind = mo.lastgroup
            value = mo.group()

            if kind == 'NEWLINE':
                line_num += 1

            elif kind == 'SKIP':
                continue

            elif kind == 'STRING':
                tokens.append(Token(
                    TokenType.LITERAL_CADENA,
                    value,
                    line_num
                ))

            elif kind == 'NUMBER':
                tokens.append(Token(
                    TokenType.LITERAL_NUM,
                    value,
                    line_num
                ))

            elif kind == 'TRUE':
                tokens.append(Token(
                    TokenType.PR_TRUE,
                    value,
                    line_num
                ))

            elif kind == 'FALSE':
                tokens.append(Token(
                    TokenType.PR_FALSE,
                    value,
                    line_num
                ))

            elif kind == 'NULL':
                tokens.append(Token(
                    TokenType.PR_NULL,
                    value,
                    line_num
                ))

            elif kind == 'L_CORCHETE':
                tokens.append(Token(
                    TokenType.L_CORCHETE,
                    value,
                    line_num
                ))

            elif kind == 'R_CORCHETE':
                tokens.append(Token(
                    TokenType.R_CORCHETE,
                    value,
                    line_num
                ))

            elif kind == 'L_LLAVE':
                tokens.append(Token(
                    TokenType.L_LLAVE,
                    value,
                    line_num
                ))

            elif kind == 'R_LLAVE':
                tokens.append(Token(
                    TokenType.R_LLAVE,
                    value,
                    line_num
                ))

            elif kind == 'COMA':
                tokens.append(Token(
                    TokenType.COMA,
                    value,
                    line_num
                ))

            elif kind == 'DOS_PUNTOS':
                tokens.append(Token(
                    TokenType.DOS_PUNTOS,
                    value,
                    line_num
                ))

            elif kind == 'MISMATCH':
                print(f"ERROR LÉXICO línea {line_num}: '{value}'")

        tokens.append(Token(TokenType.EOF, "EOF", line_num))

        return tokens


# PARSER
class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.errors = []

    # UTILIDADES
    def peek(self):
        return self.tokens[self.current]

    def advance(self):

        if self.current < len(self.tokens) - 1:
            self.current += 1

    def match(self, token_type):

        if self.peek().type == token_type:
            self.advance()

        else:
            self.error(
                f"Se esperaba {token_type.name}"
            )
            self.panic_mode()

    def error(self, message):

        token = self.peek()

        msg = (
            f"[Línea {token.line}] "
            f"Error sintáctico: {message}. "
            f"Encontrado: '{token.lexeme}'"
        )

        self.errors.append(msg)

    # PANIC MODE
    def panic_mode(self):

        sync_tokens = {
            TokenType.COMA,
            TokenType.R_LLAVE,
            TokenType.R_CORCHETE
        }

        while (
                self.peek().type not in sync_tokens
                and self.peek().type != TokenType.EOF
        ):
            self.advance()

    # GRAMÁTICA
    def parse(self):

        self.json()

        if self.peek().type != TokenType.EOF:
            self.error("Se esperaba EOF")

        if not self.errors:
            print("JSON SINTACTICAMENTE CORRECTO")

        else:
            print("\nERRORES ENCONTRADOS:\n")

            for error in self.errors:
                print(error)

    def json(self):
        self.element()

    def element(self):

        if self.peek().type == TokenType.L_LLAVE:
            self.object()

        elif self.peek().type == TokenType.L_CORCHETE:
            self.array()

        else:
            self.error(
                "Se esperaba objeto o arreglo"
            )
            self.panic_mode()

    def object(self):

        self.match(TokenType.L_LLAVE)

        if self.peek().type != TokenType.R_LLAVE:
            self.attributes_list()

        self.match(TokenType.R_LLAVE)

    def attributes_list(self):

        self.attribute()

        while self.peek().type == TokenType.COMA:
            self.match(TokenType.COMA)
            self.attribute()

    def attribute(self):

        self.match(TokenType.LITERAL_CADENA)

        self.match(TokenType.DOS_PUNTOS)

        self.attribute_value()

    def attribute_value(self):

        token = self.peek().type

        if token == TokenType.L_LLAVE:
            self.object()

        elif token == TokenType.L_CORCHETE:
            self.array()

        elif token == TokenType.LITERAL_CADENA:
            self.match(TokenType.LITERAL_CADENA)

        elif token == TokenType.LITERAL_NUM:
            self.match(TokenType.LITERAL_NUM)

        elif token == TokenType.PR_TRUE:
            self.match(TokenType.PR_TRUE)

        elif token == TokenType.PR_FALSE:
            self.match(TokenType.PR_FALSE)

        elif token == TokenType.PR_NULL:
            self.match(TokenType.PR_NULL)

        else:
            self.error("Valor inválido")
            self.panic_mode()

    def array(self):

        self.match(TokenType.L_CORCHETE)

        if self.peek().type != TokenType.R_CORCHETE:
            self.element_list()

        self.match(TokenType.R_CORCHETE)

    def element_list(self):

        self.element()

        while self.peek().type == TokenType.COMA:
            self.match(TokenType.COMA)
            self.element()


# MAIN
def main():

    try:

        with open("input.json", "r", encoding="utf-8") as file:
            source = file.read()

        lexer = Lexer(source)

        tokens = lexer.tokenize()

        parser = Parser(tokens)

        parser.parse()

    except FileNotFoundError:
        print("No se encontro input.json")


if __name__ == "__main__":
    main()