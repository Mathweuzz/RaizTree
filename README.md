Implementação do estilo do comando `tree` em Python 3, mas sem acesso direto ao sistema de arquivos no núcleo.
A lista de caminhos entra via stdin (ex.: `find . | python raiztree/tree_no_import.py`).

Restrição do núcleo:
- o arquivo `raiztree/tree_no_import.py` não contém nenhuma linha com a palavra proibida.