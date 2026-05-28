lexer grammar QlikViewLexer;

// Keywords (Case-insensitive via fragment rules if needed, but standard ANTLR4 convention is matching case unless we use custom streams. 
// For simplicity we define exact match or assume lowercase/uppercase normalized stream).
// We will use standard ANTLR approach for case-insensitivity: defining exact cases and handling in stream, or fragments.
// Here we define basic keywords:

LOAD : [lL][oO][aA][dD] ;
SQL : [sS][qQ][lL] ;
SELECT : [sS][eE][lL][eE][cC][tT] ;
FROM : [fF][rR][oO][mM] ;
RESIDENT : [rR][eE][sS][iI][dD][eE][nN][tT] ;
AS : [aA][sS] ;

// Punctuation
COMMA : ',' ;
SEMI  : ';' ;
LPAREN : '(' ;
RPAREN : ')' ;
LBRACK : '[' ;
RBRACK : ']' ;
STAR   : '*' ;

// Identifiers
IDENTIFIER : [a-zA-Z_] [a-zA-Z0-9_]* ;

// Strings (Double quoted, single quoted, bracketed)
STRING_LITERAL : '\'' ~['\r\n]*? '\'' ;
BRACKETED_ID   : '[' ~']'* ']' ;

// Whitespace and Comments
WS : [ \t\r\n]+ -> skip ;
LINE_COMMENT : '//' ~[\r\n]* -> skip ;
BLOCK_COMMENT : '/*' .*? '*/' -> skip ;
