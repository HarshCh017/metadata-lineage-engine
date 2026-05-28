parser grammar QlikViewParser;

options { tokenVocab=QlikViewLexer; }

script : statement* EOF ;

statement : load_statement
          | sql_statement
          | other_statement
          ;

load_statement : LOAD field_list (FROM source | RESIDENT IDENTIFIER) SEMI ;

sql_statement : SQL SELECT field_list FROM source SEMI ;

field_list : field (COMMA field)* 
           | STAR
           ;

field : identifier (AS identifier)? ;

source : STRING_LITERAL
       | BRACKETED_ID
       | identifier
       ;

identifier : IDENTIFIER | BRACKETED_ID ;

other_statement : ~SEMI* SEMI ; // Catch-all for unsupported statements to avoid crashing
