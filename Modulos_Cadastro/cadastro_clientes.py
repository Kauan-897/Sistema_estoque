import tkinter as tk
from tkinter import messagebox
import banco

# =============================================================================
# LÓGICA HÍBRIDA: CADASTRAR (NOVO) OU ATUALIZAR (EXISTENTE)
# =============================================================================
def _salvar_cliente_logic(memo_widget, entry_id, entry_nome, entry_tel, entry_email):
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    
    # Pega os dados
    cliente_id = entry_id.get().strip() # Se tiver valor, é EDIÇÃO. Se vazio, é NOVO.
    nome = entry_nome.get().strip()
    telefone = entry_tel.get().strip()
    email = entry_email.get().strip()
    
    if not nome:
        memo_widget.insert(tk.END, "ERRO: O campo 'Nome' é obrigatório.")
        memo_widget.config(state=tk.DISABLED)
        return
        
    conexao = None
    try:
        conexao = banco.conectar()
        if not conexao:
             memo_widget.insert(tk.END, "ERRO: Sem conexão com MySQL.")
             return
        cursor = conexao.cursor()
        
        # --- CENÁRIO 1: EDIÇÃO (ATUALIZAR) ---
        if cliente_id:
            cursor.execute("""
                UPDATE clientes 
                SET nome = %s, telefone = %s, email = %s 
                WHERE id = %s
            """, (nome, telefone, email, cliente_id))
            
            conexao.commit()
            memo_widget.insert(tk.END, f"SUCESSO: Cliente '{nome}' atualizado!")
            messagebox.showinfo("Sucesso", "Dados do cliente atualizados.")

        # --- CENÁRIO 2: NOVO CADASTRO (INSERIR) ---
        else:
            # Verifica duplicidade apenas se for novo
            cursor.execute("SELECT id FROM clientes WHERE nome = %s", (nome,))
            if cursor.fetchone():
                memo_widget.insert(tk.END, f"ERRO: Já existe um cliente com o nome '{nome}'.")
                messagebox.showwarning("Duplicidade", f"O cliente '{nome}' já está cadastrado.")
            else:
                cursor.execute("""
                    INSERT INTO clientes (nome, telefone, email) 
                    VALUES (%s, %s, %s)
                """, (nome, telefone, email))
                
                conexao.commit()
                memo_widget.insert(tk.END, f"SUCESSO: Novo cliente cadastrado!")
                messagebox.showinfo("Sucesso", "Cliente cadastrado.")
                
                # Limpa campos apenas no cadastro novo para facilitar o próximo
                _limpar_campos(entry_id, entry_nome, entry_tel, entry_email)
            
    except Exception as e:
        if conexao: conexao.rollback()
        memo_widget.insert(tk.END, f"\nERRO TÉCNICO: {e}")
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()
        memo_widget.config(state=tk.DISABLED)

def _limpar_campos(entry_id, entry_nome, entry_tel, entry_email):
    """Limpa o formulário e libera para NOVO cadastro"""
    entry_id.config(state=tk.NORMAL)
    entry_id.delete(0, tk.END)
    entry_id.config(state=tk.DISABLED)
    
    entry_nome.delete(0, tk.END)
    entry_tel.delete(0, tk.END)
    entry_email.delete(0, tk.END)

# =============================================================================
# LÓGICA DE PESQUISA E SELEÇÃO
# =============================================================================
def _pesquisar_cliente_logic(entry_busca, listbox_resultados):
    termo = entry_busca.get().strip()
    listbox_resultados.delete(0, tk.END)
    
    conexao = banco.conectar()
    if not conexao: return
    cursor = conexao.cursor()
    
    try:
        sql = "SELECT id, nome, telefone, email FROM clientes WHERE nome LIKE %s ORDER BY nome ASC"
        cursor.execute(sql, (f"%{termo}%",))
        resultados = cursor.fetchall()
        
        if resultados:
            for row in resultados:
                listbox_resultados.insert(tk.END, f"[{row[0]}] {row[1]}")
        else:
            listbox_resultados.insert(tk.END, "Nenhum cliente encontrado.")
    finally:
        conexao.close()

def _selecionar_cliente_evento(event, listbox_resultados, entry_id, entry_nome, entry_tel, entry_email):
    selecao = listbox_resultados.curselection()
    if not selecao: return
    texto = listbox_resultados.get(selecao[0])
    if "Nenhum" in texto: return

    try:
        id_str = texto.split('] ', 1)[0].replace('[', '')
        cliente_id = int(id_str)
        
        conexao = banco.conectar()
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome, telefone, email FROM clientes WHERE id = %s", (cliente_id,))
        row = cursor.fetchone()
        conexao.close()
        
        if row:
            # Preenche o ID (Isso ativa o modo EDIÇÃO)
            entry_id.config(state=tk.NORMAL)
            entry_id.delete(0, tk.END)
            entry_id.insert(0, row[0])
            entry_id.config(state=tk.DISABLED)
            
            entry_nome.delete(0, tk.END); entry_nome.insert(0, row[1] if row[1] else "")
            entry_tel.delete(0, tk.END); entry_tel.insert(0, row[2] if row[2] else "")
            entry_email.delete(0, tk.END); entry_email.insert(0, row[3] if row[3] else "")
    except: pass 


# =============================================================================
# JANELA PRINCIPAL (FRAME EMBUTIDO)
# =============================================================================
def abrir_janela_cadastro_cliente(parent):
    # Frame Principal
    frame_total = tk.Frame(parent, bg="white")
    frame_total.pack(fill="both", expand=True)

    tk.Label(frame_total, text="Gerenciamento de Clientes", font=("Arial", 16, "bold"), bg="white", fg="#444").pack(pady=15)

    container = tk.Frame(frame_total, bg="white")
    container.pack(fill="both", expand=True, padx=20, pady=10)

    # Layout Dividido
    frame_esq = tk.Frame(container, bg="white")
    frame_esq.pack(side=tk.LEFT, fill="both", expand=True, padx=10)
    
    frame_dir = tk.Frame(container, bg="#f9f9f9", relief="groove", borderwidth=2)
    frame_dir.pack(side=tk.RIGHT, fill="y", padx=10, ipadx=10)

    # --- ESQUERDA: FORMULÁRIO ---
    form = tk.Frame(frame_esq, bg="#f0f0f0", relief="groove", borderwidth=1)
    form.pack(fill="x", pady=5, ipady=10)

    tk.Label(form, text="Dados do Cliente", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=10)

    # Campo ID (Novo e Importante para saber se é Edição)
    tk.Label(form, text="ID (Automático):", bg="#f0f0f0", fg="gray").pack(anchor="w", padx=20)
    entry_id = tk.Entry(form, width=10, bg="#e0e0e0")
    entry_id.pack(fill="x", padx=20, pady=2)
    entry_id.config(state=tk.DISABLED) # Bloqueado

    tk.Label(form, text="Nome do Cliente:", bg="#f0f0f0").pack(anchor="w", padx=20)
    entry_nome = tk.Entry(form, width=35)
    entry_nome.pack(fill="x", padx=20, pady=2)

    tk.Label(form, text="Telefone:", bg="#f0f0f0").pack(anchor="w", padx=20)
    entry_tel = tk.Entry(form, width=35)
    entry_tel.pack(fill="x", padx=20, pady=2)

    tk.Label(form, text="Email:", bg="#f0f0f0").pack(anchor="w", padx=20)
    entry_email = tk.Entry(form, width=35)
    entry_email.pack(fill="x", padx=20, pady=2)

    # Botões
    frame_botoes = tk.Frame(form, bg="#f0f0f0")
    frame_botoes.pack(fill="x", padx=20, pady=15)
    
    tk.Button(frame_botoes, text="💾 Salvar / Atualizar", bg="#007bff", fg="white", font=("Arial", 10, "bold"),
              command=lambda: _salvar_cliente_logic(log_text, entry_id, entry_nome, entry_tel, entry_email)).pack(side="left", fill="x", expand=True, padx=(0,5))
              
    tk.Button(frame_botoes, text="🧹 Novo / Limpar", bg="#ffcccc", fg="red", font=("Arial", 10),
              command=lambda: _limpar_campos(entry_id, entry_nome, entry_tel, entry_email)).pack(side="right", padx=(5,0))

    # Log
    frame_log = tk.Frame(frame_esq, bg="white")
    frame_log.pack(fill="both", expand=True, pady=10)
    tk.Label(frame_log, text="Log de Operações:", bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
    
    log_text = tk.Text(frame_log, height=8, font=("Consolas", 9))
    log_text.pack(fill="both", expand=True)
    log_text.config(state=tk.DISABLED)

    # --- DIREITA: PESQUISA ---
    tk.Label(frame_dir, text="🔍 Pesquisar Clientes", font=("Arial", 11, "bold"), bg="#f9f9f9").pack(pady=10)
    
    entry_busca = tk.Entry(frame_dir, font=("Arial", 11))
    entry_busca.pack(fill="x", padx=10, pady=5)
    
    # Lista Resultados
    frame_lista = tk.Frame(frame_dir)
    frame_lista.pack(fill="both", expand=True, padx=10, pady=5)
    
    scrollbar = tk.Scrollbar(frame_lista)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    listbox_resultados = tk.Listbox(frame_lista, width=35, height=20, yscrollcommand=scrollbar.set, font=("Consolas", 10))
    listbox_resultados.pack(side=tk.LEFT, fill="both", expand=True)
    scrollbar.config(command=listbox_resultados.yview)
    
    tk.Button(frame_dir, text="Pesquisar", bg="#e1f5fe",
              command=lambda: _pesquisar_cliente_logic(entry_busca, listbox_resultados)).pack(fill="x", padx=10, pady=10)
    
    # Bindings
    entry_busca.bind('<Return>', lambda e: _pesquisar_cliente_logic(entry_busca, listbox_resultados))
    
    # Ao clicar na lista, preenche o formulário e o ID (Ativando modo Edição)
    listbox_resultados.bind('<<ListboxSelect>>', 
                            lambda event: _selecionar_cliente_evento(event, listbox_resultados, entry_id, entry_nome, entry_tel, entry_email))

    # Carrega inicial
    _pesquisar_cliente_logic(entry_busca, listbox_resultados)