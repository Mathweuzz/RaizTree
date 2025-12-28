def read_all_lines():
    paths = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        paths.append(line)
    return paths

def main():
    paths = read_all_lines()

    print("== RaizTree / estágio 0: eco de entrada ==")
    print("Linhas lidas: ", len(paths))

    i = 0
    n = len(paths)
    while i < n:
        print(paths[i])
        i += 1

main()