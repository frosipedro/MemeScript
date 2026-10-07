# Alterações do vocabulário da MemeScript

Atualização de 6 de outubro de 2026. O comportamento das construções foi mantido; mudaram as quatro palavras reservadas abaixo.

| Antes | Agora | Função |
| --- | --- | --- |
| `ACORDA_PEDRINHO` | `E_HORA_DO_SHOW` | Início do programa |
| `ACABOU` | `JA_ACABOU_JESSICA` | Fim do programa |
| `E_VERDADE_ESSE_BILETE` | `PODE_ISSO_ARNALDO` | Condicional `if` |
| `SO_QUE_NAO` | `ERROU` | Alternativa `else` |

Os programas devem usar o vocabulário novo. As palavras antigas não são aliases de comandos.

## Arquivos modificados

- `README.md`
- `docs/apresentacao_nova.pptx`
- `docs/gramatica.ebnf`
- `docs/relatorio_tecnico.docx`
- `docs/relatorio_tecnico.md`
- `docs/relatorio_tecnico.pdf`
- `docs/resultados_validacao.txt`
- `docs/roteiro_defesa.md`
- `exemplos/01_valido_basico.meme`
- `exemplos/02_valido_completo.meme`
- `exemplos/03_erro_lexico.meme`
- `exemplos/04_erro_sintatico.meme`
- `exemplos/05_erro_semantico.meme`
- `exemplos/06_erro_redeclaracao.meme`
- `exemplos/07_erro_tipos.meme`
- `exemplos/08_erro_break.meme`
- `exemplos/09_valido_aninhado.meme`
- `exemplos/10_valido_tipos.meme`
- `gerados/01_valido_basico.tokens.json`
- `gerados/02_valido_completo.ast.json`
- `gerados/02_valido_completo.tokens.json`
- `gerados/09_valido_aninhado.ast.json`
- `gerados/09_valido_aninhado.tokens.json`
- `gerados/10_valido_tipos.tokens.json`
- `memescript/ast_nodes.py`
- `memescript/lexer.py`
- `memescript/parser.py`
- `testes/test_transpilador.py`

## Apresentação substituída

`docs/apresentacao_nova.pptx` é a apresentação escolhida pelo grupo, com os novos comandos e notas atualizadas. O pacote deixa de incluir `docs/apresentacao.pptx`; remova esse arquivo antigo do repositório se ele ainda existir.

## Arquivo acrescentado

- `ALTERACOES.md` (este registro).

## Verificação

Os 32 métodos de teste passaram. A demonstração executou os quatro exemplos válidos e rejeitou os seis exemplos inválidos. O relatório Word/PDF e os 14 slides foram renderizados e conferidos.

O README conserva as alterações e os integrantes informados pelo grupo. Os `.py` em `gerados/` foram regenerados e permaneceram idênticos: os novos comandos produzem o mesmo Python. As tabelas de símbolos e ASTs dos exemplos básico e de tipos também permaneceram idênticas. Os tokens e as ASTs afetadas foram atualizados a partir dos novos fontes.

```bash
python -m unittest discover -s testes -v
python demo.py
```
