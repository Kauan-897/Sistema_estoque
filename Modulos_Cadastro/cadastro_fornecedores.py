import tkinter as tk
from tkinter import messagebox
import banco

# --- 1. LÓGICA DE CADASTRO ---
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

# --- 2. LÓGICA DE PESQUISA ---
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
                # [ID] Nome (Contato: ...)
                contato_info = f" ({row[2]})" if row[2] else ""
                listbox.insert(tk.END, f"[{row[0]}] {row[1]}{contato_info}")
        else:
            listbox.insert(tk.END, "Nenhum fornecedor encontrado.")
    finally:
        conexao.close()

# --- 3. LÓGICA DE SELEÇÃO ---
def _selecionar_fornecedor(event, listbox, entry_nome, entry_contato):
    sel = listbox.curselection()
    if not sel: return
    texto = listbox.get(sel[0])
    if "Nenhum" in texto: return

    try:
        # Extrai ID do texto "[ID] Nome"
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

# --- 4. JANELA PRINCIPAL ---
def abrir_janela_fornecedores(janela_raiz):
    janela = tk.Toplevel(janela_raiz)
    janela.title("Gerenciamento de Fornecedores")
    janela.geometry("850x450")
    janela.transient(janela_raiz)
    janela.grab_set()

    # Layout Dividido
    frame_esq = tk.Frame(janela)
    frame_esq.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)
    frame_dir = tk.Frame(janela, relief="sunken", borderwidth=1)
    frame_dir.pack(side=tk.RIGHT, fill="y", padx=10, pady=10)

    # --- ESQUERDA: CADASTRO ---
    form = tk.Frame(frame_esq, relief="groove", borderwidth=2)
    form.pack(fill="x", pady=5)
    
    tk.Label(form, text="Novo Fornecedor", font=("Arial", 12, "bold")).pack(pady=10)
    
    tk.Label(form, text="Nome da Empresa/Pessoa:").pack(anchor="w", padx=10)
    entry_nome = tk.Entry(form); entry_nome.pack(fill="x", padx=10, pady=2)
    
    tk.Label(form, text="Contato (Tel/Email):").pack(anchor="w", padx=10)
    entry_contato = tk.Entry(form); entry_contato.pack(fill="x", padx=10, pady=2)
    
    tk.Button(form, text="Salvar Fornecedor", fg="blue", font=("Arial", 10, "bold"),
              command=lambda: _cadastrar_fornecedor_logic(log_text, entry_nome, entry_contato)).pack(fill="x", padx=10, pady=15)

    # Log
    log_frame = tk.Frame(frame_esq)
    log_frame.pack(fill="both", expand=True, pady=5)
    tk.Label(log_frame, text="Log:").pack(anchor="w")
    log_text = tk.Text(log_frame, height=5)
    log_text.pack(fill="both", expand=True)
    log_text.config(state=tk.DISABLED)

    # --- DIREITA: PESQUISA ---
    tk.Label(frame_dir, text="🔍 Buscar Fornecedor", font=("Arial", 11, "bold")).pack(pady=5)
    entry_busca = tk.Entry(frame_dir)
    entry_busca.pack(fill="x", padx=5)
    
    listbox = tk.Listbox(frame_dir, width=35, height=20)
    listbox.pack(fill="both", expand=True, padx=5, pady=5)
    
    tk.Button(frame_dir, text="Pesquisar", command=lambda: _pesquisar_fornecedor(entry_busca, listbox)).pack(fill="x", padx=5)
    
    # Bindings
    entry_busca.bind('<Return>', lambda e: _pesquisar_fornecedor(entry_busca, listbox))
    listbox.bind('<<ListboxSelect>>', lambda e: _selecionar_fornecedor(e, listbox, entry_nome, entry_contato))

    tk.Button(janela, text="Fechar", command=janela.destroy).pack(side="bottom", fill="x", padx=10, pady=10)
    
    _pesquisar_fornecedor(entry_busca, listbox)
    janela.wait_window()