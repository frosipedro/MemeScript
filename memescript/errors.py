class CompileError(Exception):
    """Erro de compilação com categoria e localização no código-fonte."""

    def __init__(self, category, message, line, column):
        self.category = category
        self.message = message
        self.line = line
        self.column = column
        super().__init__(
            f"Erro {category} na linha {line}, coluna {column}: {message}"
        )
