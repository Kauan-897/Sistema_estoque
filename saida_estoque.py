import tkinter as tk
from tkinter import messagebox
import banco

# --- 1. FUNÇÃO DE LÓGICA (INTERNA) ---
def _remover_stock_logic(memo_widget, entry_nome, entry_qntd, entry_cliente_id):
    """
    Pega os dados dos campos de entrada, valida e REMOVE do estoque,
    registando na tabela SAIDAS.
    """
    
    # 1. Limpa o memo e habilita
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    
    # 2. Pega os dados das caixas de texto
    nome = entry_nome.get().strip()
    qntd_str = entry_qntd.get().strip().replace(',', '.')
    cliente_id_str = entry_cliente_id.get().strip()
    
    # 3. Validação dos dados
    if not nome:
        memo_widget.insert(tk.END, "ERRO: O campo 'Nome' não pode estar vazio.")
        memo_widget.config(state=tk.DISABLED)
        return
        
    try:
        quantidade = float(qntd_str)
        if quantidade <= 0:
             raise ValueError("Quantidade deve ser positiva")
    except ValueError:
        memo_widget.insert(tk.END, f"ERRO: Quantidade inválida ('{qntd_str}').\nInsira um número positivo.")
        memo_widget.config(state=tk.DISABLED)
        return
        
    try:
        cliente_id = int(cliente_id_str)
    except ValueError:
        memo_widget.insert(tk.END, f"ERRO: ID do Cliente inválido ('{cliente_id_str}').\nInsira um número de ID.")
        memo_widget.config(state=tk.DISABLED)
        return

    # TODO: USUARIO ID (Quando tivermos login)
    # Por agora, vamos "fingir" que é o admin (ID 1)
    usuario_id_fixo = 1
    
    # 4. Lógica de Banco de Dados
    conexao = None
    cursor = None
    try:
        conexao = banco.conectar()
        if not conexao:
             memo_widget.insert(tk.END, "ERRO: Não foi possível conectar ao banco de dados MySQL.")
             memo_widget.config(state=tk.DISABLED)
             return
            
        cursor = conexao.cursor()
        
        # --- VALIDAÇÕES COMPLEXAS ---
        # A. O produto existe E tem stock suficiente?
        cursor.execute("SELECT id, quantidade FROM estoque WHERE nome = %s", (nome,))
        produto_existente = cursor.fetchone()
        
        if not produto_existente:
            memo_widget.insert(tk.END, f"ERRO: O item '{nome}' não foi encontrado no estoque.")
            raise Exception("Produto não encontrado") # Para o 'finally'

        estoque_id = produto_existente[0]
        stock_atual = produto_existente[1]

        if stock_atual < quantidade:
            memo_widget.insert(tk.END, f"ERRO: Stock insuficiente!\n")
            memo_widget.insert(tk.END, f"  Stock Atual: {stock_atual}\n")
            memo_widget.insert(tk.END, f"  Qtd. Pedida: {quantidade}")
            raise Exception("Stock insuficiente") # Para o 'finally'

        # B. O cliente existe?
        cursor.execute("SELECT id FROM clientes WHERE id = %s", (cliente_id,))
        cliente_existente = cursor.fetchone()
        
        if not cliente_existente:
            memo_widget.insert(tk.END, f"ERRO: Cliente com ID '{cliente_id}' não encontrado.\n")
            memo_widget.insert(tk.END, "Cadastre o cliente primeiro ou verifique o ID.")
            raise Exception("Cliente não encontrado") # Para o 'finally'

        # --- EXECUÇÃO (Se tudo estiver OK) ---
        memo_widget.insert(tk.END, f"Iniciando baixa de stock para o Cliente ID {cliente_id}...\n")
        
        # Passo 1: Remover do estoque
        novo_stock = stock_atual - quantidade
        cursor.execute("""
            UPDATE estoque 
            SET quantidade = %s 
            WHERE id = %s
        """, (novo_stock, estoque_id))
        
        # Passo 2: Registar na tabela SAIDAS
        cursor.execute("""
            INSERT INTO saidas (estoque_id, cliente_id, usuario_id, Quantidade) 
            VALUES (%s, %s, %s, %s)
        """, (estoque_id, cliente_id, usuario_id_fixo, quantidade))
        
        # Se chegámos aqui, tudo correu bem
        conexao.commit()
        memo_widget.insert(tk.END, f"\nSUCESSO!\n")
        memo_widget.insert(tk.END, f"  Produto: {nome}\n")
        memo_widget.insert(tk.END, f"  Novo Stock: {novo_stock}")
        
        # Limpa os campos de entrada
        entry_nome.delete(0, tk.END)
        entry_qntd.delete(0, tk.END)
        entry_cliente_id.delete(0, tk.END)
            
    except Exception as e:
        if conexao:
            conexao.rollback()
        # Não mostramos o erro no memo se já lá estiver uma mensagem
        if "ERRO:" not in memo_widget.get("1.0", tk.END):
            memo_widget.insert(tk.END, f"\n--- ERRO NA OPERAÇÃO ---\nOcorreu um erro: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
        memo_widget.config(state=tk.DISABLED)


# --- 2. FUNÇÃO PRINCIPAL (CRIA A JANELA) ---
def abrir_janela_saida(janela_raiz):
    
    janela_saida = tk.Toplevel(janela_raiz)
    janela_saida.title("Saída Manual de Estoque")
    janela_saida.geometry("550x500") # Um pouco mais alto
    
    janela_saida.transient(janela_raiz)
    janela_saida.grab_set()

    # --- Frame 1: Saída Manual (.grid()) ---
    frame_manual = tk.Frame(janela_saida, relief="groove", borderwidth=2)
    frame_manual.pack(fill="x", padx=15, pady=(15, 10))

    label_manual_titulo = tk.Label(frame_manual, text="Remover Quantidade (Saída)", font=("Arial", 12, "bold"))
    label_manual_titulo.grid(row=0, column=0, columnspan=2, pady=(5, 10))

    label_nome = tk.Label(frame_manual, text="Nome do Item Existente:")
    label_nome.grid(row=1, column=0, padx=10, pady=5, sticky="e")
    
    entry_nome = tk.Entry(frame_manual, width=40)
    entry_nome.grid(row=1, column=1, padx=5, pady=5)

    label_qntd = tk.Label(frame_manual, text="Quantidade a Remover:")
    label_qntd.grid(row=2, column=0, padx=10, pady=5, sticky="e")
    
    entry_qntd = tk.Entry(frame_manual, width=15)
    entry_qntd.grid(row=2, column=1, padx=5, pady=5, sticky="w") 

    # Novo campo para o Cliente
    label_cliente_id = tk.Label(frame_manual, text="ID do Cliente:")
    label_cliente_id.grid(row=3, column=0, padx=10, pady=5, sticky="e")
    
    entry_cliente_id = tk.Entry(frame_manual, width=15)
    entry_cliente_id.grid(row=3, column=1, padx=5, pady=5, sticky="w") 

    # Botão para remover
    btn_remover = tk.Button(frame_manual, text="Confirmar Saída do Estoque", fg="red",
                             command=lambda: _remover_stock_logic(log_text, entry_nome, entry_qntd, entry_cliente_id))
    btn_remover.grid(row=4, column=0, columnspan=2, padx=10, pady=10, ipady=5, sticky="ew")
    
    # --- Frame 2: Log (.pack()) ---
    frame_log = tk.Frame(janela_saida)
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

    # --- Botão Fechar ---
    btn_fechar = tk.Button(janela_saida, text="Fechar Janela", command=janela_saida.destroy)
    btn_fechar.pack(padx=15, pady=(0, 15), side="bottom", fill="x")

    janela_saida.wait_window()