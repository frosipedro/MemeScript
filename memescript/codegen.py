"""Geração a partir da AST validada. Nunca faz substituição textual."""

from . import ast_nodes as ast

# Na MemeScript, o tipo lógico só nasce de uma comparação. Não há variável,
# literal nem operador lógico, então um nó Binary com um destes operadores
# é exatamente uma expressão do tipo lógico.
COMPARISONS = {"==", "!=", "<", "<=", ">", ">="}


class CodeGenerator:
    def __init__(self, symbols):
        self.symbols = symbols
        self.lines = []

    def name(self, source_name):
        # Python reserva 'class', 'for' etc. Um prefixo injetivo também impede
        # que nomes da linguagem sobrescrevam print, input, int ou float.
        return "ms_var_" + source_name

    def emit(self, text, depth=0):
        self.lines.append("    " * depth + text)

    def expression(self, node):
        if isinstance(node, ast.Literal):
            return repr(node.value)
        if isinstance(node, ast.Variable):
            return self.name(node.name)
        if isinstance(node, ast.Unary):
            return f"({node.operator}{self.expression(node.operand)})"
        if isinstance(node, ast.Binary):
            return f"({self.expression(node.left)} {node.operator} {self.expression(node.right)})"
        raise TypeError(type(node).__name__)

    def output_value(self, node):
        # Valores lógicos são exibidos com as palavras da linguagem, não com True/False do Python.
        code = self.expression(node)
        if isinstance(node, ast.Binary) and node.operator in COMPARISONS:
            return f"('verdadeiro' if {code} else 'falso')"
        return code

    def convert_assignment(self, name, expression):
        code = self.expression(expression)
        # A promoção inteiro -> real também ocorre no Python gerado.
        return f"float({code})" if self.symbols[name] == "real" else code

    def block(self, statements, depth):
        if not statements:
            self.emit("pass", depth)
        for node in statements:
            if isinstance(node, ast.Assign):
                self.emit(f"{self.name(node.name)} = {self.convert_assignment(node.name, node.expression)}", depth)
            elif isinstance(node, ast.Read):
                conversion = {"inteiro": "int", "real": "float", "texto": "str"}[self.symbols[node.name]]
                code = "input()" if conversion == "str" else f"{conversion}(input())"
                self.emit(f"{self.name(node.name)} = {code}", depth)
            elif isinstance(node, ast.Print):
                args = ", ".join(self.output_value(expr) for expr in node.expressions)
                self.emit(f"print({args})", depth)
            elif isinstance(node, ast.If):
                self.emit(f"if {self.expression(node.condition)}:", depth)
                self.block(node.then_body, depth + 1)
                if node.else_body is not None:
                    self.emit("else:", depth)
                    self.block(node.else_body, depth + 1)
            elif isinstance(node, ast.While):
                self.emit(f"while {self.expression(node.condition)}:", depth)
                self.block(node.body, depth + 1)
            elif isinstance(node, ast.Break):
                self.emit("break", depth)
            else:
                raise TypeError(type(node).__name__)

    def generate(self, program):
        self.emit("# Gerado pelo MemeScript 1.0.0")
        self.emit("# Variáveis recebem o prefixo ms_var_ para preservar seus nomes.")
        for node in program.declarations:
            self.emit(f"{self.name(node.name)} = {self.convert_assignment(node.name, node.initializer)}")
        if program.declarations:
            self.emit("")
        self.block(program.statements, 0)
        return "\n".join(self.lines) + "\n"
