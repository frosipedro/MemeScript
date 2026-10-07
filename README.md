# MemeScript

Linguagem temática baseada em memes, com transpilador para Python. Projeto do Trabalho Prático 1 de Linguagens Formais e Compiladores da UNIJUÍ, professor Marcos Ronaldo Melo Cavalheiro.

## Pré-requisitos

- Python 3.10 ou superior.
- Nenhum pacote externo. O transpilador e os testes usam apenas a biblioteca padrão.
- Arquivos-fonte em UTF-8, extensão sugerida `.meme`.

Abra o terminal **na pasta que contém este README**. No Windows, use `python` ou `py -3`; no Linux/WSL, use `python3` se `python` não estiver disponível. Os exemplos abaixo usam `python`.

## Primeiro uso

```bash
python -m memescript exemplos/02_valido_completo.meme -o gerados/02_valido_completo.py
python gerados/02_valido_completo.py
```

Quando o programa pedir o limite de cafés, digite `10`. Resultado esperado: cinco cafés, energia final `70`, gasto `22.5`, precedência `14` e expressão com parênteses `20`.

Alternativa equivalente:

```bash
python transpilador.py exemplos/01_valido_basico.meme -o gerados/01_valido_basico.py
```

O comando de transpilação **não executa** o programa gerado. Sem `-o`, a saída recebe o mesmo nome do fonte, com extensão `.py`.

## Inspeção das etapas

```bash
python -m memescript exemplos/01_valido_basico.meme --check --tokens --ast --symbols
```

`--check` valida sem gravar o Python. `--tokens`, `--ast` e `--symbols` exibem os resultados em JSON após a compilação completa passar. Códigos de saída: `0` sucesso, `1` erro de compilação, `2` erro de arquivo/uso/limite de execução da ferramenta. Um programa inválido não cria nem sobrescreve o arquivo Python de saída.

## Testes e demonstração

```bash
python -m unittest discover -s testes -v
python demo.py
```

São 32 métodos de teste, alguns com múltiplos casos. `demo.py` regenera e executa quatro exemplos válidos e mostra os seis erros previstos. Ele fornece automaticamente as entradas dos arquivos `.in`. Os processos válidos da demonstração têm limite de cinco segundos.

## Exemplo da linguagem

```text
E_HORA_DO_SHOW
SABOR_INTEIRO numero = 67;
SABOR_TEXTO mensagem = "Receba!";
RECEBA numero = numero + 1;
AMOSTRADINHO(mensagem, numero);
JA_ACABOU_JESSICA
```

## MemeScript × Python

| MemeScript | Python |
| --- | --- |
| `SABOR_INTEIRO` | `int` |
| `SABOR_REAL` | `float` |
| `SABOR_TEXTO` | `str` |
| `RECEBA` | `=` (atribuição) |
| `QUERO_CAFE` | `input()` |
| `AMOSTRADINHO` | `print()` |
| `PODE_ISSO_ARNALDO` | `if` |
| `ERROU` | `else` |
| `BORA_BILL` | `while` |
| `DESCANSAR_NE` | `break` |
| `ATA` | Fim do bloco pela redução da indentação |
| `E_HORA_DO_SHOW` | Início do programa, sem palavra reservada equivalente |
| `JA_ACABOU_JESSICA` | Fim do programa, sem palavra reservada equivalente |

Python não usa `end`: os blocos são definidos pela indentação. Na entrada de números, `QUERO_CAFE` gera `int(input())` ou `float(input())`, conforme o tipo declarado.

## Regras principais

- Tipos declarados: `SABOR_INTEIRO`, `SABOR_REAL`, `SABOR_TEXTO`.
- Todas as declarações aparecem no início do programa e possuem inicializador. Existe um único escopo global.
- `RECEBA` modifica uma variável já declarada. Não faz declaração implícita.
- `QUERO_CAFE(nome);` lê um inteiro, real ou texto conforme a tabela de símbolos. Reais usam ponto decimal.
- `AMOSTRADINHO(expressao, ...);` mostra um ou mais valores separados por espaço e termina com uma quebra de linha.
- `PODE_ISSO_ARNALDO (comparacao)` abre um condicional. `ERROU` é opcional. Um único `ATA` fecha o condicional inteiro.
- `BORA_BILL (comparacao)` abre um laço, fechado por `ATA`.
- `DESCANSAR_NE;` encerra o laço mais próximo. Fora de um laço, causa erro semântico.
- Comandos simples terminam em `;`. Aberturas e fechamentos de programa/bloco não usam `;`.
- Espaços, tabs e quebras de linha não definem blocos. Comentários começam com `//` e vão até o fim da linha.
- Operadores: `+ - * / == != < <= > >=`. Unários `+` e `-` têm maior precedência, seguidos de `* /`, `+ -` e comparações. Parênteses modificam o agrupamento.
- `/` sempre resulta em real. Inteiro pode ser promovido para real. Real não é convertido implicitamente para inteiro.
- Texto aceita apenas igualdade/desigualdade e entrada/saída, sem concatenação ou operações aritméticas.
- Comparações produzem um tipo lógico interno. Ele pode ser exibido, mas não é um tipo declarável.
- Identificadores usam `[A-Za-z_][A-Za-z0-9_]*`. A linguagem diferencia maiúsculas de minúsculas. Strings podem conter acentos e os escapes `\n`, `\r`, `\t`, `\"` e `\\`.

## Organização

| Caminho | Responsabilidade |
| --- | --- |
| `memescript/lexer.py` | ERs, maior casamento, palavras reservadas e localização |
| `memescript/parser.py` | Gramática e construção da AST |
| `memescript/ast_nodes.py` | Nós e serialização da AST |
| `memescript/semantic.py` | Tabela de símbolos e verificação de tipos |
| `memescript/codegen.py` | Emissão de Python a partir da AST validada |
| `memescript/compiler.py` | Coordenação das fases |
| `memescript/__main__.py` | Interface de linha de comando |
| `exemplos/` | Quatro programas válidos e seis inválidos |
| `gerados/` | Python, tokens, AST e símbolos dos programas válidos |
| `testes/` | Suíte automatizada |
| `docs/gramatica.ebnf` | Gramática completa |
| `docs/relatorio_tecnico.md`, `.docx` e `.pdf` | Especificação formal |
| `docs/apresentacao_nova.pptx` | Apresentação editável com notas |
| `docs/roteiro_defesa.md` | Falas sugeridas, demonstração e perguntas |
| `docs/resultados_validacao.txt` | Registro reproduzível dos testes |

## Limites do escopo

A versão 1.0 não possui funções, vetores, escopos locais, operadores lógicos `and/or/not`, conversões explícitas, concatenação de texto nem comentários de bloco. Comparações encadeadas como `1 < x < 10` não fazem parte da gramática. Todos os ramos passam pela análise semântica, mesmo quando uma condição constante impediria sua execução.

Entradas incompatíveis com o tipo, divisão por zero e estouro/faixa numérica em operações são erros de execução do Python gerado. A análise semântica verifica **tipos**, não valores futuros. O runtime do Python também limita aninhamento recursivo e conversão de inteiros com quantidade muito grande de dígitos. Não há prova de término para laços.

## Linguagem destino e uso de IA

O enunciado permite Python desde que a equipe justifique a escolha e a informe ao professor no primeiro marco. A justificativa está no relatório. A escolha ainda precisa ser comunicada pela equipe; este material não afirma que o professor já a aprovou.

Esta versão contou com assistência do ChatGPT na proposta da linguagem, implementação, testes, documentação e apresentação. Os integrantes devem revisar o material, verificar se esse uso é autorizado e dominar as etapas para a defesa individual. Nenhuma divisão de tarefas nem aprovação do professor foi presumida.

## Contribuidores

Aqui estão os membros do time que contribuíram para o desenvolvimento deste projeto:

- Pedro Rockenbach Frosi           [@frosipedro](https://github.com/frosipedro)
- Cristian dos Santos Siqueira     [@CristianSSiqueira](https://github.com/CristianSSiqueira)
- Marco Antônio Hendges            [@Marco-Hendges](https://github.com/Marco-Hendges)
- William Rafael Fagundes          [@Williamrafaelfagundes](https://github.com/Williamrafaelfagundes)
