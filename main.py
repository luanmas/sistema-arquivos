from entity.file_system import FileSystem

def main():
    fs = FileSystem()
    print("Sistema de Arquivos Simulado (digite 'exit' para sair)")
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
        elif cmd == "move":
            if len(args) != 2:
                print("Uso: move <nome_arquivo> <novo_diretorio>")
            else:
                fs.move(args[0], args[1])
        else:
            print("Comando inválido. Comandos disponíveis: create, ls, cd, move, exit")

if __name__ == "__main__":
    main()