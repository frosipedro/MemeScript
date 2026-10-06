"""CLI: python -m memescript programa.meme -o programa.py"""

import argparse
import json
from pathlib import Path
import sys

from .ast_nodes import to_dict
from .compiler import compile_source
from .errors import CompileError


def main(argv=None):
    parser = argparse.ArgumentParser(description="Transpila MemeScript para Python.")
    parser.add_argument("source", type=Path, help="arquivo .meme em UTF-8")
    parser.add_argument("-o", "--output", type=Path, help="arquivo Python de saída")
    parser.add_argument("--tokens", action="store_true", help="mostra tokens como JSON")
    parser.add_argument("--ast", action="store_true", help="mostra AST como JSON")
    parser.add_argument("--symbols", action="store_true", help="mostra tabela de símbolos")
    parser.add_argument("--check", action="store_true", help="valida sem gravar o programa Python")
    args = parser.parse_args(argv)
    if args.check and args.output:
        parser.error("--check não pode ser combinado com --output")
    output = args.output or args.source.with_suffix(".py")
    if not args.check and output.resolve() == args.source.resolve():
        parser.error("a saída deve ser diferente do arquivo-fonte")
    try:
        source = args.source.read_text(encoding="utf-8-sig")
        result = compile_source(source)
        if args.tokens:
            print(json.dumps([t.as_dict() for t in result.tokens], ensure_ascii=False, indent=2))
        if args.ast:
            print(json.dumps(to_dict(result.ast), ensure_ascii=False, indent=2))
        if args.symbols:
            print(json.dumps(result.symbols, ensure_ascii=False, indent=2))
        # A gravação só ocorre depois de TODAS as fases passarem.
        if not args.check:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(result.python, encoding="utf-8")
            print(f"ACERTOU, MISERAVI! Python gerado em: {output}")
        else:
            print("ACERTOU, MISERAVI! Programa válido.")
        return 0
    except CompileError as error:
        print(error, file=sys.stderr)
        return 1
    except (OSError, UnicodeError) as error:
        print(f"Erro de arquivo: {error}", file=sys.stderr)
        return 2
    except RecursionError:
        print("Erro: o aninhamento excedeu o limite de recursão do Python.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
