from typing import Dict
from entity.inode import Inode


class FileSystem:
    def __init__(self):
        self.inodes: Dict[str, Inode] = {}  # Mapa de ID para Inode
        self.root = Inode("/", True)  # Diretório raiz
        self.inodes[self.root.id] = self.root
        self.current_dir = self.root  # Diretório atual
        self.current_path = "/"  # Caminho atual para exibição
        self.next_block_id = 0  # Para alocar índices fictícios de blocos

    def create_file(self, name: str):
        if name in self.current_dir.entries:
            print(f"Erro: '{name}' já existe neste diretório.")
            return
        inode = Inode(name, False)
        self.inodes[inode.id] = inode
        self.current_dir.entries[name] = inode.id
        print(f"Arquivo '{name}' criado com sucesso.")

    def create_dir(self, name: str):
        if name in self.current_dir.entries:
            print(f"Erro: '{name}' já existe neste diretório.")
            return
        inode = Inode(name, True)
        self.inodes[inode.id] = inode
        self.current_dir.entries[name] = inode.id
        print(f"Diretório '{name}' criado com sucesso.")

    def ls(self):
        if not self.current_dir.entries:
            print("Diretório vazio.")
            return
        for name in self.current_dir.entries:
            inode = self.inodes[self.current_dir.entries[name]]
            type_str = "dir" if inode.is_dir else "file"
            print(f"{type_str}\t{name}")

    def cd(self, path: str):
        if path == ".":
            return  # Fica no diretório atual
        if path == "..":
            # Encontrar o diretório pai
            for inode in self.inodes.values():
                if inode.is_dir and self.current_dir.id in inode.entries.values():
                    self.current_dir = inode
                    self._update_path()
                    return
            if self.current_dir.id == self.root.id:
                print("Já está na raiz.")
            return
        if path not in self.current_dir.entries:
            print(f"Erro: Diretório '{path}' não encontrado.")
            return
        inode_id = self.current_dir.entries[path]
        inode = self.inodes[inode_id]
        if not inode.is_dir:
            print(f"Erro: '{path}' não é um diretório.")
            return
        self.current_dir = inode
        self._update_path()

    def _update_path(self):
        if self.current_dir.id == self.root.id:
            self.current_path = "/"
            return
        path = []
        current = self.current_dir
        while current.id != self.root.id:
            for inode in self.inodes.values():
                if inode.is_dir and current.id in inode.entries.values():
                    for name, id in inode.entries.items():
                        if id == current.id:
                            path.append(name)
                            current = inode
                            break
            if current.id == self.root.id:
                path.append("")
                break
        self.current_path = "/".join(reversed(path)) or "/"

        # Novo método para movimentação de arquivos
    def move(self, file_name: str, dest_path: str):
        # Verificar se o arquivo existe no diretório atual
        if file_name not in self.current_dir.entries:
            print(f"Erro: Arquivo '{file_name}' não encontrado no diretório atual.")
            print(f"Diretório atual: {self.current_path}")
            print(f"Conteúdo do diretório atual: {list(self.current_dir.entries.keys())}")
            return
        
        # Obter o inode do arquivo
        file_inode_id = self.current_dir.entries[file_name]
        file_inode = self.inodes[file_inode_id]
        
        # Verificar se é um arquivo (não diretório)
        if file_inode.is_dir:
            print(f"Erro: '{file_name}' é um diretório. Apenas arquivos podem ser movidos.")
            return

        # Encontrar o diretório de destino
        if dest_path == "/":
            dest_dir = self.root
        else:
            # Procurar o diretório de destino no diretório atual
            if dest_path not in self.current_dir.entries:
                print(f"Erro: Diretório de destino '{dest_path}' não encontrado.")
                return
            dest_inode_id = self.current_dir.entries[dest_path]
            dest_dir = self.inodes[dest_inode_id]
            if not dest_dir.is_dir:
                print(f"Erro: '{dest_path}' não é um diretório.")
                return

        # Verificar se já existe um arquivo com o mesmo nome no destino
        if file_name in dest_dir.entries:
            print(f"Erro: Já existe um arquivo ou diretório chamado '{file_name}' em '{dest_path}'.")
            return

        # Mover o arquivo: remover do diretório atual e adicionar ao destino
        del self.current_dir.entries[file_name]  # Remove do diretório atual
        dest_dir.entries[file_name] = file_inode_id  # Adiciona ao diretório de destino
        print(f"Arquivo '{file_name}' movido para '{dest_path}' com sucesso.")