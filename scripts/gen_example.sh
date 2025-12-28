#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

demo_root="$repo_root/examples/demo_fs"
py="$repo_root/raiztree/tree_no_import.py"

# Recria a árvore demo (somente dentro do repo)
rm -rf "$demo_root"
mkdir -p \
  "$demo_root/src/lib" \
  "$demo_root/src/bin" \
  "$demo_root/docs" \
  "$demo_root/assets/icons"

# Arquivos
: > "$demo_root/README.md"
: > "$demo_root/src/main.c"
: > "$demo_root/src/lib/utils.c"
: > "$demo_root/src/lib/math.c"
: > "$demo_root/src/bin/app"
: > "$demo_root/docs/design.md"
: > "$demo_root/assets/icons/logo.svg"

# Um diretório vazio (pra mostrar que com input tipado ele aparece)
mkdir -p "$demo_root/empty_dir"

# Gera entradas e saídas
out_dir="$repo_root/examples"
mkdir -p "$out_dir"

# Entrada tipada (recomendada)
(
  cd "$demo_root"
  find . -printf '%y %p\n'
) > "$out_dir/demo_input_typed.txt"

# Saída completa
python "$py" < "$out_dir/demo_input_typed.txt" > "$out_dir/demo_output.txt"

# Saída com max_depth=2 (via protocolo de primeira linha)
(
  echo "#max_depth=2"
  cat "$out_dir/demo_input_typed.txt"
) | python "$py" > "$out_dir/demo_output_depth2.txt"

# Exemplo "sujo" (sem tipo) pra testar normalização (// e ./ no meio)
cat > "$out_dir/weird_input_plain.txt" << 'EOT'
.
./src
./src//lib
./src/lib/./utils.c
./src/lib//math.c
./docs
./docs/./design.md
./assets/icons//logo.svg
./empty_dir
EOT

python "$py" < "$out_dir/weird_input_plain.txt" > "$out_dir/weird_output.txt"

echo "== OK =="
echo "Gerado:"
echo "  examples/demo_input_typed.txt"
echo "  examples/demo_output.txt"
echo "  examples/demo_output_depth2.txt"
echo "  examples/weird_input_plain.txt"
echo "  examples/weird_output.txt"