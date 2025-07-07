import uuid

class Inode:
    def __init__(self, name: str, is_dir: bool):
        self.id = str(uuid.uuid4())  # ID único para o inode
        self.name = name  # Nome do arquivo ou diretório
        self.is_dir = is_dir  # True para diretórios, False para arquivos
        self.size = 0  # Tamanho (0 para diretórios inicialmente)
        self.data_blocks = []  # Lista de índices fictícios de blocos de dados
        self.entries = {} if is_dir else None  # Para diretórios: dicionário {nome: inode_id}