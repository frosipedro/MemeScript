from dataclasses import dataclass

from .lexer import tokenize
from .parser import Parser
from .semantic import SemanticAnalyzer
from .codegen import CodeGenerator


@dataclass
class Compilation:
    tokens: list
    ast: object
    symbols: dict
    python: str


def compile_source(source):
    tokens = tokenize(source)
    tree = Parser(tokens).parse()
    symbols = SemanticAnalyzer().analyze(tree)
    python = CodeGenerator(symbols).generate(tree)
    return Compilation(tokens, tree, symbols, python)
