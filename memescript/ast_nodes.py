"""Nós da AST. Delimitadores e palavras de fechamento não viram nós."""

from dataclasses import dataclass, fields, is_dataclass


@dataclass
class Literal:
    value: object
    type_name: str
    line: int
    column: int


@dataclass
class Variable:
    name: str
    line: int
    column: int


@dataclass
class Unary:
    operator: str
    operand: object
    line: int
    column: int


@dataclass
class Binary:
    left: object
    operator: str
    right: object
    line: int
    column: int


@dataclass
class VarDecl:
    type_name: str
    name: str
    initializer: object
    line: int
    column: int


@dataclass
class Assign:
    name: str
    expression: object
    line: int
    column: int


@dataclass
class Read:
    name: str
    line: int
    column: int


@dataclass
class Print:
    expressions: list
    line: int
    column: int


@dataclass
class If:
    condition: object
    then_body: list
    else_body: object  # None significa ausência de SO_QUE_NAO.
    line: int
    column: int


@dataclass
class While:
    condition: object
    body: list
    line: int
    column: int


@dataclass
class Break:
    line: int
    column: int


@dataclass
class Program:
    declarations: list
    statements: list


def to_dict(node):
    """Serialização para inspeção didática, sem executar o programa."""
    if is_dataclass(node):
        return {"node": type(node).__name__, **{
            field.name: to_dict(getattr(node, field.name)) for field in fields(node)
        }}
    if isinstance(node, list):
        return [to_dict(item) for item in node]
    return node
