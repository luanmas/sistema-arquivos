from entity.file_system_linked import SistemaArquivos
from entity.file_system_linked import benchmark_inode_access_linked_list

def main():
    fs = SistemaArquivos()
    print("Sistema de Arquivos com Alocação por Lista Encadeada (digite 'exit' para sair)")
    
    while True:
        print(f"\n{fs.caminho_atual}$ ", end="")
        comando = input().strip().split()
        if not comando:
            continue

        cmd = comando[0].lower()
        args = comando[1:] if len(comando) > 1 else []

        if cmd == "exit":
            break
        elif cmd == "create":
            if len(args) < 2:
                print("Uso: create [file|dir] <nome>")
            elif args[0] == "file":
                fs.criar_arquivo(args[1])
            elif args[0] == "dir":
                fs.criar_diretorio(args[1])
            else:
                print("Uso: create [file|dir] <nome>")
        elif cmd == "ls":
            fs.listar()
        elif cmd == "cd":
            if len(args) != 1:
                print("Uso: cd <nome>")
            else:
                fs.mudar_diretorio(args[0])
        elif cmd == "move":
            if len(args) != 2:
                print("Uso: move <nome_arquivo> <novo_diretorio>")
            else:
                fs.mover(args[0], args[1])
        elif cmd == "write":
            if len(args) < 2:
                print("Uso: write <arquivo> <texto>")
            else:
                nome_arquivo = args[0]
                texto = ' '.join(args[1:])
                fs.escrever_arquivo(nome_arquivo, texto)
        elif cmd == "read":
            if len(args) != 1:
                print("Uso: read <arquivo>")
            else:
                fs.ler_arquivo(args[0])
        elif cmd == "delete":
            if len(args) != 1:
                print("Uso: delete <nome>")
            else:
                fs.deletar(args[0])

        elif cmd == 'benchmark':
            fs.escrever_arquivo("teste.txt", "abcdefghij" * 100)  # Cria um arquivo com 100 bytes (10 blocos)

            for k in [0, 1, 5, 9, 1000, 5000]:
                tempo_inode = benchmark_inode_access_linked_list(fs, "teste.txt", k)
                print(f"LINKED-LIST: Acesso ao bloco {k}: {tempo_inode:.8f} milisegundos")
        elif cmd == "detalhes":
            if len(args) != 1:
                print("Uso: detalhes <arquivo|diretorio>")
            else:
                fs.detalhes(args[0])
        else:
            print("Comando inválido. Comandos disponíveis: create, ls, cd, move, write, read, delete, exit")

if __name__ == "__main__":
    main()
