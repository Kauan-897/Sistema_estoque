import tkinter as tk
from tkinter import messagebox
import banco

# =============================================================================
# LÓGICA DE NEGÓCIO (Mantida igual, apenas copiada)
# =============================================================================

def _cadastrar_fornecedor_logic(memo_widget, entry_nome, entry_contato):
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    
    nome = entry_nome.get().strip()
    contato = entry_contato.get().strip()
    
    if not nome:
        memo_widget.insert(tk.END, "ERRO: O campo 'Nome' é obrigatório.")
        memo_widget.config(state=tk.DISABLED)
        return
        
    conexao = None
    try:
        conexao = banco.conectar()
        if not conexao: return
        cursor = conexao.cursor()
        
        # Verifica duplicidade
        cursor.execute("SELECT id FROM fornecedores WHERE nome = %s", (nome,))
        if cursor.fetchone():
            memo_widget.insert(tk.END, f"ERRO: Fornecedor '{nome}' já existe.")
        else:
            cursor.execute("INSERT INTO fornecedores (nome, contato) VALUES (%s, %s)", (nome, contato))
            conexao.commit()
            memo_widget.insert(tk.END, f"\nSUCESSO: Fornecedor cadastrado!")
            
            entry_nome.delete(0, tk.END)
            entry_contato.delete(0, tk.END)
            
    except Exception as e:
        if conexao: conexao.rollback()
        memo_widget.insert(tk.END, f"\nERRO: {e}")
    finally:
        if conexao: conexao.close()
        memo_widget.config(state=tk.DISABLED)

def _pesquisar_fornecedor(entry_busca, listbox):
    termo = entry_busca.get().strip()
    listbox.delete(0, tk.END)
    
    conexao = banco.conectar()
    if not conexao: return
    cursor = conexao.cursor()
    
    try:
        sql = "SELECT id, nome, contato FROM fornecedores WHERE nome LIKE %s ORDER BY nome ASC"
        cursor.execute(sql, (f"%{termo}%",))
        resultados = cursor.fetchall()
        
        if resultados:
            for row in resultados:
                contato_info = f" ({row[2]})" if row[2] else ""
                listbox.insert(tk.END, f"[{row[0]}] {row[1]}{contato_info}")
        else:
            listbox.insert(tk.END, "Nenhum fornecedor encontrado.")
    finally:
        conexao.close()

def _selecionar_fornecedor(event, listbox, entry_nome, entry_contato):
    sel = listbox.curselection()
    if not sel: return
    texto = listbox.get(sel[0])
    if "Nenhum" in texto: return

    try:
        id_forn = texto.split('] ', 1)[0].replace('[', '')
        
        conexao = banco.conectar()
        cursor = conexao.cursor()
        cursor.execute("SELECT nome, contato FROM fornecedores WHERE id = %s", (id_forn,))
        row = cursor.fetchone()
        conexao.close()
        
        if row:
            entry_nome.delete(0, tk.END); entry_nome.insert(0, row[0])
            entry_contato.delete(0, tk.END); entry_contato.insert(0, row[1] if row[1] else "")
    except: pass


# =============================================================================
# JANELA PRINCIPAL (AGORA É UM FRAME)
# =============================================================================
def abrir_janela_fornecedores(parent):
    # Cria o Frame Principal
    frame_total = tk.Frame(parent, bg="white")
    frame_total.pack(fill="both", expand=True)

    # Título
    tk.Label(frame_total, text="Gerenciamento de Fornecedores", font=("Arial", 16, "bold"), bg="white", fg="#444").pack(pady=15)

    # Container
    container = tk.Frame(frame_total, bg="white")
    container.pack(fill="both", expand=True, padx=20, pady=10)

    # Layout Dividido
    frame_esq = tk.Frame(container, bg="white")
    frame_esq.pack(side=tk.LEFT, fill="both", expand=True, padx=10)
    
    frame_dir = tk.Frame(container, bg="#f9f9f9", relief="groove", borderwidth=2)
    frame_dir.pack(side=tk.RIGHT, fill="y", padx=10, ipadx=10)

    # --- ESQUERDA: CADASTRO ---
    form = tk.Frame(frame_esq, bg="#f0f0f0", relief="groove", borderwidth=1)
    form.pack(fill="x", pady=5, ipady=10)
    
    tk.Label(form, text="Novo Fornecedor", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=10)
    
    tk.Label(form, text="Nome da Empresa/Pessoa:", bg="#f0f0f0").pack(anchor="w", padx=20)
    entry_nome = tk.Entry(form, width=35)
    entry_nome.pack(fill="x", padx=20, pady=2)
    
    tk.Label(form, text="Contato (Tel/Email):", bg="#f0f0f0").pack(anchor="w", padx=20, pady=(10,0))
    entry_contato = tk.Entry(form, width=35)
    entry_contato.pack(fill="x", padx=20, pady=2)
    
    tk.Button(form, text="Salvar Fornecedor", bg="#007bff", fg="white", font=("Arial", 10, "bold"),
              command=lambda: _cadastrar_fornecedor_logic(log_text, entry_nome, entry_contato)).pack(fill="x", padx=20, pady=20)

    # Log
    frame_log = tk.Frame(frame_esq, bg="white")
    frame_log.pack(fill="both", expand=True, pady=10)
    tk.Label(frame_log, text="Log de Operações:", bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
    
    log_text = tk.Text(frame_log, height=8, font=("Consolas", 9))
    log_text.pack(fill="both", expand=True)
    log_text.config(state=tk.DISABLED)

    # --- DIREITA: PESQUISA ---
    tk.Label(frame_dir, text="🔍 Buscar Fornecedor", font=("Arial", 11, "bold"), bg="#f9f9f9").pack(pady=10)
    
    entry_busca = tk.Entry(frame_dir, font=("Arial", 11))
    entry_busca.pack(fill="x", padx=10, pady=5)
    
    # Lista Resultados
    frame_lista = tk.Frame(frame_dir)
    frame_lista.pack(fill="both", expand=True, padx=10, pady=5)
    
    scrollbar = tk.Scrollbar(frame_lista)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    listbox = tk.Listbox(frame_lista, width=35, height=20, yscrollcommand=scrollbar.set, font=("Consolas", 10))
    listbox.pack(side=tk.LEFT, fill="both", expand=True)
    scrollbar.config(command=listbox.yview)
    
    tk.Button(frame_dir, text="Pesquisar", bg="#e1f5fe",
              command=lambda: _pesquisar_fornecedor(entry_busca, listbox)).pack(fill="x", padx=10, pady=10)
    
    # Bindings
    entry_busca.bind('<Return>', lambda e: _pesquisar_fornecedor(entry_busca, listbox))
    listbox.bind('<<ListboxSelect>>', lambda e: _selecionar_fornecedor(e, listbox, entry_nome, entry_contato))

    # Carrega inicial
    _pesquisar_fornecedor(entry_busca, listbox)