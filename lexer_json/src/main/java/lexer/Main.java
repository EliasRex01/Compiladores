/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package lexer;

/**
 *
 * @author eliasovd
 */

import java.io.*;
import java.util.List;

public class Main {

    public static void main(String[] args) {
        String inputFile = "input.json";
        String outputFile = "output.txt";

        try (BufferedReader reader = new BufferedReader(new FileReader(inputFile));
             BufferedWriter writer = new BufferedWriter(new FileWriter(outputFile))) {

            String line;

            while ((line = reader.readLine()) != null) {
                Lexer lexer = new Lexer(line);
                List<Token> tokens = lexer.tokenize();

                boolean error = false;

                StringBuilder outputLine = new StringBuilder();

                for (Token token : tokens) {
                    if (token.type == TokenType.ERROR) {
                        writer.write("ERROR LEXICO: " + token.lexeme);
                        error = true;
                        break;
                    }
                    outputLine.append(token).append(" ");
                }

                if (!error) {
                    writer.write(outputLine.toString().trim());
                }

                writer.newLine();
            }

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}