"""Testes de comportamento, estrutura da AST, diagnósticos e interface."""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from memescript import ast_nodes as ast
from memescript.compiler import compile_source
from memescript.errors import CompileError
from memescript.lexer import tokenize

ROOT = Path(__file__).resolve().parents[1]


def program(body):
    return "E_HORA_DO_SHOW\n" + body + "\nJA_ACABOU_JESSICA"


def execute(source, inputs=()):
    result = compile_source(source)
    output = io.StringIO()
    namespace = {}
    with contextlib.redirect_stdout(output), patch("builtins.input", side_effect=inputs):
        exec(compile(result.python, "<gerado>", "exec"), namespace)
    return output.getvalue(), namespace


class LexerTests(unittest.TestCase):
    def test_longest_match(self):
        tokens = tokenize("a==2 a=2 a!=2 a<=2 a>=2 6.7")
        self.assertEqual([t.kind for t in tokens], [
            "IDENTIFIER", "==", "INTEGER", "IDENTIFIER", "=", "INTEGER",
            "IDENTIFIER", "!=", "INTEGER", "IDENTIFIER", "<=", "INTEGER",
            "IDENTIFIER", ">=", "INTEGER", "REAL", "EOF"])

    def test_keyword_boundary(self):
        self.assertEqual([t.kind for t in tokenize("ATA ATA_2 ata")], ["ATA", "IDENTIFIER", "IDENTIFIER", "EOF"])

    def test_crlf_and_comments(self):
        tokens = tokenize("// café\r\n\t67\rATA\n")
        self.assertEqual((tokens[0].line, tokens[0].column), (2, 2))
        self.assertEqual(tokens[1].line, 3)
        self.assertEqual(tokens[-1].line, 4)

    def test_string_escapes(self):
        token = tokenize(r'"café\n\t\"ATA\"\\"')[0]
        self.assertEqual(token.value, 'café\n\t"ATA"\\')

    def test_invalid_character_location(self):
        with self.assertRaises(CompileError) as context:
            tokenize("ATA\n  @")
        self.assertEqual((context.exception.category, context.exception.line, context.exception.column), ("léxico", 2, 3))

    def test_bad_string(self):
        for source in ['"sem fechamento', '"linha\nreal"', r'"escape\q"']:
            with self.subTest(source=source), self.assertRaises(CompileError):
                tokenize(source)


class ParserTests(unittest.TestCase):
    def test_ast_precedence(self):
        tree = compile_source(program("AMOSTRADINHO(2 + 3 * 4);")).ast
        expr = tree.statements[0].expressions[0]
        self.assertIsInstance(expr, ast.Binary)
        self.assertEqual(expr.operator, "+")
        self.assertEqual(expr.right.operator, "*")

    def test_arithmetic_behavior(self):
        output, _ = execute(program("AMOSTRADINHO(2+3*4, (2+3)*4, 10-3-2, 20/2/2, -2*-3, +4);"))
        self.assertEqual(output, "14 20 5 5.0 6 4\n")

    def test_comparisons(self):
        output, _ = execute(program("AMOSTRADINHO(2<3, 2<=2, 3>2, 3>=3, 2==2, 2!=3);"))
        self.assertEqual(output, "verdadeiro verdadeiro verdadeiro verdadeiro verdadeiro verdadeiro\n")
        output, _ = execute(program("AMOSTRADINHO(3<2, 2!=2, (1<2)==(2<1));"))
        self.assertEqual(output, "falso falso falso\n")

    def test_empty_blocks_and_program(self):
        source = program("PODE_ISSO_ARNALDO (1==2)\nERROU\nATA\nBORA_BILL (1==2)\nATA")
        self.assertEqual(execute(source)[0], "")
        self.assertIn("pass", compile_source(program("")).python)

    def test_syntax_failures(self):
        bodies = ["SABOR_INTEIRO x = ;", "AMOSTRADINHO(1)", "AMOSTRADINHO();", "ERROU", "BORA_BILL (1<2)\nAMOSTRADINHO(1);", "AMOSTRADINHO(1<2<3);", "AMOSTRADINHO(1);\nSABOR_INTEIRO x=0;", "BORA_BILL (1<2)\nSABOR_INTEIRO x=0;\nATA"]
        for body in bodies:
            with self.subTest(body=body), self.assertRaises(CompileError) as context:
                compile_source(program(body))
            self.assertEqual(context.exception.category, "sintático")

    def test_extra_source_after_end(self):
        with self.assertRaises(CompileError):
            compile_source(program("") + "\nATA")

    def test_ast_serialization(self):
        serialized = ast.to_dict(compile_source(program("AMOSTRADINHO(67);")).ast)
        self.assertEqual(json.loads(json.dumps(serialized))["node"], "Program")


class SemanticTests(unittest.TestCase):
    def reject(self, body, fragment):
        with self.assertRaises(CompileError) as context:
            compile_source(program(body))
        self.assertEqual(context.exception.category, "semântico")
        self.assertIn(fragment, str(context.exception))

    def test_undeclared_read_write_and_expression(self):
        for body in ["RECEBA x=1;", "QUERO_CAFE(x);", "AMOSTRADINHO(x);"]:
            with self.subTest(body=body):
                self.reject(body, "antes da declaração")

    def test_duplicate(self):
        self.reject("SABOR_INTEIRO x=0; SABOR_REAL x=1.0;", "duplicada")

    def test_self_reference_and_forward_reference(self):
        self.reject("SABOR_INTEIRO x=x+1;", "antes da declaração")
        self.reject("SABOR_INTEIRO x=y; SABOR_INTEIRO y=1;", "antes da declaração")

    def test_type_errors(self):
        for body in ["SABOR_INTEIRO x=1.0;", "SABOR_INTEIRO x=1; RECEBA x=\"texto\";", "SABOR_TEXTO x=67;", "SABOR_INTEIRO x=4/2;"]:
            with self.subTest(body=body):
                self.reject(body, "incompatível")

    def test_operations_reject_non_numeric(self):
        for expr in ['"a"+"b"', '-"a"', '(1<2)+3']:
            with self.subTest(expr=expr):
                self.reject(f"AMOSTRADINHO({expr});", "exige")

    def test_invalid_conditions(self):
        self.reject("BORA_BILL (67)\nATA", "condição")
        self.reject('PODE_ISSO_ARNALDO ("sim")\nATA', "condição")

    def test_comparison_type_rules(self):
        self.reject('AMOSTRADINHO("a"<"b");', "incompatível")
        self.reject('AMOSTRADINHO("67"==67);', "incompatível")
        self.assertEqual(execute(program('AMOSTRADINHO("ATA"=="ATA", 1==1.0);'))[0], "verdadeiro verdadeiro\n")

    def test_break_outside_loop(self):
        self.reject("DESCANSAR_NE;", "dentro de BORA_BILL")
        self.reject("PODE_ISSO_ARNALDO (1==1)\nDESCANSAR_NE;\nATA", "dentro de BORA_BILL")

    def test_numeric_promotion(self):
        output, namespace = execute(program("SABOR_REAL r=1; RECEBA r=2; AMOSTRADINHO(r);"))
        self.assertEqual(output, "2.0\n")
        self.assertIsInstance(namespace["ms_var_r"], float)

    def test_symbols(self):
        self.assertEqual(compile_source(program('SABOR_INTEIRO n=1; SABOR_REAL r=n; SABOR_TEXTO s="";')).symbols, {"n": "inteiro", "r": "real", "s": "texto"})


class IntegrationTests(unittest.TestCase):
    def test_valid_examples(self):
        expected = {"01_valido_basico": "Receba! 68\n", "09_valido_aninhado": "0 1\n1 1\nFim: 2 2\n", "10_valido_tipos": "Pedro 67 6.7\nTexto: verdadeiro\n"}
        for stem, output in expected.items():
            with self.subTest(stem=stem):
                path = ROOT / "exemplos" / (stem + ".meme")
                input_path = path.with_suffix(".in")
                inputs = input_path.read_text(encoding="utf-8").splitlines() if input_path.exists() else []
                self.assertEqual(execute(path.read_text(encoding="utf-8"), inputs)[0], output)

    def test_complete_expected_output(self):
        path = ROOT / "exemplos/02_valido_completo.meme"
        expected = path.with_suffix(".out").read_text(encoding="utf-8")
        self.assertEqual(execute(path.read_text(encoding="utf-8"), ["10"])[0], expected)

    def test_complete_zero_limit(self):
        path = ROOT / "exemplos/02_valido_completo.meme"
        output = execute(path.read_text(encoding="utf-8"), ["0"])[0]
        self.assertNotIn("Cafés:", output)
        self.assertIn("Energia final: 0\nGasto: 0.0", output)

    def test_python_identifiers_do_not_collide(self):
        source = program("SABOR_INTEIRO print=1; SABOR_INTEIRO class=2; SABOR_INTEIRO ms_var_print=3; AMOSTRADINHO(print,class,ms_var_print);")
        self.assertEqual(execute(source)[0], "1 2 3\n")

    def test_string_contents_are_not_code(self):
        text = 'ATA JA_ACABOU_JESSICA __import__("os") # RECEBA'
        self.assertEqual(execute(program("AMOSTRADINHO(" + json.dumps(text) + ");"))[0], text + "\n")

    def test_invalid_example_categories(self):
        for path in sorted((ROOT / "exemplos").glob("*_erro_*.meme")):
            with self.subTest(path=path.name), self.assertRaises(CompileError) as context:
                compile_source(path.read_text(encoding="utf-8"))
            category = "léxico" if path.name.startswith("03") else "sintático" if path.name.startswith("04") else "semântico"
            self.assertEqual(context.exception.category, category)

    def test_cli_success_and_debug(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "out.py"
            run = subprocess.run([sys.executable, "-m", "memescript", "exemplos/01_valido_basico.meme", "-o", str(output), "--ast", "--tokens", "--symbols"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn('"node": "Program"', run.stdout)
            self.assertTrue(output.exists())
            execution = subprocess.run([sys.executable, str(output)], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(execution.stdout, "Receba! 68\n")

    def test_cli_error_does_not_write_or_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "out.py"
            for exists in (False, True):
                if exists:
                    output.write_text("anterior", encoding="utf-8")
                run = subprocess.run([sys.executable, "-m", "memescript", "exemplos/07_erro_tipos.meme", "-o", str(output)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(run.returncode, 1)
                self.assertIn("Erro semântico", run.stderr)
                if exists:
                    self.assertEqual(output.read_text(encoding="utf-8"), "anterior")
                else:
                    self.assertFalse(output.exists())

    def test_cli_check_does_not_write(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "teste.meme"
            path.write_text(program("AMOSTRADINHO(67);"), encoding="utf-8")
            run = subprocess.run([sys.executable, "-m", "memescript", str(path), "--check"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(run.returncode, 0)
            self.assertFalse(path.with_suffix(".py").exists())


if __name__ == "__main__":
    unittest.main()
