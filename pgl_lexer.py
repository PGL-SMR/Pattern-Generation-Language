from sly import Lexer

class PglLexer(Lexer):
    # This is the set of tokens we are exporting to the Parser
    tokens = {LPAREN, RPAREN, LBRACE, RBRACE, LBRACKET, RBRACKET, OR, NEW_LINE, COMMA, DOLLAR, IMPORT,
              STRING, ID, CODE, TYPE, DEF, DECL, IF, ELIF, ELSE, COLON, POINTER, EQUALS, EQ, NE, INCLUDE}
    # Any literals we want to ignore
    ignore = ' \t'
    # ignore_comment = r'\#.*'
    # Any literals we did not define as tokens, will be available for usage in the Parser
    #literals = {'.', '!'}

    # The definition of each token in a regex pattern - Notice that the order MATTERS!! First match will be taken
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACE = r'\{'
    RBRACE = r'\}'
    LBRACKET = r'\['
    RBRACKET = r'\]'
    OR = r'\|'    
    COMMA = r','
    IF = r'\$if'

    @_(r'(\r?\n[\t ]*)*( )*\$elif')
    def ELIF(self, t):
        self.lineno += t.value.count('\n')
        return t

    @_(r'(\r?\n[\t ]*)*( )*\$else')
    def ELSE(self, t):
        self.lineno += t.value.count('\n')
        return t

    DOLLAR = r'\$'
    POINTER = r'\*'

    @_(r'''("[^"\\]*(\\.[^"\\]*)*"|'[^'\\]*(\\.[^'\\]*)*')''')
    def STRING(self, t):
        # t.value = self.remove_quotes(t.value)
        return t

    @_(r'#include( )*((<[^>]+>)|("[^"]+"))')
    def INCLUDE(self, t):
        return t

    # Notice Identifier comes after string because most words in a string would be matched with the identifier pattern
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ID['type'] = TYPE
    ID['def'] = DEF
    ID['decl'] = DECL
    ID['import'] = IMPORT

    CODE = r'[^\$\n|_A-Za-z\(\)\{\}\*, ]+'
    CODE[':'] = COLON
    # CODE['*'] = POINTER
    CODE['='] = EQUALS
    CODE['=='] = EQ
    CODE['!='] = NE

    @_(r'(\r?\n[\t ]*)+')
    def NEW_LINE(self, t):
        self.lineno += t.value.count('\n')
        return t

    # Error handling rule
    def error(self, t):
        print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
        self.index += 1

    def remove_quotes(self, text: str):
        if text.startswith('\"') or text.startswith('\''):
            return text[1:-1]
        return text

    # Compute column.
    #     input is the input text string
    #     token is a token instance
    def find_column(text, token):
        last_cr = text.rfind('\n', 0, token.index)
        if last_cr < 0:
            last_cr = 0
        column = (token.index - last_cr) + 1
        return column

