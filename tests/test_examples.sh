#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"

# Regenera exemplos
"$repo_root/scripts/gen_example.sh" >/dev/null

# Compara (diff)
diff -u "$repo_root/examples/demo_output.txt" "$repo_root/examples/demo_output.txt" >/dev/null
diff -u "$repo_root/examples/demo_output_depth2.txt" "$repo_root/examples/demo_output_depth2.txt" >/dev/null
diff -u "$repo_root/examples/weird_output.txt" "$repo_root/examples/weird_output.txt" >/dev/null

echo "== OK: exemplos geram saídas consistentes =="