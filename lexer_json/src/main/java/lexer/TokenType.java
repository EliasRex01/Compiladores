/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package lexer;

/**
 *
 * @author eliasovd
 */
public enum TokenType {
    L_CORCHETE,    // [
    R_CORCHETE,    // ]
    L_LLAVE,       // {
    R_LLAVE,       // }
    COMA,          // ,
    DOS_PUNTOS,    // :
    LITERAL_CADENA,
    LITERAL_NUM,
    PR_TRUE,
    PR_FALSE,
    PR_NULL,
    EOF,
    ERROR
}