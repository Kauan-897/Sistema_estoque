import sqlite3
import os

# Define o nome do arquivo do banco de dados
ARQUIVO_BANCO = "pedidos.db"

def inicializar_banco():
    """
    Verifica e cria todas as tabelas necessárias no banco de dados.
    Esta função é chamada apenas uma vez quando o aplicativo é iniciado.
    """
    conexao = None
    try:
        # Conecta (ou cria) o arquivo do banco
        conexao = sqlite3.connect(ARQUIVO_BANCO)
        cursor = conexao.cursor()

        print("Verificando banco de dados...")

        # --- Tabela 1: estoque ---
        # (Esta é a sua versão mais recente e simplificada)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE, 
            quantidade REAL NOT NULL
        )
        """)

        # --- Tabela 2: saidas ---
        # (Esta é a sua versão mais recente e simplificada)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS saidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario TEXT,
            cliente TEXT,
            produto TEXT NOT NULL,
            quantidade REAL NOT NULL,
            data TEXT
        )
        """)
        
        # (Se você tiver mais tabelas, adicione-as aqui)

        conexao.commit()
        print("Banco de dados e tabelas verificados/criados com sucesso!")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao inicializar o banco: {e}")
    finally:
        if conexao:
            conexao.close()

# --- Bloco de Execução Principal ---
# Se você executar este arquivo (banco.py) diretamente,
# ele irá criar o banco de dados.
if __name__ == "__main__":
    print("Inicializando o banco de dados diretamente...")
    inicializar_banco()
    print("Processo concluído.")