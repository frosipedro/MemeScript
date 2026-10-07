"""Parser preditivo por descida recursiva, sem recursão à esquerda."""

from . import ast_nodes as ast
from .errors import CompileError

TYPE_KEYWORDS = {
    "SABOR_INTEIRO": "inteiro", "SABOR_REAL": "real", "SABOR_TEXTO": "texto",
}
RELATIONAL = {"==", "!=", "<", "<=", ">", ">="}


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    @property
    def current(self):
        return self.tokens[self.position]

    def advance(self):
        token = self.current
        self.position += 1
        return token

    def error(self, expected):
        token = self.current
        found = repr(token.lexeme) if token.kind != "EOF" else "fim do arquivo"
        raise CompileError("sintático", f"encontrado {found}; esperado {expected}", token.line, token.column)

    def expect(self, kind):
        if self.current.kind != kind:
            self.error(kind)
        return self.advance()

    def parse(self):
        self.expect("E_HORA_DO_SHOW")
        declarations = []
        while self.current.kind in TYPE_KEYWORDS:
            declarations.append(self.declaration())
        statements = self.block({"JA_ACABOU_JESSICA"})
        self.expect("JA_ACABOU_JESSICA")
        self.expect("EOF")
        return ast.Program(declarations, statements)

    def declaration(self):
        type_token = self.advance()
        name = self.expect("IDENTIFIER")
        self.expect("=")
        initializer = self.expression()
        self.expect(";")
        return ast.VarDecl(TYPE_KEYWORDS[type_token.kind], name.lexeme, initializer, name.line, name.column)

    def block(self, terminators):
        statements = []
        while self.current.kind not in terminators:
            if self.current.kind in ("EOF", "JA_ACABOU_JESSICA"):
                self.error(" ou ".join(sorted(terminators)))
            statements.append(self.statement())
        return statements

    def statement(self):
        token = self.current
        if token.kind == "RECEBA":
            self.advance()
            name = self.expect("IDENTIFIER")
            self.expect("=")
            expression = self.expression()
            self.expect(";")
            return ast.Assign(name.lexeme, expression, name.line, name.column)
        if token.kind == "QUERO_CAFE":
            self.advance()
            self.expect("(")
            name = self.expect("IDENTIFIER")
            self.expect(")")
            self.expect(";")
            return ast.Read(name.lexeme, name.line, name.column)
        if token.kind == "AMOSTRADINHO":
            self.advance()
            self.expect("(")
            expressions = [self.expression()]
            while self.current.kind == ",":
                self.advance()
                expressions.append(self.expression())
            self.expect(")")
            self.expect(";")
            return ast.Print(expressions, token.line, token.column)
        if token.kind == "PODE_ISSO_ARNALDO":
            self.advance()
            self.expect("(")
            condition = self.expression()
            self.expect(")")
            then_body = self.block({"ERROU", "ATA"})
            else_body = None
            if self.current.kind == "ERROU":
                self.advance()
                else_body = self.block({"ATA"})
            self.expect("ATA")
            return ast.If(condition, then_body, else_body, token.line, token.column)
        if token.kind == "BORA_BILL":
            self.advance()
            self.expect("(")
            condition = self.expression()
            self.expect(")")
            body = self.block({"ATA"})
            self.expect("ATA")
            return ast.While(condition, body, token.line, token.column)
        if token.kind == "DESCANSAR_NE":
            self.advance()
            self.expect(";")
            return ast.Break(token.line, token.column)
        self.error("RECEBA, QUERO_CAFE, AMOSTRADINHO, PODE_ISSO_ARNALDO, BORA_BILL ou DESCANSAR_NE")

    def expression(self):
        # No máximo uma comparação por nível. Aritmética vem primeiro.
        left = self.additive()
        if self.current.kind in RELATIONAL:
            token = self.advance()
            left = ast.Binary(left, token.kind, self.additive(), token.line, token.column)
        return left

    def additive(self):
        left = self.multiplicative()
        while self.current.kind in ("+", "-"):
            token = self.advance()
            left = ast.Binary(left, token.kind, self.multiplicative(), token.line, token.column)
        return left

    def multiplicative(self):
        left = self.unary()
        while self.current.kind in ("*", "/"):
            token = self.advance()
            left = ast.Binary(left, token.kind, self.unary(), token.line, token.column)
        return left

    def unary(self):
        if self.current.kind in ("+", "-"):
            token = self.advance()
            return ast.Unary(token.kind, self.unary(), token.line, token.column)
        return self.primary()

    def primary(self):
        token = self.current
        types = {"INTEGER": "inteiro", "REAL": "real", "STRING": "texto"}
        if token.kind in types:
            self.advance()
            return ast.Literal(token.value, types[token.kind], token.line, token.column)
        if token.kind == "IDENTIFIER":
            self.advance()
            return ast.Variable(token.lexeme, token.line, token.column)
        if token.kind == "(":
            self.advance()
            expression = self.expression()
            self.expect(")")
            return expression
        self.error("literal, identificador ou expressão entre parênteses")
