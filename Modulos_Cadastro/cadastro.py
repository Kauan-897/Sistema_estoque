import tkinter as tk
from tkinter import filedialog, messagebox
import banco
import csv

# --- 2. FUNÇÃO DE LÓGICA (CADASTRO CSV - AGORA COM CÓDIGO) ---
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

        # Tenta ler com 'latin-1' (comum no Excel)
        with open(caminho_arquivo, "r", encoding="latin-1") as arquivo:
            leitor = csv.reader(arquivo, delimiter=';')
            
            # --- CORREÇÃO 1: Pular as DUAS linhas de cabeçalho ---
            next(leitor, None) # Pula linha 1: "Cliente;..."
            next(leitor, None) # Pula linha 2: "Item;Descritivo;..."
            
            memo_widget.insert(tk.END, "Lendo arquivo...\n-----------------\n")

            for linha in leitor:
                # Verifica se a linha tem dados suficientes
                if not linha or len(linha) < 2: 
                    continue
                
                # --- CORREÇÃO 2: Ignorar coluna 'Item' (pois ela repete números) ---
                # A coluna 0 é "Item" (1, 1, 2...), não é um código único confiável.
                # A coluna 1 é "Descritivo" (Nome do Produto).
                
                produto_codigo = None           # Vamos deixar o código vazio para não dar erro de duplicidade
                produto_nome = linha[1].strip() # Coluna 1 é o Nome
                
                # 1. Verifica se o NOME já existe
                cursor.execute("SELECT id FROM estoque WHERE nome = %s", (produto_nome,))
                if cursor.fetchone():
                    memo_widget.insert(tk.END, f" -> Ignorado: '{produto_nome}' (Nome já existe)\n")
                    itens_ignorados += 1
                    continue

                # 2. Insere o produto (Sem código, para garantir o cadastro)
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
        
# --- 3. FUNÇÃO: LÓGICA DO CADASTRO MANUAL ---
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
        
        # Verifica duplicidade de nome
        cursor.execute("SELECT id FROM estoque WHERE nome = %s", (nome,))
        if cursor.fetchone():
            memo_widget.insert(tk.END, f"ERRO: O item '{nome}' já existe.\n")
        else:
            # Verifica duplicidade de código
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


# --- 4. FUNÇÃO PRINCIPAL (JANELA) ---
def abrir_janela_cadastro(janela_raiz):
    
    janela_cad = tk.Toplevel(janela_raiz)
    janela_cad.title("Cadastrar Itens no Estoque")
    janela_cad.geometry("600x650")
    
    janela_cad.transient(janela_raiz)
    janela_cad.grab_set()

    # --- Frame 1: Cadastro Manual ---
    frame_manual = tk.Frame(janela_cad, relief="groove", borderwidth=2)
    frame_manual.pack(fill="x", padx=15, pady=(15, 10))

    label_manual_titulo = tk.Label(frame_manual, text="Cadastro Manual", font=("Arial", 12, "bold"))
    label_manual_titulo.grid(row=0, column=0, columnspan=2, pady=(5, 10))

    # Campo Código
    label_codigo = tk.Label(frame_manual, text="Código / Referência:")
    label_codigo.grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_codigo = tk.Entry(frame_manual, width=20)
    entry_codigo.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    # Campo Nome
    label_nome = tk.Label(frame_manual, text="Nome do Item:")
    label_nome.grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_nome = tk.Entry(frame_manual, width=40)
    entry_nome.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    # Campo Quantidade
    label_qntd = tk.Label(frame_manual, text="Quantidade Inicial:")
    label_qntd.grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_qntd = tk.Entry(frame_manual, width=15)
    entry_qntd.grid(row=3, column=1, padx=5, pady=5, sticky="w") 

    btn_cadastrar = tk.Button(frame_manual, text="Salvar Item Manual",
                             command=lambda: _cadastrar_manual_logic(log_text, entry_codigo, entry_nome, entry_qntd))
    btn_cadastrar.grid(row=4, column=0, columnspan=2, padx=10, pady=15, ipady=5, sticky="ew")
    
    # --- Frame 2: Cadastro CSV ---
    frame_csv = tk.Frame(janela_cad, relief="groove", borderwidth=2)
    frame_csv.pack(fill="both", expand=True, padx=15, pady=10)

    menu_label = tk.Label(frame_csv, text="Cadastro em Massa via CSV", font=("Arial", 12, "bold"))
    menu_label.pack(pady=(5, 10))
    
    log_frame = tk.Frame(frame_csv)
    log_scrollbar = tk.Scrollbar(log_frame)
    log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    log_text = tk.Text(log_frame, height=10, width=70, yscrollcommand=log_scrollbar.set)
    log_text.pack(side=tk.LEFT, fill="both", expand=True)
    log_scrollbar.config(command=log_text.yview)
    
    log_text.insert(tk.END, "Aguarde uma operação...")
    log_text.config(state=tk.DISABLED) 
    log_frame.pack(padx=10, pady=5, fill="both", expand=True)

    btn_csv = tk.Button(frame_csv, 
                        text="Selecionar CSV (Código; Nome; Qtd)", 
                        command=lambda: _cadastrar_itens_logic(janela_cad, log_text))
    btn_csv.pack(padx=40, pady=(10, 10), fill='x')

    btn_fechar = tk.Button(janela_cad, text="Fechar Janela", command=janela_cad.destroy)
    btn_fechar.pack(padx=15, pady=(0, 15), side="bottom", fill="x")

    janela_cad.wait_window()