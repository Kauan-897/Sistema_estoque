import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import csv

# --- 2. FUNÇÃO DE LÓGICA (CADASTRO CSV) ---
def _cadastrar_itens_logic(janela_pai, memo_widget):
    
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    memo_widget.insert(tk.END, "Iniciando cadastro de itens via CSV...\n")
    
    conexao = None
    itens_cadastrados = 0
    itens_ignorados = 0
    
    try:
        caminho_arquivo = filedialog.askopenfilename(
            parent=janela_pai, 
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
                    
                    # --- CORRIGIDO (Erro 1) ---
                    # O comando SQL estava com uma vírgula a mais no final: VALUES (?, 0, )
                    # O correto é apenas VALUES (?, 0)
                    cursor.execute("""
                        INSERT INTO estoque (nome, quantidade)
                        VALUES (?, 0) 
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

# --- 3. FUNÇÃO: LÓGICA DO CADASTRO MANUAL ---
def _cadastrar_manual_logic(memo_widget, entry_nome, entry_qntd):
    """
    Pega os dados dos campos de entrada, valida e salva no banco.
    Reporta tudo no 'memo_widget'.
    """
    
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    
    nome = entry_nome.get().strip()
    qntd_str = entry_qntd.get().strip().replace(',', '.')
    
    if not nome:
        memo_widget.insert(tk.END, "ERRO: O campo 'Nome' não pode estar vazio.")
        memo_widget.config(state=tk.DISABLED)
        return
        
    try:
        quantidade = float(qntd_str)
        if quantidade < 0:
             raise ValueError("Quantidade não pode ser negativa")
    except ValueError:
        memo_widget.insert(tk.END, f"ERRO: Quantidade inválida ('{qntd_str}').\nInsira um número válido.")
        memo_widget.config(state=tk.DISABLED)
        return
    
    conexao = None
    try:
        conexao = sqlite3.connect("pedidos.db")
        cursor = conexao.cursor()
        
        cursor.execute("SELECT id FROM estoque WHERE nome = ?", (nome,))
        produto_existente = cursor.fetchone()
        
        if produto_existente:
            memo_widget.insert(tk.END, f"ERRO: O item '{nome}' já existe no estoque.\n\n")
            memo_widget.insert(tk.END, "Use a tela de 'Entrada de Estoque' para adicionar mais quantidade a um item existente.")
        else:
            memo_widget.insert(tk.END, f"Cadastrando novo item:\n  Nome: {nome}\n  Quantidade Inicial: {quantidade}\n")
            
            # --- CORRIGIDO (Erro 2) ---
            # O comando SQL antigo tentava inserir em colunas que não existem mais
            # (valor, lucro, venda).
            # O correto é inserir apenas 'nome' e 'quantidade'.
            cursor.execute("""
                INSERT INTO estoque (nome, quantidade)
                VALUES (?, ?)
            """, (nome, quantidade))
            
            conexao.commit()
            memo_widget.insert(tk.END, "\nSUCESSO: Novo item cadastrado no estoque!")
            
            entry_nome.delete(0, tk.END)
            entry_qntd.delete(0, tk.END)
            
    except Exception as e:
        if conexao:
            conexao.rollback()
        memo_widget.insert(tk.END, f"\n--- ERRO NO BANCO ---\nOcorreu um erro: {e}")
    
    finally:
        if conexao:
            conexao.close()
        memo_widget.config(state=tk.DISABLED)


# --- 4. FUNÇÃO PRINCIPAL (JANELA) ---
# (Esta função está CORRETA como você a enviou)
def abrir_janela_cadastro(janela_raiz):

   

    janela_cad = tk.Toplevel(janela_raiz)
    janela_cad.title("Cadastrar Itens no Estoque")
    janela_cad.geometry("600x600")
    
    janela_cad.transient(janela_raiz)
    janela_cad.grab_set()

    # --- Frame 1: Cadastro Manual (usará .grid() por dentro) ---
    frame_manual = tk.Frame(janela_cad, relief="groove", borderwidth=2)
    frame_manual.pack(fill="x", padx=15, pady=(15, 10))

    label_manual_titulo = tk.Label(frame_manual, text="Cadastro Manual", font=("Arial", 12, "bold"))
    label_manual_titulo.grid(row=0, column=0, columnspan=3, pady=(5, 10))

    label_nome = tk.Label(frame_manual, text="Nome do Item:")
    label_nome.grid(row=1, column=0, padx=10, pady=5, sticky="e")
    
    entry_nome = tk.Entry(frame_manual, width=40)
    entry_nome.grid(row=1, column=1, padx=5, pady=5)

    label_qntd = tk.Label(frame_manual, text="Quantidade Inicial:")
    label_qntd.grid(row=2, column=0, padx=10, pady=5, sticky="e")
    
    entry_qntd = tk.Entry(frame_manual, width=15)
    entry_qntd.grid(row=2, column=1, padx=5, pady=5, sticky="w") 

    btn_cadastrar = tk.Button(frame_manual, text="Salvar Item Manual",
                             command=lambda: _cadastrar_manual_logic(log_text, entry_nome, entry_qntd))
    btn_cadastrar.grid(row=1, column=2, rowspan=2, padx=10, pady=5, ipady=5)
    
    # --- Frame 2: Cadastro CSV (usará .pack() por dentro) ---
    frame_csv = tk.Frame(janela_cad, relief="groove", borderwidth=2)
    frame_csv.pack(fill="both", expand=True, padx=15, pady=10)

    menu_label = tk.Label(frame_csv, text="Cadastro em Massa via CSV", font=("Arial", 12, "bold"))
    menu_label.pack(pady=(5, 10))
    
    # --- LOG WIDGET (O "MEMO") ---
    log_frame = tk.Frame(frame_csv)
    log_scrollbar = tk.Scrollbar(log_frame)
    log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    log_text = tk.Text(log_frame, height=10, width=70, yscrollcommand=log_scrollbar.set)
    log_text.pack(side=tk.LEFT, fill="both", expand=True)
    log_scrollbar.config(command=log_text.yview)
    
    log_text.insert(tk.END, "Aguarde uma operação...")
    log_text.config(state=tk.DISABLED) 
    log_frame.pack(padx=10, pady=5, fill="both", expand=True)

    # --- BOTÃO CSV ---
    btn_csv = tk.Button(frame_csv, 
                        text="Selecionar Arquivo CSV para Cadastrar", 
                        command=lambda: _cadastrar_itens_logic(janela_cad, log_text))
    btn_csv.pack(padx=40, pady=(10, 10), fill='x')

    # --- Botão Fechar (fica fora dos frames) ---
    btn_fechar = tk.Button(janela_cad, text="Fechar Janela", command=janela_cad.destroy)
    btn_fechar.pack(padx=15, pady=(0, 15), side="bottom", fill="x")

    janela_cad.wait_window()