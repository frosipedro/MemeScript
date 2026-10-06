"""Reconhecimento por expressões regulares e maior casamento."""

from dataclasses import dataclass, asdict
import json
import re

from .errors import CompileError

KEYWORDS = {
    word: word for word in (
        "ACORDA_PEDRINHO", "ACABOU", "SABOR_INTEIRO", "SABOR_REAL",
        "SABOR_TEXTO", "RECEBA", "QUERO_CAFE", "AMOSTRADINHO",
        "E_VERDADE_ESSE_BILETE", "SO_QUE_NAO", "BORA_BILL",
        "DESCANSAR_NE", "ATA",
    )
}

# A seleção abaixo considera todos os padrões na posição atual, escolhe
# o match mais longo e usa a ordem da lista apenas para desempatar.
PATTERNS = [
    ("WHITESPACE", re.compile(r"[ \t\r\n]+")),
    ("COMMENT", re.compile(r"//[^\r\n]*")),
    ("REAL", re.compile(r"[0-9]+\.[0-9]+")),
    ("INTEGER", re.compile(r"[0-9]+")),
    ("STRING", re.compile(r'"(?:[^"\\\x00-\x1f]|\\["\\nrt])*"')),
    ("IDENTIFIER", re.compile(r"[A-Za-z_][A-Za-z0-9_]*")),
    ("OPERATOR", re.compile(r"==|!=|<=|>=|[=+*/<>-]")),
    ("DELIMITER", re.compile(r"[(),;]")),
]


@dataclass(frozen=True)
class Token:
    kind: str
    lexeme: str
    value: object
    line: int
    column: int

    def as_dict(self):
        return asdict(self)


def tokenize(source):
    tokens = []
    offset, line, column = 0, 1, 1
    while offset < len(source):
        matches = []
        for priority, (kind, pattern) in enumerate(PATTERNS):
            match = pattern.match(source, offset)
            if match:
                matches.append((len(match.group()), -priority, kind, match.group()))
        if not matches:
            detail = "texto malformado ou escape inválido" if source[offset] == '"' else f"símbolo inválido {source[offset]!r}"
            raise CompileError("léxico", detail, line, column)
        _, _, kind, lexeme = max(matches)
        if kind not in ("WHITESPACE", "COMMENT"):
            value = lexeme
            if kind == "IDENTIFIER":
                kind = KEYWORDS.get(lexeme, kind)
            elif kind == "INTEGER":
                try:
                    value = int(lexeme)
                except ValueError:
                    raise CompileError("léxico", "literal inteiro excede o limite do runtime", line, column) from None
            elif kind == "REAL":
                value = float(lexeme)
                if value == float("inf"):
                    raise CompileError("léxico", "literal real fora da faixa representável", line, column)
            elif kind == "STRING":
                value = json.loads(lexeme)
            elif kind in ("OPERATOR", "DELIMITER"):
                kind = lexeme
            tokens.append(Token(kind, lexeme, value, line, column))
        parts = re.split(r"\r\n|\r|\n", lexeme)
        if len(parts) > 1:
            line += len(parts) - 1
            column = len(parts[-1]) + 1
        else:
            column += len(lexeme)
        offset += len(lexeme)
    tokens.append(Token("EOF", "", None, line, column))
    return tokens
