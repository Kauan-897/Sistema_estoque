import tkinter as tk
from tkinter import ttk, messagebox
import banco

# =============================================================================
# LÓGICA HÍBRIDA: CRIAR OU ATUALIZAR
# =============================================================================
def _salvar_usuario(entry_id, entry_nome, entry_user, entry_pass, cmb_nivel, tree):
    id_user = entry_id.get().strip()
    nome = entry_nome.get().strip()
    user = entry_user.get().strip()
    password = entry_pass.get().strip()
    nivel = cmb_nivel.get()
    
    if not nome or not user or not password or not nivel:
        messagebox.showwarning("Aviso", "Preencha todos os campos (Nome, Login, Senha e Nível).")
        return

    conexao = banco.conectar()
    if not conexao: return
    cursor = conexao.cursor()
    
    try:
        # --- CENÁRIO 1: ATUALIZAÇÃO (UPDATE) ---
        if id_user:
            # Verifica se o NOVO login já existe em OUTRO usuário (para não duplicar)
            cursor.execute("SELECT id FROM usuarios WHERE username = %s AND id != %s", (user, id_user))
            if cursor.fetchone():
                messagebox.showerror("Erro", f"O login '{user}' já está a ser usado por outra pessoa.")
                return

            cursor.execute("""
                UPDATE usuarios 
                SET nome = %s, username = %s, password_hash = %s, nivel = %s 
                WHERE id = %s
            """, (nome, user, password, nivel, id_user))
            
            conexao.commit()
            messagebox.showinfo("Sucesso", f"Dados de '{nome}' atualizados!")
            _limpar_campos(entry_id, entry_nome, entry_user, entry_pass, cmb_nivel)

        # --- CENÁRIO 2: NOVO USUÁRIO (INSERT) ---
        else:
            # Verifica se LOGIN já existe
            cursor.execute("SELECT id FROM usuarios WHERE username = %s", (user,))
            if cursor.fetchone():
                messagebox.showerror("Erro", f"O login '{user}' já existe.")
                return

            cursor.execute("""
                INSERT INTO usuarios (nome, username, password_hash, nivel) 
                VALUES (%s, %s, %s, %s)
            """, (nome, user, password, nivel))
            
            conexao.commit()
            messagebox.showinfo("Sucesso", f"Usuário '{nome}' criado!")
            _limpar_campos(entry_id, entry_nome, entry_user, entry_pass, cmb_nivel)

        _listar_usuarios(tree)

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    finally:
        conexao.close()

def _limpar_campos(entry_id, entry_nome, entry_user, entry_pass, cmb_nivel):
    entry_id.config(state=tk.NORMAL)
    entry_id.delete(0, tk.END)
    entry_id.config(state=tk.DISABLED)
    
    entry_nome.delete(0, tk.END)
    entry_user.delete(0, tk.END)
    entry_pass.delete(0, tk.END)
    cmb_nivel.set("vendedor")

# =============================================================================
# LÓGICA DE LISTAGEM E SELEÇÃO
# =============================================================================
def _listar_usuarios(tree):
    for i in tree.get_children(): tree.delete(i)
    
    conexao = banco.conectar()
    if not conexao: return
    cursor = conexao.cursor()
    
    cursor.execute("SELECT id, nome, username, nivel, password_hash FROM usuarios ORDER BY nome")
    for row in cursor.fetchall():
        # row: 0=id, 1=nome, 2=user, 3=nivel, 4=senha
        nome_display = row[1] if row[1] else "--- (Sem Nome)"
        # Guardamos a senha oculta no treeview para poder preencher ao editar
        tree.insert("", tk.END, values=(row[0], nome_display, row[2], row[3], row[4]))
    
    conexao.close()

def _selecionar_usuario(event, tree, entry_id, entry_nome, entry_user, entry_pass, cmb_nivel):
    sel = tree.selection()
    if not sel: return
    
    # Pega dados da linha
    item = tree.item(sel[0])
    dados = item['values'] 
    # values: 0=id, 1=nome, 2=user, 3=nivel, 4=senha
    
    # Preenche ID (Ativa modo Edição)
    entry_id.config(state=tk.NORMAL)
    entry_id.delete(0, tk.END)
    entry_id.insert(0, dados[0])
    entry_id.config(state=tk.DISABLED)
    
    # Preenche Nome (se for "---", limpa)
    entry_nome.delete(0, tk.END)
    if dados[1] != "--- (Sem Nome)":
        entry_nome.insert(0, dados[1])
        
    # Preenche Login
    entry_user.delete(0, tk.END)
    entry_user.insert(0, str(dados[2]))
    
    # Preenche Nível
    cmb_nivel.set(dados[3])
    
    # Preenche Senha (Opcional: trazer a senha atual para o campo)
    entry_pass.delete(0, tk.END)
    entry_pass.insert(0, str(dados[4])) # Traz a senha atual

def _excluir_usuario(tree, entry_id, entry_nome, entry_user, entry_pass, cmb_nivel):
    sel = tree.selection()
    if not sel: return
    
    dados = tree.item(sel[0])['values']
    id_user = dados[0]
    username = str(dados[2])
    
    if username == 'admin':
        messagebox.showwarning("Proibido", "Não é possível excluir o usuário 'admin' padrão.")
        return

    if messagebox.askyesno("Confirmar", f"Tem certeza que deseja remover o acesso de '{username}'?"):
        conexao = banco.conectar()
        cursor = conexao.cursor()
        try:
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (id_user,))
            conexao.commit()
            messagebox.showinfo("Sucesso", "Usuário removido.")
            _listar_usuarios(tree)
            _limpar_campos(entry_id, entry_nome, entry_user, entry_pass, cmb_nivel)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir: {e}")
        finally:
            conexao.close()

# =============================================================================
# JANELA PRINCIPAL (EMBUTIDA)
# =============================================================================
def abrir_admin_usuarios(parent):
    # Frame Principal
    frame_total = tk.Frame(parent, bg="white")
    frame_total.pack(fill="both", expand=True)

    tk.Label(frame_total, text="Controle de Acesso (Admin)", font=("Arial", 16, "bold"), bg="white", fg="#444").pack(pady=15)

    container = tk.Frame(frame_total, bg="white")
    container.pack(fill="both", expand=True, padx=20, pady=10)

    # --- ESQUERDA: FORMULÁRIO ---
    frame_esq = tk.Frame(container, bg="#f0f0f0", relief="groove", borderwidth=1)
    frame_esq.pack(side=tk.LEFT, fill="both", expand=True, padx=10)

    tk.Label(frame_esq, text="Dados do Usuário", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=15)

    # ID (Escondido/Bloqueado)
    tk.Label(frame_esq, text="ID:", bg="#f0f0f0", fg="gray").pack(anchor="w", padx=20)
    entry_id = tk.Entry(frame_esq, bg="#e0e0e0", width=10)
    entry_id.pack(fill="x", padx=20, pady=2)
    entry_id.config(state=tk.DISABLED)

    # Nome
    tk.Label(frame_esq, text="Nome Completo:", bg="#f0f0f0").pack(anchor="w", padx=20)
    entry_nome = tk.Entry(frame_esq)
    entry_nome.pack(fill="x", padx=20, pady=2)

    # Login
    tk.Label(frame_esq, text="Login (Usuário):", bg="#f0f0f0").pack(anchor="w", padx=20, pady=(10,0))
    entry_user = tk.Entry(frame_esq)
    entry_user.pack(fill="x", padx=20, pady=2)

    # Senha
    tk.Label(frame_esq, text="Senha:", bg="#f0f0f0").pack(anchor="w", padx=20, pady=(10,0))
    entry_pass = tk.Entry(frame_esq) # Removi o show="*" para o admin poder ver e editar a senha
    entry_pass.pack(fill="x", padx=20, pady=2)

    # Nível
    tk.Label(frame_esq, text="Nível de Acesso:", bg="#f0f0f0").pack(anchor="w", padx=20, pady=(10,0))
    cmb_nivel = ttk.Combobox(frame_esq, values=["admin", "vendedor", "estoquista"], state="readonly")
    cmb_nivel.set("vendedor")
    cmb_nivel.pack(fill="x", padx=20, pady=2)

    # Botões
    frame_btns = tk.Frame(frame_esq, bg="#f0f0f0")
    frame_btns.pack(fill="x", padx=20, pady=20)

    tk.Button(frame_btns, text="💾 Salvar / Atualizar", bg="#007bff", fg="white", font=("Arial", 10, "bold"),
              command=lambda: _salvar_usuario(entry_id, entry_nome, entry_user, entry_pass, cmb_nivel, tree)).pack(side="left", fill="x", expand=True, padx=(0,5))
    
    tk.Button(frame_btns, text="🧹 Limpar", bg="white", fg="black",
              command=lambda: _limpar_campos(entry_id, entry_nome, entry_user, entry_pass, cmb_nivel)).pack(side="right", padx=(5,0))

    # --- DIREITA: LISTA ---
    frame_dir = tk.Frame(container, bg="white")
    frame_dir.pack(side=tk.RIGHT, fill="both", expand=True, padx=10)

    tk.Label(frame_dir, text="Usuários do Sistema", font=("Arial", 11, "bold"), bg="white").pack(pady=5)

    # Colunas (Senha fica oculta visualmente, mas acessível no código)
    cols = ("ID", "Nome", "Login", "Nível", "SenhaOculta")
    tree = ttk.Treeview(frame_dir, columns=cols, show="headings", height=10)
    
    tree.heading("ID", text="ID"); tree.column("ID", width=30, anchor="center")
    tree.heading("Nome", text="Nome"); tree.column("Nome", width=200)
    tree.heading("Login", text="Login"); tree.column("Login", width=120)
    tree.heading("Nível", text="Permissão"); tree.column("Nível", width=100, anchor="center")
    
    # Esconde coluna senha
    tree.column("SenhaOculta", width=0, stretch=tk.NO) 
    
    tree.pack(fill="both", expand=True)

    tk.Button(frame_dir, text="🗑️ Remover Usuário Selecionado", bg="#ffcccc", fg="red",
              command=lambda: _excluir_usuario(tree, entry_id, entry_nome, entry_user, entry_pass, cmb_nivel)).pack(pady=10, fill="x")

    # Evento de Clique
    tree.bind('<<TreeviewSelect>>', 
              lambda e: _selecionar_usuario(e, tree, entry_id, entry_nome, entry_user, entry_pass, cmb_nivel))

    _listar_usuarios(tree)