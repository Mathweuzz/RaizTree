# RaizTree — Design (sem acesso direto ao disco)

## Visão geral

O RaizTree não varre o sistema de arquivos. Ele recebe uma lista de caminhos via stdin e apenas:
1) normaliza esses caminhos;
2) monta uma árvore em memória;
3) imprime a árvore.

A varredura fica por conta do shell (ex.: `find`).

## Protocolo de entrada (stdin)

### 1) Linha de configuração (opcional)
Se a primeira linha começar com `#`, ela é interpretada como configuração.

Exemplo:
#max_depth=4

(Se não houver `#`, todas as linhas são tratadas como caminhos.)

### 2) Linhas de dados (caminhos)
Aceitamos dois formatos:

**A) Com tipo (recomendado)**
Formato: `<tipo> <caminho>`

Onde `<tipo>` é um caractere do `find -printf '%y %p\n'`:
- `d` diretório
- `f` arquivo
- outros: link, socket etc. (tratamos como "não-diretório" por padrão)

Exemplo:
d .
d ./src
f ./src/main.c

**B) Sem tipo**
Formato: `<caminho>`

Exemplo:
.
./src
./src/main.c

> Sem tipo, o programa usa heurística: se um nó tem filhos, ele vira diretório; se não tem, vira arquivo.
> Isso pode errar em diretórios vazios. Por isso o formato com tipo é preferível.

## Normalização de caminhos

Dado um caminho `s`:
- remove espaços nas pontas;
- trata `.` e `./` como raiz;
- divide por `/` e remove segmentos vazios (corrige `//`);
- remove segmentos `.` no meio;
- ignora linhas vazias.

Resultado: lista de componentes, ex.:
"./src/lib/utils.c" -> ["src","lib","utils.c"]

## Estrutura de dados

Usamos apenas tipos nativos.

Cada nó é um dicionário:
- "k": tipo do nó ("d"=dir, "f"=file, "?"=desconhecido)
- "ch": filhos (dict nome -> nó)

Raiz:
root = {"k": "d", "ch": {}}

Inserção:
- cada componente cria/usa um filho.
- componentes intermediários são diretórios.
- o último componente recebe o tipo (se veio da entrada).

Finalização de tipos:
- se um nó tem filhos, é diretório.
- senão, se ficou "?", vira arquivo.

## Impressão

Nesta etapa (implementação básica), imprimimos com indentação simples:
.
  src
    main.c

Na próxima etapa, adicionamos conectores (`├──`, `└──`, `│   `).

## Contagem

Contamos durante o percurso:
- diretórios: nós "d" exceto a raiz
- arquivos: nós "f"