import tkinter as tk
from tkinter import filedialog, messagebox
import banco
import csv

# =============================================================================
# LÓGICA DE NEGÓCIO (Mantida igual)
# =============================================================================

def _cadastrar_itens_logic(janela_pai, memo_widget):
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    memo_widget.insert(tk.END, "Iniciando cadastro via CSV...\n")
    
    conexao = None
    cursor = None 
    itens_cadastrados = 0
    itens_ignorados = 0
    
    try:
        caminho_arquivo = filedialog.askopenfilename(
            parent=janela_pai, 
            title="Selecione o arquivo CSV",
            filetypes=[("Arquivos CSV", "*.csv")]
        )
        if not caminho_arquivo:
            memo_widget.insert(tk.END, "Cadastro cancelado.")
            memo_widget.config(state=tk.DISABLED)
            return
            
        conexao = banco.conectar()
        if not conexao:
             memo_widget.insert(tk.END, "ERRO: Sem conexão com MySQL.")
             memo_widget.config(state=tk.DISABLED)
             return
        cursor = conexao.cursor()

        with open(caminho_arquivo, "r", encoding="latin-1") as arquivo:
            leitor = csv.reader(arquivo, delimiter=';')
            next(leitor, None) 
            next(leitor, None) 
            
            memo_widget.insert(tk.END, "Lendo arquivo...\n-----------------\n")

            for linha in leitor:
                if not linha or len(linha) < 2: continue
                
                produto_codigo = None 
                produto_nome = linha[1].strip() 
                
                cursor.execute("SELECT id FROM estoque WHERE nome = %s", (produto_nome,))
                if cursor.fetchone():
                    memo_widget.insert(tk.END, f" -> Ignorado: '{produto_nome}' (Nome já existe)\n")
                    itens_ignorados += 1
                    continue

                memo_widget.insert(tk.END, f" -> Cadastrando: {produto_nome}...")
                
                cursor.execute("""
                    INSERT INTO estoque (codigo, nome, quantidade)
                    VALUES (%s, %s, 0) 
                """, (None, produto_nome,))
                
                memo_widget.insert(tk.END, " OK\n")
                itens_cadastrados += 1

            if itens_cadastrados > 0:
                conexao.commit()
                memo_widget.insert(tk.END, f"\nSUCESSO: {itens_cadastrados} itens cadastrados.")
                messagebox.showinfo("Sucesso", "Itens cadastrados!", parent=janela_pai)
            else:
                memo_widget.insert(tk.END, "\nNenhum item novo cadastrado.")

    except Exception as e:
        if conexao: conexao.rollback()
        memo_widget.insert(tk.END, f"\nERRO: {e}")
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}", parent=janela_pai)
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()
        memo_widget.config(state=tk.DISABLED)
        
def _cadastrar_manual_logic(memo_widget, entry_codigo, entry_nome, entry_qntd):
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    
    codigo = entry_codigo.get().strip()
    nome = entry_nome.get().strip()
    qntd_str = entry_qntd.get().strip().replace(',', '.')
    
    if not nome:
        memo_widget.insert(tk.END, "ERRO: O campo 'Nome' é obrigatório.")
        memo_widget.config(state=tk.DISABLED)
        return
        
    try:
        quantidade = float(qntd_str)
        if quantidade < 0: raise ValueError
    except ValueError:
        memo_widget.insert(tk.END, f"ERRO: Quantidade inválida.")
        memo_widget.config(state=tk.DISABLED)
        return
    
    conexao = None
    cursor = None
    try:
        conexao = banco.conectar()
        if not conexao:
             memo_widget.insert(tk.END, "ERRO: Sem conexão com MySQL.")
             return
        cursor = conexao.cursor()
        
        cursor.execute("SELECT id FROM estoque WHERE nome = %s", (nome,))
        if cursor.fetchone():
            memo_widget.insert(tk.END, f"ERRO: O item '{nome}' já existe.\n")
        else:
            code_ok = True
            if codigo:
                cursor.execute("SELECT id FROM estoque WHERE codigo = %s", (codigo,))
                if cursor.fetchone():
                     memo_widget.insert(tk.END, f"ERRO: O código '{codigo}' já está em uso.\n")
                     code_ok = False
            
            if code_ok:
                memo_widget.insert(tk.END, f"Cadastrando:\n  Cód: {codigo}\n  Nome: {nome}\n  Qtd: {quantidade}\n")
                
                cursor.execute("""
                    INSERT INTO estoque (codigo, nome, quantidade)
                    VALUES (%s, %s, %s)
                """, (codigo, nome, quantidade))
                
                conexao.commit()
                memo_widget.insert(tk.END, "\nSUCESSO: Item cadastrado!")
                
                entry_codigo.delete(0, tk.END)
                entry_nome.delete(0, tk.END)
                entry_qntd.delete(0, tk.END)
            
    except Exception as e:
        if conexao: conexao.rollback()
        memo_widget.insert(tk.END, f"\nERRO NO BANCO: {e}")
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()
        memo_widget.config(state=tk.DISABLED)


# =============================================================================
# JANELA PRINCIPAL (AGORA É UM FRAME)
# =============================================================================
def abrir_janela_cadastro(parent):
    # Cria o Frame Principal
    frame_total = tk.Frame(parent, bg="white")
    frame_total.pack(fill="both", expand=True)

    # Título
    tk.Label(frame_total, text="Cadastro de Produtos", font=("Arial", 16, "bold"), bg="white", fg="#444").pack(pady=15)

    # Container para dividir a tela (Esquerda: Manual, Direita: CSV)
    container = tk.Frame(frame_total, bg="white")
    container.pack(fill="both", expand=True, padx=20, pady=10)

    # --- LADO ESQUERDO: CADASTRO MANUAL ---
    frame_manual = tk.Frame(container, bg="#f0f0f0", relief="groove", borderwidth=1)
    frame_manual.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)

    tk.Label(frame_manual, text="Cadastro Manual (Um Item)", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=15)

    # Código
    tk.Label(frame_manual, text="Código / Referência:", bg="#f0f0f0").pack(anchor="w", padx=20)
    entry_codigo = tk.Entry(frame_manual, width=30)
    entry_codigo.pack(fill="x", padx=20, pady=2)

    # Nome
    tk.Label(frame_manual, text="Nome do Item:", bg="#f0f0f0").pack(anchor="w", padx=20, pady=(10,0))
    entry_nome = tk.Entry(frame_manual, width=30)
    entry_nome.pack(fill="x", padx=20, pady=2)

    # Quantidade
    tk.Label(frame_manual, text="Quantidade Inicial:", bg="#f0f0f0").pack(anchor="w", padx=20, pady=(10,0))
    entry_qntd = tk.Entry(frame_manual, width=30)
    entry_qntd.pack(fill="x", padx=20, pady=2)

    # Botão Salvar
    tk.Button(frame_manual, text="Salvar Item", bg="#007bff", fg="white", font=("Arial", 10, "bold"),
              command=lambda: _cadastrar_manual_logic(log_text, entry_codigo, entry_nome, entry_qntd)).pack(pady=20, padx=20, fill="x")

    # --- LADO DIREITO: CADASTRO CSV E LOG ---
    frame_direita = tk.Frame(container, bg="white")
    frame_direita.pack(side=tk.RIGHT, fill="both", expand=True, padx=10, pady=10)

    # Bloco CSV
    frame_csv = tk.Frame(frame_direita, bg="#e8f5e9", relief="groove", borderwidth=1)
    frame_csv.pack(fill="x", pady=0)

    tk.Label(frame_csv, text="Importação em Massa (CSV)", font=("Arial", 12, "bold"), bg="#e8f5e9").pack(pady=10)
    tk.Button(frame_csv, text="📂 Selecionar Arquivo CSV", bg="#28a745", fg="white",
              command=lambda: _cadastrar_itens_logic(parent, log_text)).pack(pady=10, padx=20, fill="x")

    # Log
    tk.Label(frame_direita, text="Log de Operações:", bg="white", font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,0))
    
    log_scrollbar = tk.Scrollbar(frame_direita)
    log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    log_text = tk.Text(frame_direita, height=15, width=40, yscrollcommand=log_scrollbar.set, font=("Consolas", 9))
    log_text.pack(side=tk.LEFT, fill="both", expand=True)
    log_scrollbar.config(command=log_text.yview)
    
    log_text.insert(tk.END, "Aguarde uma operação...")
    log_text.config(state=tk.DISABLED)