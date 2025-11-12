import tkinter as tk
from tkinter import messagebox
import banco  

# --- 1. FUNÇÃO DE LÓGICA (INTERNA) ---
# Esta é a função que faz o trabalho
def _adicionar_stock_logic(memo_widget, entry_nome, entry_qntd):
    """
    Pega os dados dos campos de entrada, valida e ADICIONA ao estoque.
    Reporta tudo no 'memo_widget'.
    """
    
    # 1. Limpa o memo e habilita
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    
    # 2. Pega os dados das caixas de texto
    nome = entry_nome.get().strip()
    qntd_str = entry_qntd.get().strip().replace(',', '.') # Troca vírgula por ponto
    
    # 3. Validação dos dados
    if not nome:
        memo_widget.insert(tk.END, "ERRO: O campo 'Nome' não pode estar vazio.")
        memo_widget.config(state=tk.DISABLED)
        return
        
    try:
        # Tenta converter a quantidade para um número
        quantidade = float(qntd_str)
        if quantidade <= 0:
             raise ValueError("Quantidade deve ser positiva")
    except ValueError:
        memo_widget.insert(tk.END, f"ERRO: Quantidade inválida ('{qntd_str}').\nInsira um número positivo.")
        memo_widget.config(state=tk.DISABLED)
        return
    
    # 4. Lógica de Banco de Dados
    conexao = None
    cursor = None # <--- MUDANÇA 2: Definir cursor
    try:
        # --- MUDANÇA 3: Conexão com MySQL ---
        conexao = banco.conectar()
        if not conexao:
             memo_widget.insert(tk.END, "ERRO: Não foi possível conectar ao banco de dados MySQL.")
             memo_widget.config(state=tk.DISABLED)
             return
        # ------------------------------------
            
        cursor = conexao.cursor()
        
        # --- MUDANÇA 4: Placeholder '?' para '%s' ---
        cursor.execute("SELECT id, quantidade FROM estoque WHERE nome = %s", (nome,))
        produto_existente = cursor.fetchone()
        
        if not produto_existente:
            # Se NÃO existe, avisa o usuário
            memo_widget.insert(tk.END, f"ERRO: O item '{nome}' não foi encontrado no estoque.\n\n")
            memo_widget.insert(tk.END, "Cadastre este item primeiro (na tela 'Cadastrar') antes de dar entrada.")
        else:
            # Se EXISTE, faz o UPDATE
            stock_antigo = produto_existente[1]
            stock_novo = stock_antigo + quantidade
            
            memo_widget.insert(tk.END, f"Atualizando item:\n  Nome: {nome}\n")
            memo_widget.insert(tk.END, f"  Stock Antigo: {stock_antigo}\n")
            memo_widget.insert(tk.END, f"  Qtd. Adicionada: {quantidade}\n")
            
            # --- MUDANÇA 4: Placeholder '?' para '%s' ---
            cursor.execute("""
                UPDATE estoque 
                SET quantidade = quantidade + %s 
                WHERE nome = %s
            """, (quantidade, nome))
            # ---------------------------
            
            conexao.commit()
            memo_widget.insert(tk.END, f"\nSUCESSO: Novo stock é {stock_novo}!")
            
            # Limpa os campos de entrada após o sucesso
            entry_nome.delete(0, tk.END)
            entry_qntd.delete(0, tk.END)
            
    except Exception as e:
        if conexao:
            conexao.rollback()
        memo_widget.insert(tk.END, f"\n--- ERRO NO BANCO ---\nOcorreu um erro: {e}")
    
    finally:
        # --- MUDANÇA 5: Fechar manualmente ---
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
        memo_widget.config(state=tk.DISABLED)


# --- 2. FUNÇÃO PRINCIPAL (CRIA A JANELA) ---
# (Nenhuma mudança necessária aqui, a interface está perfeita)
def abrir_janela_entrada(janela_raiz):
    
    # Cria a janela "filha" (Toplevel)
    janela_entrada = tk.Toplevel(janela_raiz)
    janela_entrada.title("Entrada Manual de Estoque")
    janela_entrada.geometry("550x450")
    
    janela_entrada.transient(janela_raiz)
    janela_entrada.grab_set()

    # --- Frame 1: Entrada Manual (usará .grid() por dentro) ---
    frame_manual = tk.Frame(janela_entrada, relief="groove", borderwidth=2)
    frame_manual.pack(fill="x", padx=15, pady=(15, 10))

    label_manual_titulo = tk.Label(frame_manual, text="Adicionar Quantidade", font=("Arial", 12, "bold"))
    label_manual_titulo.grid(row=0, column=0, columnspan=3, pady=(5, 10))

    label_nome = tk.Label(frame_manual, text="Nome do Item Existente:")
    label_nome.grid(row=1, column=0, padx=10, pady=5, sticky="e")
    
    entry_nome = tk.Entry(frame_manual, width=40)
    entry_nome.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

    label_qntd = tk.Label(frame_manual, text="Quantidade a Adicionar:")
    label_qntd.grid(row=2, column=0, padx=10, pady=5, sticky="e")
    
    entry_qntd = tk.Entry(frame_manual, width=15)
    entry_qntd.grid(row=2, column=1, padx=5, pady=5, sticky="w") 

    # Botão para adicionar
    btn_adicionar = tk.Button(frame_manual, text="Adicionar ao Estoque", fg="green",
                             command=lambda: _adicionar_stock_logic(log_text, entry_nome, entry_qntd))
    btn_adicionar.grid(row=3, column=0, columnspan=3, padx=10, pady=10, ipady=5, sticky="ew")
    
    # --- Frame 2: Log (usará .pack() por dentro) ---
    frame_log = tk.Frame(janela_entrada)
    frame_log.pack(fill="both", expand=True, padx=15, pady=10)
    
    log_label = tk.Label(frame_log, text="Log da Operação:")
    log_label.pack(anchor="w")
    
    log_frame_interno = tk.Frame(frame_log)
    log_frame_interno.pack(fill="both", expand=True)
    
    log_scrollbar = tk.Scrollbar(log_frame_interno)
    log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    log_text = tk.Text(log_frame_interno, height=10, width=60, yscrollcommand=log_scrollbar.set)
    log_text.pack(side=tk.LEFT, fill="both", expand=True)
    log_scrollbar.config(command=log_text.yview)
    
    log_text.insert(tk.END, "Aguardando operação...")
    log_text.config(state=tk.DISABLED) 

    # --- Botão Fechar (fica fora dos frames) ---
    btn_fechar = tk.Button(janela_entrada, text="Fechar Janela", command=janela_entrada.destroy)
    btn_fechar.pack(padx=15, pady=(0, 15), side="bottom", fill="x")

    janela_entrada.wait_window()