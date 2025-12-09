import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import csv

# --- 1. CRIAÇÃO DO BANCO ---
def criar_banco():
    try:
        conexao = sqlite3.connect("pedidos.db")
        cursor = conexao.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            valor REAL NOT NULL,
            lucro REAL NOT NULL,
            venda REAL NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS saidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario TEXT,
            cliente TEXT,
            produto TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            setor TEXT,
            total REAL,
            data TEXT
        )
        """)

        conexao.commit()
        print("Banco de dados criado/verificado com sucesso!")

    except sqlite3.Error as e:
        print(f"Erro ao criar o banco: {e}")

    finally:
        if conexao:
            conexao.close()


# --- 2. EXECUTA AO ABRIR O SISTEMA ---
criar_banco()


# --- 3. FUNÇÃO PARA ABRIR CSV ---
def abrir_pedido_csv():
    try:
        # Abre janela para escolher o arquivo
        caminho_arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo CSV",
            filetypes=[("Arquivos CSV", "*.csv")]
        )

        # Se o usuário cancelar, não faz nada
        if not caminho_arquivo:
            return

        # Lê o CSV separado por ponto e vírgula
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            leitor = csv.reader(arquivo, delimiter=';')
            cabecalho = next(leitor, None)  # Lê cabeçalho
            print(f"Cabeçalho: {cabecalho}")

            for linha in leitor:
                print(linha)

        messagebox.showinfo("Sucesso", f"Arquivo '{caminho_arquivo}' carregado com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")


# --- 4. INTERFACE TKINTER ---
janela = tk.Tk()
janela.title("Pedidos")
janela.geometry("600x400")

def estoque():
    try:
        import consulta
        consulta.abrir_janela_consulta(janela)
    except ModuleNotFoundError:
        messagebox.showerror("Erro", "Arquivo 'consulta.py' não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um problema ao abrir o estoque:\n{e}")

# --- MENU PRINCIPAL ---
menu_label = tk.Label(janela, text="Menu", font=("Arial", 12, "bold"))
menu_label.grid(row=0, column=0, padx=20, pady=20)

btn_csv = tk.Button(janela, text="Abrir Pedido CSV", command=abrir_pedido_csv)
btn_csv.grid(row=1, column=0, padx=20, pady=10)

btn_consulta = tk.Button(janela, text="Consultar Estoque", command=estoque)
btn_consulta.grid(row=2, column=0, padx=20, pady=10)

janela.mainloop()
