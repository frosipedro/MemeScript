"""Tabela de símbolos e tipos, em uma fase separada do parser."""

from . import ast_nodes as ast
from .errors import CompileError

NUMERIC = {"inteiro", "real"}


class SemanticAnalyzer:
    def __init__(self):
        self.symbols = {}

    def fail(self, node, message):
        raise CompileError("semântico", message, node.line, node.column)

    def lookup(self, name, node):
        if name not in self.symbols:
            self.fail(node, f"variável '{name}' usada antes da declaração")
        return self.symbols[name]

    def compatible(self, target, source):
        return target == source or (target == "real" and source == "inteiro")

    def check_assignment(self, target, expression, node):
        source = self.expression_type(expression)
        if not self.compatible(target, source):
            self.fail(node, f"atribuição incompatível: esperado {target}, recebido {source}")

    def analyze(self, program):
        for declaration in program.declarations:
            if declaration.name in self.symbols:
                self.fail(declaration, f"declaração duplicada de '{declaration.name}' no escopo global")
            # O nome só passa a existir depois de verificar seu inicializador.
            self.check_assignment(declaration.type_name, declaration.initializer, declaration)
            self.symbols[declaration.name] = declaration.type_name
        self.statements(program.statements, loop_depth=0)
        return dict(self.symbols)

    def statements(self, statements, loop_depth):
        for node in statements:
            if isinstance(node, ast.Assign):
                self.check_assignment(self.lookup(node.name, node), node.expression, node)
            elif isinstance(node, ast.Read):
                self.lookup(node.name, node)
            elif isinstance(node, ast.Print):
                for expression in node.expressions:
                    self.expression_type(expression)
            elif isinstance(node, (ast.If, ast.While)):
                if self.expression_type(node.condition) != "logico":
                    self.fail(node, "a condição deve produzir um valor lógico por comparação")
                if isinstance(node, ast.If):
                    self.statements(node.then_body, loop_depth)
                    if node.else_body is not None:
                        self.statements(node.else_body, loop_depth)
                else:
                    self.statements(node.body, loop_depth + 1)
            elif isinstance(node, ast.Break):
                if loop_depth == 0:
                    self.fail(node, "DESCANSAR_NE só pode aparecer dentro de BORA_BILL")
            else:
                raise TypeError(f"nó de comando desconhecido: {type(node).__name__}")

    def expression_type(self, node):
        if isinstance(node, ast.Literal):
            return node.type_name
        if isinstance(node, ast.Variable):
            return self.lookup(node.name, node)
        if isinstance(node, ast.Unary):
            operand = self.expression_type(node.operand)
            if operand not in NUMERIC:
                self.fail(node, f"operador unário '{node.operator}' exige número, recebido {operand}")
            return operand
        if isinstance(node, ast.Binary):
            left, right = self.expression_type(node.left), self.expression_type(node.right)
            if node.operator in ("+", "-", "*", "/"):
                if left not in NUMERIC or right not in NUMERIC:
                    self.fail(node, f"operador '{node.operator}' exige números, recebidos {left} e {right}")
                return "real" if node.operator == "/" or "real" in (left, right) else "inteiro"
            if node.operator in ("==", "!="):
                valid = left == right or (left in NUMERIC and right in NUMERIC)
            else:
                valid = left in NUMERIC and right in NUMERIC
            if not valid:
                self.fail(node, f"comparação '{node.operator}' incompatível entre {left} e {right}")
            return "logico"
        raise TypeError(f"nó de expressão desconhecido: {type(node).__name__}")
