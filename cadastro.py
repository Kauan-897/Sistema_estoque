import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import csv

# --- 1. FUNÇÃO DE CRIAÇÃO DO BANCO ---
# É bom ter aqui para garantir que a tabela existe
def criar_banco():
    try:
        conexao = sqlite3.connect("pedidos.db")
        cursor = conexao.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE, 
            quantidade INTEGER NOT NULL,
            valor REAL NOT NULL,
            lucro REAL NOT NULL,
            venda REAL NOT NULL
        )
        """)
        conexao.commit()
    except sqlite3.Error as e:
        print(f"Erro ao verificar/criar banco: {e}")
    finally:
        if conexao:
            conexao.close()

# --- 2. FUNÇÃO DE LÓGICA (INTERNA) ---
# Esta é a função que faz o trabalho
def _cadastrar_itens_logic(janela_pai, memo_widget):
    
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    memo_widget.insert(tk.END, "Iniciando cadastro de itens...\n")
    
    conexao = None
    itens_cadastrados = 0
    itens_ignorados = 0
    
    try:
        caminho_arquivo = filedialog.askopenfilename(
            parent=janela_pai, # Usa a janela Toplevel como "pai"
            title="Selecione o arquivo CSV de Itens",
            filetypes=[("Arquivos CSV", "*.csv")]
        )
        if not caminho_arquivo:
            memo_widget.insert(tk.END, "Cadastro cancelado pelo usuário.")
            memo_widget.config(state=tk.DISABLED)
            return
            
        conexao = sqlite3.connect("pedidos.db")
        cursor = conexao.cursor()

        with open(caminho_arquivo, "r", encoding="latin-1") as arquivo:
            leitor = csv.reader(arquivo, delimiter=';')
            
            next(leitor, None) # Pula a primeira linha (Cliente)
            
            memo_widget.insert(tk.END, "Lendo produtos do arquivo...\n")
            memo_widget.insert(tk.END, "-------------------------------------\n")

            for linha in leitor:
                if not linha or not linha[0]:
                    continue
                
                produto_nome = linha[0].strip()

                cursor.execute("SELECT id FROM estoque WHERE nome = ?", (produto_nome,))
                produto_existente = cursor.fetchone()
                
                if produto_existente:
                    memo_widget.insert(tk.END, f"  -> Ignorado: '{produto_nome}' (Já existe)\n")
                    itens_ignorados += 1
                else:
                    memo_widget.insert(tk.END, f"  -> Cadastrando: '{produto_nome}'...")
                    cursor.execute("""
                        INSERT INTO estoque (nome, quantidade, valor, lucro, venda)
                        VALUES (?, 0, 0.0, 0.0, 0.0)
                    """, (produto_nome,))
                    memo_widget.insert(tk.END, " OK\n")
                    itens_cadastrados += 1

            memo_widget.insert(tk.END, "-------------------------------------\n")
            
            if itens_cadastrados > 0:
                conexao.commit()
                memo_widget.insert(tk.END, f"SUCESSO: {itens_cadastrados} novos itens cadastrados.\n")
                messagebox.showinfo("Sucesso", 
                                    f"{itens_cadastrados} novos itens cadastrados!", 
                                    parent=janela_pai)
            else:
                memo_widget.insert(tk.END, "Nenhum item novo encontrado para cadastrar.\n")

    except Exception as e:
        if conexao:
            conexao.rollback()
        memo_widget.insert(tk.END, f"\n--- ERRO ---\nOcorreu um erro: {e}")
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}", parent=janela_pai)
        
    finally:
        if conexao:
            conexao.close()
        memo_widget.config(state=tk.DISABLED)

# --- 3. FUNÇÃO PRINCIPAL (CRIA A JANELA) ---
# Esta é a função que o seu MENU vai chamar
def abrir_janela_cadastro(janela_raiz):
    
    # Garante que a tabela existe antes de abrir
    criar_banco()
    
    # Cria a janela "filha" (Toplevel)
    janela_cad = tk.Toplevel(janela_raiz)
    janela_cad.title("Cadastrar Itens de CSV")
    janela_cad.geometry("600x450")
    
    janela_cad.transient(janela_raiz)
    janela_cad.grab_set()

    # --- Conteúdo da Janela ---
    menu_label = tk.Label(janela_cad, text="Cadastrar Itens no Estoque via CSV", font=("Arial", 12, "bold"))
    menu_label.pack(pady=15)
    
    # --- LOG WIDGET (O "MEMO") ---
    log_frame = tk.Frame(janela_cad)
    log_scrollbar = tk.Scrollbar(log_frame)
    log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    log_text = tk.Text(log_frame, height=15, width=70, yscrollcommand=log_scrollbar.set)
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    log_scrollbar.config(command=log_text.yview)
    
    log_text.insert(tk.END, "Aguardando seleção do arquivo CSV...")
    log_text.config(state=tk.DISABLED) 
    log_frame.pack(padx=15, pady=5, fill=tk.BOTH, expand=True)

    # --- BOTÕES ---
    btn_csv = tk.Button(janela_cad, 
                        text="Selecionar Arquivo CSV para Cadastrar", 
                        command=lambda: _cadastrar_itens_logic(janela_cad, log_text))
    btn_csv.pack(padx=40, pady=(10, 5), fill='x')

    btn_fechar = tk.Button(janela_cad, text="Fechar", command=janela_cad.destroy)
    btn_fechar.pack(padx=40, pady=5, fill='x')

    janela_cad.wait_window()