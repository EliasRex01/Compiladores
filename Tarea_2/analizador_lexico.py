import re
from enum import Enum

# TIPOS DE TOKENS
class Tipo_Token(Enum):
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
    def __init__(self, tipo, lexema, linea):
        self.tipo = tipo
        self.lexema = lexema
        self.linea = linea

    def __str__(self):
        return f"{self.tipo.name}('{self.lexema}')"


# LEXER
class Lexer:

    reglas_tokenizacion = [
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

    def __init__(self, texto):
        self.texto = texto

    def tokenizar(self):

        tokens = []
        numero_linea = 1

        token_regex = '|'.join(
            f'(?P<{name}>{regex})'
            for name, regex in self.reglas_tokenizacion
        )

        for mo in re.finditer(token_regex, self.texto):

            categoria = mo.lastgroup
            valor = mo.group()

            if categoria == 'NEWLINE':
                numero_linea += 1

            elif categoria == 'SKIP':
                continue

            elif categoria == 'STRING':
                tokens.append(Token(
                    Tipo_Token.LITERAL_CADENA,
                    valor,
                    numero_linea
                ))

            elif categoria == 'NUMBER':
                tokens.append(Token(
                    Tipo_Token.LITERAL_NUM,
                    valor,
                    numero_linea
                ))

            elif categoria == 'TRUE':
                tokens.append(Token(
                    Tipo_Token.PR_TRUE,
                    valor,
                    numero_linea
                ))

            elif categoria == 'FALSE':
                tokens.append(Token(
                    Tipo_Token.PR_FALSE,
                    valor,
                    numero_linea
                ))

            elif categoria == 'NULL':
                tokens.append(Token(
                    Tipo_Token.PR_NULL,
                    valor,
                    numero_linea
                ))

            elif categoria == 'L_CORCHETE':
                tokens.append(Token(
                    Tipo_Token.L_CORCHETE,
                    valor,
                    numero_linea
                ))

            elif categoria == 'R_CORCHETE':
                tokens.append(Token(
                    Tipo_Token.R_CORCHETE,
                    valor,
                    numero_linea
                ))

            elif categoria == 'L_LLAVE':
                tokens.append(Token(
                    Tipo_Token.L_LLAVE,
                    valor,
                    numero_linea
                ))

            elif categoria == 'R_LLAVE':
                tokens.append(Token(
                    Tipo_Token.R_LLAVE,
                    valor,
                    numero_linea
                ))

            elif categoria == 'COMA':
                tokens.append(Token(
                    Tipo_Token.COMA,
                    valor,
                    numero_linea
                ))

            elif categoria == 'DOS_PUNTOS':
                tokens.append(Token(
                    Tipo_Token.DOS_PUNTOS,
                    valor,
                    numero_linea
                ))

            elif categoria == 'MISMATCH':
                print(f"ERROR LEXICO linea {numero_linea}: '{valor}'")

        tokens.append(Token(Tipo_Token.EOF, "EOF", numero_linea))

        return tokens


# PARSER
class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.actual = 0
        self.errores = []

    # UTILIDADES
    def mirar(self):
        return self.tokens[self.actual]

    def avanzar(self):

        if self.actual < len(self.tokens) - 1:
            self.actual += 1

    def match(self, tipo_token):

        if self.mirar().tipo == tipo_token:
            self.avanzar()

        else:
            self.error(
                f"Se esperaba {tipo_token.name}"
            )
            self.panic_mode()

    def error(self, message):

        token = self.mirar()

        msg = (
            f"[Línea {token.linea}] "
            f"Error sintáctico: {message}. "
            f"Encontrado: '{token.lexema}'"
        )

        self.errores.append(msg)

    # PANIC MODE
    def panic_mode(self):

        tokens_sincronizantes = {
            Tipo_Token.COMA,
            Tipo_Token.R_LLAVE,
            Tipo_Token.R_CORCHETE
        }

        while (
                self.mirar().tipo not in tokens_sincronizantes
                and self.mirar().tipo != Tipo_Token.EOF
        ):
            self.avanzar()

    # GRAMÁTICA
    def parse(self):

        self.json()

        if self.mirar().tipo != Tipo_Token.EOF:
            self.error("Se esperaba EOF")

        if not self.errores:
            print("JSON SINTACTICAMENTE CORRECTO")

        else:
            print("\nERRORES ENCONTRADOS:\n")

            for error in self.errores:
                print(error)

    def json(self):
        self.element()

    def element(self):

        if self.mirar().tipo == Tipo_Token.L_LLAVE:
            self.object()

        elif self.mirar().tipo == Tipo_Token.L_CORCHETE:
            self.array()

        else:
            self.error(
                "Se esperaba objeto o arreglo"
            )
            self.panic_mode()

    def object(self):

        self.match(Tipo_Token.L_LLAVE)

        if self.mirar().tipo != Tipo_Token.R_LLAVE:
            self.attributes_list()

        self.match(Tipo_Token.R_LLAVE)

    def attributes_list(self):

        self.attribute()

        while self.mirar().tipo == Tipo_Token.COMA:
            self.match(Tipo_Token.COMA)
            self.attribute()

    def attribute(self):

        self.match(Tipo_Token.LITERAL_CADENA)

        self.match(Tipo_Token.DOS_PUNTOS)

        self.attribute_value()

    def attribute_value(self):

        token = self.mirar().tipo

        if token == Tipo_Token.L_LLAVE:
            self.object()

        elif token == Tipo_Token.L_CORCHETE:
            self.array()

        elif token == Tipo_Token.LITERAL_CADENA:
            self.match(Tipo_Token.LITERAL_CADENA)

        elif token == Tipo_Token.LITERAL_NUM:
            self.match(Tipo_Token.LITERAL_NUM)

        elif token == Tipo_Token.PR_TRUE:
            self.match(Tipo_Token.PR_TRUE)

        elif token == Tipo_Token.PR_FALSE:
            self.match(Tipo_Token.PR_FALSE)

        elif token == Tipo_Token.PR_NULL:
            self.match(Tipo_Token.PR_NULL)

        else:
            self.error("Valor inválido")
            self.panic_mode()

    def array(self):

        self.match(Tipo_Token.L_CORCHETE)

        if self.mirar().tipo != Tipo_Token.R_CORCHETE:
            self.element_list()

        self.match(Tipo_Token.R_CORCHETE)

    def element_list(self):

        self.element()

        while self.mirar().tipo == Tipo_Token.COMA:
            self.match(Tipo_Token.COMA)
            self.element()


# MAIN
def main():

    try:

        with open("input.json", "r", encoding="utf-8") as file:
            source = file.read()

        lexer = Lexer(source)

        tokens = lexer.tokenizar()

        parser = Parser(tokens)

        parser.parse()

    except FileNotFoundError:
        print("No se encontro input.json")


if __name__ == "__main__":
    main()