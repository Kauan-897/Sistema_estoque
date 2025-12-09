import mysql.connector
from mysql.connector import errorcode
import tkinter as tk
from tkinter import simpledialog, messagebox
import os
from dotenv import load_dotenv 

# Carrega as variáveis do arquivo .env
load_dotenv()

# --- CONFIGURAÇÕES PADRÃO ---
# O sistema tenta pegar do .env. Se não achar, usa um valor padrão vazio ou o que definir.
DB_CONFIG = {
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''), # <--- AQUI A MÁGICA! Ele lê do arquivo oculto
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'database': os.getenv('DB_NAME', 'Pedido'),
    'raise_on_warnings': True
}

# --- DEFINIÇÃO DAS TABELAS (Schema Completo e Atualizado) ---
TABLES = {}

TABLES['estoque'] = """
    CREATE TABLE IF NOT EXISTS estoque (
        id INT PRIMARY KEY AUTO_INCREMENT,
        codigo VARCHAR(50), 
        Nome VARCHAR(255) NOT NULL UNIQUE,
        status VARCHAR(10) NOT NULL DEFAULT 'Ativo',
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

# --- FUNÇÃO AUXILIAR: PEDIR SENHA ---
def _pedir_senha_usuario():
    """Abre uma janela popup pedindo a senha correta."""
    root = tk.Tk()
    root.withdraw() # Esconde a janela principal cinza
    
    senha = simpledialog.askstring(
        "Erro de Conexão MySQL", 
        "A senha do banco de dados está incorreta ou mudou.\n\nPor favor, digite a senha do MySQL deste computador:",
        show='*' # Mostra asteriscos em vez da senha
    )
    root.destroy()
    return senha

# --- CONEXÃO INTELIGENTE ---
def conectar():
    global DB_CONFIG
    tentativas = 0
    
    while tentativas < 3: # Tenta no máximo 3 vezes para não travar
        try:
            conexao = mysql.connector.connect(**DB_CONFIG)
            return conexao
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                # Se a senha estiver errada, pede ao usuário
                nova_senha = _pedir_senha_usuario()
                if nova_senha is not None:
                    DB_CONFIG['password'] = nova_senha # Atualiza a configuração global
                    tentativas += 1
                    continue # Tenta de novo com a nova senha
                else:
                    return None # Usuário cancelou
            else:
                print(f"Erro de Conexão: {err}")
                return None
    return None

def inicializar_banco():
    global DB_CONFIG
    conexao = None
    cursor = None
    
    # 1. Tenta conectar ao Servidor (sem banco específico) para criar o banco
    while True:
        try:
            db_sem_db = DB_CONFIG.copy()
            db_sem_db.pop('database', None)
            
            conexao = mysql.connector.connect(**db_sem_db)
            cursor = conexao.cursor()
            
            # Se conectou, sai do loop
            break
            
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                nova_senha = _pedir_senha_usuario()
                if nova_senha is not None:
                    DB_CONFIG['password'] = nova_senha # Atualiza para o futuro
                    continue # Tenta de novo
                else:
                    messagebox.showerror("Erro Fatal", "Não foi possível conectar ao MySQL. O programa será fechado.")
                    return # Sai da função
            else:
                messagebox.showerror("Erro", f"Erro ao conectar ao servidor MySQL: {err}")
                return

    # 2. Cria o Banco e as Tabelas
    try:
        try:
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']} DEFAULT CHARACTER SET 'utf8'")
            print(f"Base de dados '{DB_CONFIG['database']}' criada.")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DB_CREATE_EXISTS:
                print(f"Base de dados '{DB_CONFIG['database']}' já existe.")
            else:
                raise err
        
        # Conecta ao banco correto agora
        conexao.database = DB_CONFIG['database']
        
        print("A verificar tabelas...")
        for nome, script in TABLES.items():
            try:
                cursor.execute(script)
            except mysql.connector.Error as err:
                print(f"Erro ao criar tabela '{nome}': {err}")

        # Verifica Usuário Admin
        print("A verificar usuário padrão...")
        cursor.execute("SELECT COUNT(id) FROM usuarios")
        num_usuarios = cursor.fetchone()[0]
        
        if num_usuarios == 0:
            print("Criando usuário 'admin'...")
            cursor.execute("INSERT INTO usuarios (username, password_hash, nivel) VALUES ('admin', 'admin', 'admin')")
            conexao.commit()
        
        print("Banco de dados pronto!")

    except mysql.connector.Error as err:
        print(f"ERRO FATAL NA INICIALIZAÇÃO: {err}")
        messagebox.showerror("Erro Fatal", f"Erro ao criar tabelas: {err}")
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()