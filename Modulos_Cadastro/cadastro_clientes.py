import tkinter as tk
from tkinter import messagebox
import banco # <-- O nosso módulo de conexão MySQL

# --- 1. FUNÇÃO DE LÓGICA (CADASTRAR) ---
def _cadastrar_cliente_logic(memo_widget, entry_nome, entry_tel, entry_email):
    """
    Pega os dados dos campos de entrada, valida e salva um NOVO cliente.
    """
    
    # 1. Limpa o memo e habilita
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    
    # 2. Pega os dados das caixas de texto
    nome = entry_nome.get().strip()
    telefone = entry_tel.get().strip()
    email = entry_email.get().strip()
    
    # 3. Validação (Apenas o nome é obrigatório)
    if not nome:
        memo_widget.insert(tk.END, "ERRO: O campo 'Nome' não pode estar vazio.")
        memo_widget.config(state=tk.DISABLED)
        return
        
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
        
        # Verifica se o cliente JÁ EXISTE (pelo nome)
        cursor.execute("SELECT id FROM clientes WHERE nome = %s", (nome,))
        cliente_existente = cursor.fetchone()
        
        if cliente_existente:
            memo_widget.insert(tk.END, f"ERRO: O cliente '{nome}' já está cadastrado.")
        else:
            memo_widget.insert(tk.END, f"Cadastrando novo cliente:\n  Nome: {nome}\n")
            if telefone: memo_widget.insert(tk.END, f"  Telefone: {telefone}\n")
            if email: memo_widget.insert(tk.END, f"  Email: {email}\n")
            
            cursor.execute("""
                INSERT INTO clientes (nome, telefone, email) 
                VALUES (%s, %s, %s)
            """, (nome, telefone, email))
            
            conexao.commit()
            memo_widget.insert(tk.END, f"\nSUCESSO: Novo cliente cadastrado!")
            
            # Limpa os campos
            entry_nome.delete(0, tk.END)
            entry_tel.delete(0, tk.END)
            entry_email.delete(0, tk.END)
            
    except Exception as e:
        if conexao: conexao.rollback()
        memo_widget.insert(tk.END, f"\n--- ERRO NO BANCO ---\nOcorreu um erro: {e}")
    
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()
        memo_widget.config(state=tk.DISABLED)

# --- 2. NOVA FUNÇÃO: PESQUISAR CLIENTES ---
def _pesquisar_cliente_logic(entry_busca, listbox_resultados):
    termo = entry_busca.get().strip()
    listbox_resultados.delete(0, tk.END) # Limpa a lista
    
    conexao = None
    cursor = None
    try:
        conexao = banco.conectar()
        if not conexao: return
        cursor = conexao.cursor()
        
        # Pesquisa por Nome (LIKE)
        sql = "SELECT id, nome, telefone, email FROM clientes WHERE nome LIKE %s ORDER BY nome ASC"
        termo_like = f"%{termo}%"
        cursor.execute(sql, (termo_like,))
        resultados = cursor.fetchall()
        
        if resultados:
            for row in resultados:
                # row[0]=id, row[1]=nome, row[2]=tel, row[3]=email
                # Formato visual na lista: [ID] Nome
                texto_display = f"[{row[0]}] {row[1]}"
                listbox_resultados.insert(tk.END, texto_display)
        else:
            listbox_resultados.insert(tk.END, "Nenhum cliente encontrado.")
            
    except Exception as e:
        messagebox.showerror("Erro", f"Erro na pesquisa: {e}")
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()

# --- 3. NOVA FUNÇÃO: SELECIONAR CLIENTE DA LISTA ---
def _selecionar_cliente_evento(event, listbox_resultados, entry_nome, entry_tel, entry_email):
    selecao = listbox_resultados.curselection()
    if not selecao: return
    
    texto = listbox_resultados.get(selecao[0])
    if texto == "Nenhum cliente encontrado.": return

    try:
        # O texto é "[ID] Nome". Vamos pegar o ID e buscar os dados completos no banco
        # (É mais seguro buscar no banco de novo para garantir que temos tel e email certos)
        id_str = texto.split('] ', 1)[0].replace('[', '')
        cliente_id = int(id_str)
        
        conexao = banco.conectar()
        cursor = conexao.cursor()
        cursor.execute("SELECT nome, telefone, email FROM clientes WHERE id = %s", (cliente_id,))
        resultado = cursor.fetchone()
        
        if resultado:
            nome, tel, email = resultado
            
            # Preenche os campos
            entry_nome.delete(0, tk.END)
            entry_nome.insert(0, nome if nome else "")
            
            entry_tel.delete(0, tk.END)
            entry_tel.insert(0, tel if tel else "")
            
            entry_email.delete(0, tk.END)
            entry_email.insert(0, email if email else "")
            
        cursor.close()
        conexao.close()

    except Exception:
        pass 

# --- 4. FUNÇÃO PRINCIPAL (CRIA A JANELA) ---
def abrir_janela_cadastro_cliente(janela_raiz):
    
    janela_cli = tk.Toplevel(janela_raiz)
    janela_cli.title("Gerenciamento de Clientes")
    janela_cli.geometry("900x500") # Janela mais larga
    
    janela_cli.transient(janela_raiz)
    janela_cli.grab_set()

    # === DIVISÃO DA TELA ===
    frame_esquerda = tk.Frame(janela_cli)
    frame_esquerda.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)
    
    frame_direita = tk.Frame(janela_cli, relief="sunken", borderwidth=1)
    frame_direita.pack(side=tk.RIGHT, fill="y", padx=10, pady=10)

    # --- LADO ESQUERDO: Formulário de Cadastro ---
    frame_manual = tk.Frame(frame_esquerda, relief="groove", borderwidth=2)
    frame_manual.pack(fill="x", padx=5, pady=5)

    label_titulo = tk.Label(frame_manual, text="Dados do Cliente", font=("Arial", 12, "bold"))
    label_titulo.pack(pady=10)

    # Nome
    tk.Label(frame_manual, text="Nome do Cliente:").pack(anchor="w", padx=10)
    entry_nome = tk.Entry(frame_manual, width=40)
    entry_nome.pack(fill="x", padx=10, pady=2)

    # Telefone
    tk.Label(frame_manual, text="Telefone:").pack(anchor="w", padx=10)
    entry_tel = tk.Entry(frame_manual, width=40)
    entry_tel.pack(fill="x", padx=10, pady=2)

    # Email
    tk.Label(frame_manual, text="Email:").pack(anchor="w", padx=10)
    entry_email = tk.Entry(frame_manual, width=40)
    entry_email.pack(fill="x", padx=10, pady=2)

    # Botão Salvar
    btn_salvar = tk.Button(frame_manual, text="Salvar Novo Cliente", fg="blue", font=("Arial", 10, "bold"),
                             command=lambda: _cadastrar_cliente_logic(log_text, entry_nome, entry_tel, entry_email))
    btn_salvar.pack(fill="x", padx=10, pady=15)
    btn_apagar = tk.Button(frame_manual, text="Apagar Campos", fg="red", font=("Arial", 10, "bold"),
                             command=lambda: (entry_nome.delete(0, tk.END), entry_tel.delete(0, tk.END), entry_email.delete(0, tk.END)))
    btn_apagar.pack(fill="x", padx=10, pady=(0,10))
    
    # Log / Memo
    frame_log = tk.Frame(frame_esquerda)
    frame_log.pack(fill="both", expand=True, padx=5, pady=10)
    tk.Label(frame_log, text="Log da Operação:").pack(anchor="w")
    
    log_scrollbar = tk.Scrollbar(frame_log)
    log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    log_text = tk.Text(frame_log, height=5, width=40, yscrollcommand=log_scrollbar.set)
    log_text.pack(side=tk.LEFT, fill="both", expand=True)
    log_scrollbar.config(command=log_text.yview)
    log_text.insert(tk.END, "Aguardando operação...")
    log_text.config(state=tk.DISABLED) 

    # --- LADO DIREITO: Pesquisa ---
    tk.Label(frame_direita, text="🔍 Pesquisar Clientes", font=("Arial", 11, "bold")).pack(pady=5)
    tk.Label(frame_direita, text="Digite o nome:").pack()
    
    entry_busca = tk.Entry(frame_direita)
    entry_busca.pack(fill="x", padx=5, pady=2)
    
    # Botão Pesquisar
    btn_pesquisar = tk.Button(frame_direita, text="Pesquisar", 
                              command=lambda: _pesquisar_cliente_logic(entry_busca, listbox_resultados))
    btn_pesquisar.pack(fill="x", padx=5, pady=5)
    
    # Enter para pesquisar
    entry_busca.bind('<Return>', lambda event: _pesquisar_cliente_logic(entry_busca, listbox_resultados))

    tk.Label(frame_direita, text="Resultados:").pack(anchor="w", padx=5)

    listbox_frame = tk.Frame(frame_direita)
    listbox_frame.pack(fill="both", expand=True, padx=5, pady=5)
    scrollbar_lista = tk.Scrollbar(listbox_frame)
    scrollbar_lista.pack(side=tk.RIGHT, fill=tk.Y)
    listbox_resultados = tk.Listbox(listbox_frame, width=30, height=20, yscrollcommand=scrollbar_lista.set)
    listbox_resultados.pack(side=tk.LEFT, fill="both", expand=True)
    scrollbar_lista.config(command=listbox_resultados.yview)
    
    # Evento de clique na lista (Preencher formulário)
    listbox_resultados.bind('<<ListboxSelect>>', 
                            lambda event: _selecionar_cliente_evento(event, listbox_resultados, entry_nome, entry_tel, entry_email))

    # Botão Fechar
    btn_fechar = tk.Button(janela_cli, text="Fechar Janela", command=janela_cli.destroy)
    btn_fechar.pack(side="bottom", fill="x", padx=10, pady=10)
    
    # Carrega a lista inicial
    _pesquisar_cliente_logic(entry_busca, listbox_resultados)

    janela_cli.wait_window()