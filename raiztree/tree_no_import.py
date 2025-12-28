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

    if s.startswith("#"):
        return ("#", s)

    # Formato recomendado: "<tipo> <caminho>"
    if len(s) >= 3 and s[1] == " ":
        t = s[0]
        p = s[2:].strip()
        if p != "":
            if t in "dfplcbDs?":
                return (t, p)

    return ("?", s)


def split_and_normalize_path(path):
    s = path.strip()
    if s == "":
        return None

    if s == "." or s == "./":
        return []

    while s.startswith("./"):
        s = s[2:]

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

    if n == 0:
        if kind == "d":
            root["k"] = "d"
        return

    while i < n:
        name = parts[i]
        child = ensure_child(node, name)

        is_last = (i == n - 1)

        if not is_last:
            child["k"] = "d"
        else:
            if kind == "d":
                child["k"] = "d"
            elif kind == "f":
                if child["k"] != "d":
                    child["k"] = "f"
            else:
                pass

        node = child
        i += 1


def finalize_kinds(node):
    if len(node["ch"]) > 0:
        node["k"] = "d"

    names = list(node["ch"].keys())
    i = 0
    n = len(names)
    while i < n:
        finalize_kinds(node["ch"][names[i]])
        i += 1

    if node["k"] == "?" and len(node["ch"]) == 0:
        node["k"] = "f"


def sorted_child_names(node):
    names = list(node["ch"].keys())
    names.sort()
    return names


def parse_int_nonneg(s):
    t = s.strip()
    if t == "":
        return None

    # aceita apenas decimal simples
    i = 0
    n = len(t)
    while i < n:
        c = t[i]
        if c < "0" or c > "9":
            return None
        i += 1

    v = 0
    i = 0
    while i < n:
        v = v * 10 + (ord(t[i]) - ord("0"))
        i += 1
    return v


def get_max_depth(cfg):
    # Aceita: #max_depth=2   ou   #L=2   ou   #depth=2
    if "max_depth" in cfg:
        return parse_int_nonneg(cfg["max_depth"])
    if "L" in cfg:
        return parse_int_nonneg(cfg["L"])
    if "depth" in cfg:
        return parse_int_nonneg(cfg["depth"])
    return None


def count_kind(node, counts):
    # counts = [dirs, files]
    if node["k"] == "d":
        counts[0] += 1
    else:
        counts[1] += 1


def print_tree_children(node, prefix, depth, max_depth, counts):
    # depth: nível do 'node' em relação à raiz (raiz=0)
    # filhos terão depth+1
    if max_depth is not None and depth >= max_depth:
        return

    names = sorted_child_names(node)
    i = 0
    n = len(names)
    while i < n:
        name = names[i]
        child = node["ch"][name]
        is_last = (i == n - 1)

        if is_last:
            branch = "└── "
        else:
            branch = "├── "

        print(prefix + branch + name)
        count_kind(child, counts)

        if is_last:
            next_prefix = prefix + "    "
        else:
            next_prefix = prefix + "│   "

        print_tree_children(child, next_prefix, depth + 1, max_depth, counts)
        i += 1


def main():
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
            i += 1
            continue

        parts = split_and_normalize_path(payload)
        if parts is None:
            i += 1
            continue

        # Se veio um tipo não 'd'/'f', deixamos como desconhecido (vira arquivo se for folha)
        if kind != "d" and kind != "f":
            kind2 = "?"
        else:
            kind2 = kind

        insert_path(root, kind2, parts)
        i += 1

    finalize_kinds(root)

    max_depth = get_max_depth(cfg)

    # imprime raiz e filhos com conectores
    print(".")
    counts = [0, 0]  # [dirs, files] (sem contar a raiz)
    print_tree_children(root, "", 0, max_depth, counts)

    d = counts[0]
    f = counts[1]
    print()
    ds = "directory" if d == 1 else "directories"
    fs = "file" if f == 1 else "files"
    print(str(d) + " " + ds + ", " + str(f) + " " + fs)


main()