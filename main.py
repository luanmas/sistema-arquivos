from entity.file_system import FileSystem, benchmark_inode_delete
from entity.file_system import benchmark_inode_access, benchmark_move_inode, benchmark_write_file
from entity.file_system_linked import SistemaArquivos, benchmark_linked_delete
from entity.file_system_linked import benchmark_inode_access_linked_list
from entity.file_system_linked import benchmark_move_linked_list

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
        elif cmd == "detalhes":
            if len(args) != 1:
                print("Uso: detalhes <arquivo|diretorio>")
            else:
                fs.detalhes(args[0])
        elif cmd == "status":
            fs.status()
        elif cmd == 'benchmark-access':
            fs = FileSystem()
            fs_linked = SistemaArquivos()
            fs.write_file("teste.txt", "abcdefghij" * 10000)
            fs_linked.escrever_arquivo("teste.txt", "abcdefghij" * 10000)
            for k in [5, 10, 50, 900, 1000, 5000]:
                tempo_inode = benchmark_inode_access(fs, "teste.txt", k)
                tempo_linked_list = benchmark_inode_access_linked_list(fs_linked, "teste.txt", k)
                print(f"Bloco {k}: INODE = {tempo_inode:.6f} ms | LINKED LIST = {tempo_linked_list:.6f} ms")  
        elif cmd == 'benchmark-write':
            print("\n=== Benchmark de Escrita ===")
            sizes = [10, 100, 1000]
            for size in sizes:
                result = benchmark_write_file(fs, f"bench_{size}.txt", size, 1)
                print(f"Tamanho: {size} bytes | "
                      f"Tempo médio: {result['average_time']:.4f} ms |") 
        elif cmd == 'benchmark-delete':
            fs_inode = FileSystem()  
            fs_linked = SistemaArquivos() 
            
            file_sizes = [100, 1000] 
            file_names = ["teste1.txt", "teste2.txt"]

            print("\n=== Benchmark de Exclusão com Inode ===")
            for name, size in zip(file_names, file_sizes):
                fs_inode.write_file(name, "abcdefghij" * (size // 10))  
                inode_id = fs_inode.current_dir.entries.get(name)
                if inode_id is not None:
                    blocks = len(fs_inode.inodes[inode_id].data_blocks) if hasattr(fs_inode.inodes[inode_id], 'data_blocks') else 'N/A'
                    print(f"Arquivo '{name}' criado com {size} bytes (blocos: {blocks}).")

            for name in file_names:
                tempo_delete = benchmark_inode_delete(fs_inode, name)
                if tempo_delete >= 0:
                    print(f"INODE: Exclusão do arquivo '{name}': {tempo_delete:.8f} milisegundos")
            
            print("\n=== Benchmark de Exclusão com Alocação Encadeada ===")
            for name, size in zip(file_names, file_sizes):
                fs_linked.escrever_arquivo(name, "abcdefghij" * (size // 10))  

                inode_id = fs_linked.diretorio_atual.entries.get(name)
                if inode_id is not None:
                    blocks = 'Encadeado' if hasattr(fs_linked.nos[inode_id], 'first_block') else 'N/A'
                    print(f"Arquivo '{name}' criado com {size} bytes (blocos: {blocks}).")

            for name in file_names:
                tempo_delete = benchmark_linked_delete(fs_linked, name)
                if tempo_delete >= 0:
                    print(f"ENC: Exclusão do arquivo '{name}': {tempo_delete:.8f} milisegundos")
            print("\n=== Fim do Benchmark ===")
        elif cmd == 'benchmark-move':
            fs_linked = SistemaArquivos()
            fs_linked.escrever_arquivo("arquivo2.txt", "abcdefghij")
            fs_linked.criar_diretorio('destino_linked')
            fs.write_file("arquivo1.txt", "abcdefghij")
            fs.create_dir('destino')
            tempo_inode = benchmark_move_inode(fs, "arquivo1.txt", "destino")
            tempo_linked = benchmark_move_linked_list(fs_linked, "arquivo2.txt", "destino_linked")
            if tempo_inode >= 0:
                print(f"Tempo para mover i-node: {tempo_inode:.4f} ms")
            if tempo_linked >= 0:
                print(f"Tempo para mover lista encadeada: {tempo_linked:.4f} ms")
        else:
            print("Comando inválido. Comandos disponíveis: create, ls, cd, move, exit")

if __name__ == "__main__":
    main()