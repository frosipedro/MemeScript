"""Demonstração reproduzível, com execução dos arquivos Python gerados."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
VALID = ("01_valido_basico", "02_valido_completo", "09_valido_aninhado", "10_valido_tipos")


def main():
    for stem in VALID:
        print(f"\n=== {stem} ===", flush=True)
        output = ROOT / "gerados" / (stem + ".py")
        subprocess.run([sys.executable, "-m", "memescript", str(ROOT / "exemplos" / (stem + ".meme")), "-o", str(output)], cwd=ROOT, check=True)
        input_path = ROOT / "exemplos" / (stem + ".in")
        data = input_path.read_text(encoding="utf-8") if input_path.exists() else ""
        subprocess.run([sys.executable, str(output)], input=data, text=True, encoding="utf-8", cwd=ROOT, check=True, timeout=5)
    for path in sorted((ROOT / "exemplos").glob("*_erro_*.meme")):
        print(f"\n=== {path.stem} ===", flush=True)
        result = subprocess.run([sys.executable, "-m", "memescript", str(path), "--check"], cwd=ROOT)
        if result.returncode != 1:
            raise RuntimeError(f"Esperado erro de compilação em {path.name}")
    print("\nDemonstração concluída: programas válidos executados e inválidos rejeitados.")


if __name__ == "__main__":
    main()
