/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package lexer;

/**
 *
 * @author eliasovd
 */

import java.util.ArrayList;
import java.util.List;

public class Lexer {

    private String input;
    private int pos;

    public Lexer(String input) {
        this.input = input;
        this.pos = 0;
    }

    public List<Token> tokenize() {
        List<Token> tokens = new ArrayList<>();

        while (pos < input.length()) {
            char c = input.charAt(pos);

            switch (c) {
                case '[':
                    tokens.add(new Token(TokenType.L_CORCHETE, "["));
                    pos++;
                    break;
                case ']':
                    tokens.add(new Token(TokenType.R_CORCHETE, "]"));
                    pos++;
                    break;
                case '{':
                    tokens.add(new Token(TokenType.L_LLAVE, "{"));
                    pos++;
                    break;
                case '}':
                    tokens.add(new Token(TokenType.R_LLAVE, "}"));
                    pos++;
                    break;
                case ',':
                    tokens.add(new Token(TokenType.COMA, ","));
                    pos++;
                    break;
                case ':':
                    tokens.add(new Token(TokenType.DOS_PUNTOS, ":"));
                    pos++;
                    break;
                case '"':
                    tokens.add(readString());
                    break;
                default:
                    if (Character.isDigit(c)) {
                        tokens.add(readNumber());
                    } else if (Character.isLetter(c)) {
                        tokens.add(readKeyword());
                    } else if (Character.isWhitespace(c)) {
                        pos++;
                    } else {
                        tokens.add(new Token(TokenType.ERROR, String.valueOf(c)));
                        pos++;
                    }
            }
        }

        return tokens;
    }

    private Token readString() {
        StringBuilder sb = new StringBuilder();
        sb.append('"');
        pos++;

        while (pos < input.length() && input.charAt(pos) != '"') {
            sb.append(input.charAt(pos));
            pos++;
        }

        if (pos < input.length()) {
            sb.append('"');
            pos++;
            return new Token(TokenType.LITERAL_CADENA, sb.toString());
        }

        return new Token(TokenType.ERROR, sb.toString());
    }

    private Token readNumber() {
        StringBuilder sb = new StringBuilder();

        while (pos < input.length() &&
                (Character.isDigit(input.charAt(pos)) || input.charAt(pos) == '.'
                        || input.charAt(pos) == 'e' || input.charAt(pos) == 'E'
                        || input.charAt(pos) == '+' || input.charAt(pos) == '-')) {
            sb.append(input.charAt(pos));
            pos++;
        }

        return new Token(TokenType.LITERAL_NUM, sb.toString());
    }

    private Token readKeyword() {
        StringBuilder sb = new StringBuilder();

        while (pos < input.length() && Character.isLetter(input.charAt(pos))) {
            sb.append(input.charAt(pos));
            pos++;
        }

        String word = sb.toString();

        switch (word.toLowerCase()) {
            case "true":
                return new Token(TokenType.PR_TRUE, word);
            case "false":
                return new Token(TokenType.PR_FALSE, word);
            case "null":
                return new Token(TokenType.PR_NULL, word);
            default:
                return new Token(TokenType.ERROR, word);
        }
    }
}