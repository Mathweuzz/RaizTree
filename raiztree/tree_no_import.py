def parse_config_line(line):
    cfg = {}
    s = line.strip()
    if not s.startswith("#"):
        return cfg
    s = s[1:].strip()
    if s == "":
        return cfg

    parts = s.split()
    i = 0
    n = len(parts)
    while i < n:
        token = parts[i]
        eq = token.find("=")
        if eq >= 0:
            k = token[:eq].strip()
            v = token[eq+1:].strip()
            if k != "":
                cfg[k] = v
        else:
            cfg[token] = "1"
        i += 1
    return cfg


def parse_typed_or_plain_line(line):
    s = line.strip()
    if s == "":
        return (None, None)

    # Linha de config
    if s.startswith("#"):
        return ("#", s)

    # Formato recomendado: "<tipo> <caminho>"
    # Ex: "d ./src" ou "f ./src/main.c"
    if len(s) >= 3 and s[1] == " ":
        t = s[0]
        p = s[2:].strip()
        if p != "":
            # Aceita tipos comuns do find %y
            if t in "dfplcbDs?":
                return (t, p)

    # Sem tipo
    return ("?", s)


def split_and_normalize_path(path):
    s = path.strip()
    if s == "":
        return None

    if s == "." or s == "./":
        return []

    # remove prefixos "./" repetidos
    while s.startswith("./"):
        s = s[2:]

    # remove barras iniciais extras
    while s.startswith("/"):
        s = s[1:]

    if s == "":
        return []

    raw = s.split("/")
    parts = []
    i = 0
    n = len(raw)
    while i < n:
        seg = raw[i]
        if seg == "" or seg == ".":
            i += 1
            continue
        parts.append(seg)
        i += 1

    return parts


def new_node(kind):
    return {"k": kind, "ch": {}}


def ensure_child(parent, name):
    ch = parent["ch"]
    if name in ch:
        return ch[name]
    node = new_node("?")
    ch[name] = node
    return node


def insert_path(root, kind, parts):
    node = root
    i = 0
    n = len(parts)

    # Caminho raiz (.)
    if n == 0:
        if kind == "d":
            root["k"] = "d"
        return

    while i < n:
        name = parts[i]
        child = ensure_child(node, name)

        is_last = (i == n - 1)

        if not is_last:
            # intermediários sempre diretórios
            child["k"] = "d"
        else:
            # último componente recebe tipo se for explícito
            if kind == "d":
                child["k"] = "d"
            elif kind == "f":
                # só marca arquivo se não for diretório conhecido
                if child["k"] != "d":
                    child["k"] = "f"
            else:
                # desconhecido: deixa como está (pode ser promovido depois)
                pass

        node = child
        i += 1


def finalize_kinds(node):
    # Se tem filhos, é diretório
    if len(node["ch"]) > 0:
        node["k"] = "d"

    # Ajusta recursivamente
    names = list(node["ch"].keys())
    i = 0
    n = len(names)
    while i < n:
        finalize_kinds(node["ch"][names[i]])
        i += 1

    # Se continua desconhecido e não tem filhos, vira arquivo
    if node["k"] == "?" and len(node["ch"]) == 0:
        node["k"] = "f"


def sorted_child_names(node):
    names = list(node["ch"].keys())
    names.sort()
    return names


def print_simple(node, name, depth, counts, is_root):
    # counts = [dirs, files]
    if not is_root:
        if node["k"] == "d":
            counts[0] += 1
        else:
            counts[1] += 1

    indent = "  " * depth
    if is_root:
        print(".")
    else:
        print(indent + name)

    names = sorted_child_names(node)
    i = 0
    n = len(names)
    while i < n:
        child_name = names[i]
        child_node = node["ch"][child_name]
        print_simple(child_node, child_name, depth + 1, counts, False)
        i += 1


def main():
    # Lê tudo
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        lines.append(line)

    cfg = {}
    start = 0
    if len(lines) > 0:
        first = lines[0].strip()
        if first.startswith("#"):
            cfg = parse_config_line(first)
            start = 1

    root = new_node("d")

    i = start
    n = len(lines)
    while i < n:
        kind, payload = parse_typed_or_plain_line(lines[i])
        if kind is None:
            i += 1
            continue
        if kind == "#":
            # ignora configs no meio por enquanto
            i += 1
            continue

        parts = split_and_normalize_path(payload)
        if parts is None:
            i += 1
            continue

        insert_path(root, kind, parts)
        i += 1

    finalize_kinds(root)

    counts = [0, 0]  # [dirs, files]
    print_simple(root, ".", 0, counts, True)

    # max_depth (por enquanto não aplicado na impressão simples; fica como base p/ próxima etapa)
    _ = cfg

    d = counts[0]
    f = counts[1]
    print()
    if d == 1:
        ds = "directory"
    else:
        ds = "directories"
    if f == 1:
        fs = "file"
    else:
        fs = "files"
    print(str(d) + " " + ds + ", " + str(f) + " " + fs)


main()