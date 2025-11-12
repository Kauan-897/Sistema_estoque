import mysql.connector
from mysql.connector import errorcode
import os # Importei o OS, apesar de não o estarmos a usar agora

# ---
# CONFIGURE OS SEUS DADOS AQUI
# ---
DB_CONFIG = {
    'user': 'root',
    'password': 'root123', # <-- MUDE ISTO
    'host': '127.0.0.1',           # (Pode ser 'localhost')
    'database': 'Pedido',          # (O nome do seu banco)
    'raise_on_warnings': True
}

# (O script SQL que criámos, guardado aqui para a inicialização)
TABLES = {}
TABLES['estoque'] = """
    CREATE TABLE IF NOT EXISTS estoque (
        id INT PRIMARY KEY AUTO_INCREMENT,
        Nome VARCHAR(255) NOT NULL UNIQUE,
        Quantidade DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
        DataCadastro DATE DEFAULT (CURRENT_DATE)
    )"""
TABLES['usuarios'] = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(50) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL, 
        nivel VARCHAR(20) DEFAULT 'vendedor'
    )"""
TABLES['clientes'] = """
    CREATE TABLE IF NOT EXISTS clientes (
        id INT PRIMARY KEY AUTO_INCREMENT,
        nome VARCHAR(255) NOT NULL UNIQUE,
        telefone VARCHAR(20),
        email VARCHAR(100)
    )"""
TABLES['fornecedores'] = """
    CREATE TABLE IF NOT EXISTS fornecedores (
        id INT PRIMARY KEY AUTO_INCREMENT,
        nome VARCHAR(255) NOT NULL UNIQUE,
        contato VARCHAR(100)
    )"""
TABLES['saidas'] = """
    CREATE TABLE IF NOT EXISTS saidas (
        id INT PRIMARY KEY AUTO_INCREMENT,
        estoque_id INT NOT NULL, 
        cliente_id INT NOT NULL, 
        usuario_id INT NOT NULL, 
        Quantidade DECIMAL(10, 2) NOT NULL,
        DataSaida DATE DEFAULT (CURRENT_DATE),
        FOREIGN KEY (estoque_id) REFERENCES estoque(id),
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )"""
TABLES['entradas'] = """
    CREATE TABLE IF NOT EXISTS entradas (
        id INT PRIMARY KEY AUTO_INCREMENT,
        estoque_id INT NOT NULL,
        fornecedor_id INT,
        usuario_id INT NOT NULL,
        Quantidade DECIMAL(10, 2) NOT NULL,
        DataEntrada DATE DEFAULT (CURRENT_DATE),
        FOREIGN KEY (estoque_id) REFERENCES estoque(id),
        FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )"""
TABLES['consignado'] = """
    CREATE TABLE IF NOT EXISTS consignado (
        id INT PRIMARY KEY AUTO_INCREMENT,
        estoque_id INT NOT NULL,    
        fornecedor_id INT NOT NULL, 
        Quantidade DECIMAL(10, 2) NOT NULL,
        Valor DECIMAL(10, 2) NOT NULL,
        DataChegada DATE DEFAULT (CURRENT_DATE),
        DataColeta DATE DEFAULT NULL,     
        FOREIGN KEY (estoque_id) REFERENCES estoque(id),
        FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
    )"""
TABLES['consignado_usos'] = """
    CREATE TABLE IF NOT EXISTS consignado_usos (
        id INT PRIMARY KEY AUTO_INCREMENT,
        estoque_id INT NOT NULL,
        fornecedor_id INT NOT NULL,
        usuario_id INT NOT NULL,
        QuantidadeUsada DECIMAL(10, 2) NOT NULL,
        ValorUnitario DECIMAL(10, 2) NOT NULL,
        DataUso DATE DEFAULT (CURRENT_DATE),
        FOREIGN KEY (estoque_id) REFERENCES estoque(id),
        FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )"""


def conectar():
    """Conecta ao servidor MySQL e retorna o objeto de conexão."""
    try:
        conexao = mysql.connector.connect(**DB_CONFIG)
        return conexao
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Erro: Nome de utilizador ou palavra-passe errada.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"Erro: A base de dados '{DB_CONFIG['database']}' não existe.")
        else:
            print(f"Ocorreu um erro: {err}")
        return None # Retorna None se a conexão falhar

def inicializar_banco():
    """
    Conecta ao MySQL e executa o script de criação de tabelas.
    Isto é chamado APENAS UMA VEZ pelo menu.py.
    """
    conexao = None
    cursor = None
    try:
        # Tenta conectar-se ao servidor
        # (mas não a uma base de dados específica ainda)
        db_sem_db = DB_CONFIG.copy()
        db_sem_db.pop('database', None)
        
        conexao = mysql.connector.connect(**db_sem_db)
        cursor = conexao.cursor()
        
        # Tenta criar o banco de dados
        try:
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']} DEFAULT CHARACTER SET 'utf8'")
            print(f"Base de dados '{DB_CONFIG['database']}' criada.")
        except mysql.connector.Error as err:
            # Se der erro 1007, a base de dados já existe, o que é bom
            if err.errno == errorcode.ER_DB_CREATE_EXISTS:
                print(f"Base de dados '{DB_CONFIG['database']}' já existe.")
            else:
                raise err
        
        # Agora, conecta-se à base de dados correta
        conexao.database = DB_CONFIG['database']
        
        # Cria todas as tabelas na ordem
        print("A verificar/criar tabelas...")
        for nome, script in TABLES.items():
            try:
                cursor.execute(script)
                # print(f"Tabela '{nome}' verificada/criada.")
            except mysql.connector.Error as err:
                print(f"Erro ao criar tabela '{nome}': {err}")

        print("Base de dados pronta!")

    except mysql.connector.Error as err:
        print(f"ERRO FATAL: Não foi possível ligar ao MySQL: {err}")
        
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()