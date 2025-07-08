from entity.file_system_linked import LinkedFileSystem

def main():
    fs = LinkedFileSystem()
    print("Sistema de Arquivos com Lista Encadeada (digite 'exit' para sair)")

    while True:
        print(f"\n{fs.current_path}$ ", end="")
        command = input().strip().split()
        if not command:
            continue
        cmd = command[0].lower()
        args = command[1:] if len(command) > 1 else []

        if cmd == "exit":
            break
        elif cmd == "create":
            if len(args) < 2:
                print("Uso: create [file|dir] <nome>")
            elif args[0] == "file":
                fs.create_file(args[1])
            elif args[0] == "dir":
                fs.create_dir(args[1])
            else:
                print("Uso: create [file|dir] <nome>")
        elif cmd == "ls":
            fs.ls()
        elif cmd == "cd":
            if len(args) != 1:
                print("Uso: cd <nome>")
            else:
                fs.cd(args[0])
        elif cmd == "write":
            if len(args) < 2:
                print("Uso: write <arquivo> <texto>")
            else:
                nome_arquivo = args[0]
                texto = ' '.join(args[1:])
                fs.write_file(nome_arquivo, texto)
        elif cmd == "read":
            if len(args) != 1:
                print("Uso: read <arquivo>")
            else:
                fs.read_file(args[0])
        elif cmd == "delete":
            if len(args) != 1:
                print("Uso: delete <nome>")
            else:
                fs.delete(args[0])

        elif cmd == "move":
            if len(args) != 2:
                print("Uso: move <arquivo> <destino>")
            else:
                fs.move(args[0], args[1])

        else:
            print("Comando inválido. Comandos disponíveis: create, ls, cd, write, read, delete, exit")

if __name__ == "__main__":
    main()
