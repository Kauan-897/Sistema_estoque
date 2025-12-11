import tkinter as tk
from tkinter import messagebox, ttk # Importa ttk para o Combobox
import banco

# --- 1. FUNÇÃO: PESQUISAR (Preenche a lista) ---
def _pesquisar_logic(entry_busca, listbox):
    termo = entry_busca.get().strip()
    listbox.delete(0, tk.END)
    
    conexao = None
    cursor = None
    try:
        conexao = banco.conectar()
        if not conexao: return
        cursor = conexao.cursor()
        
        # Agora buscamos CODIGO e STATUS também
        sql = """
            SELECT id, codigo, nome, quantidade, status 
            FROM estoque 
            WHERE nome LIKE %s OR codigo LIKE %s 
            ORDER BY nome ASC
        """
        like = f"%{termo}%"
        cursor.execute(sql, (like, like))
        resultados = cursor.fetchall()
        
        if resultados:
            for row in resultados:
                # row[0]=id, [1]=cod, [2]=nome, [3]=qtd, [4]=status
                cod = row[1] if row[1] else "-"
                status_icon = "🟢" if row[4] == "Ativo" else "🔴"
                
                # Exemplo visual: [🟢] [COD] Nome (Qtd: 10) | ID:1
                display = f"[{status_icon}] [{cod}] {row[2]} (Qtd: {row[3]}) | ID:{row[0]}"
                listbox.insert(tk.END, display)
        else:
            listbox.insert(tk.END, "Nenhum produto encontrado.")
            
    except Exception as e:
        messagebox.showerror("Erro", f"Erro na pesquisa: {e}")
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()

# --- 2. FUNÇÃO: CARREGAR DADOS PARA EDIÇÃO ---
def _selecionar_item(event, listbox, entradas):
    sel = listbox.curselection()
    if not sel: return
    
    texto = listbox.get(sel[0])
    if "Nenhum produto" in texto: return

    try:
        # Pega o ID que está no final da string " | ID:123"
        id_str = texto.split('| ID:')[1].strip()
        id_produto = int(id_str)
        
        conexao = banco.conectar()
        cursor = conexao.cursor()
        cursor.execute("SELECT id, codigo, nome, quantidade, status FROM estoque WHERE id = %s", (id_produto,))
        row = cursor.fetchone()
        conexao.close()
        
        if row:
            # Preenche os campos da direita
            entradas['id'].config(state=tk.NORMAL)
            entradas['id'].delete(0, tk.END)
            entradas['id'].insert(0, row[0])
            entradas['id'].config(state=tk.DISABLED)
            
            entradas['codigo'].delete(0, tk.END)
            if row[1]: entradas['codigo'].insert(0, row[1])
            
            entradas['nome'].delete(0, tk.END)
            entradas['nome'].insert(0, row[2])
            
            entradas['qtd'].delete(0, tk.END)
            entradas['qtd'].insert(0, row[3])
            
            # Define o status no Combobox
            status_banco = row[4]
            if status_banco not in ["Ativo", "Inativo"]: status_banco = "Ativo"
            entradas['status'].set(status_banco)

    except Exception as e:
        print(f"Erro ao selecionar: {e}")

# --- 3. FUNÇÃO: SALVAR ALTERAÇÕES ---
def _salvar_edicao(entradas, listbox, entry_busca):
    id_produto = entradas['id'].get()
    if not id_produto: return 
    
    novo_cod = entradas['codigo'].get().strip()
    novo_nome = entradas['nome'].get().strip()
    nova_qtd = entradas['qtd'].get().strip().replace(',', '.')
    novo_status = entradas['status'].get()
    
    if not novo_nome:
        messagebox.showwarning("Aviso", "O nome não pode ficar vazio.")
        return

    conexao = None
    try:
        conexao = banco.conectar()
        cursor = conexao.cursor()
        
        cursor.execute("""
            UPDATE estoque 
            SET codigo=%s, nome=%s, quantidade=%s, status=%s
            WHERE id=%s
        """, (novo_cod, novo_nome, nova_qtd, novo_status, id_produto))
        
        conexao.commit()
        messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
        _pesquisar_logic(entry_busca, listbox)
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao atualizar: {e}")
    finally:
        if conexao: conexao.close()

# --- 4. FUNÇÃO: EXCLUIR ---
def _excluir_produto(entradas, listbox, entry_busca):
    id_produto = entradas['id'].get()
    nome = entradas['nome'].get()
    
    if not id_produto: return
    
    resposta = messagebox.askyesno("Confirmar", f"Tem certeza que deseja apagar '{nome}'?\n\nMelhor usar o Status 'Inativo' se já tiver vendas.")
    
    if resposta:
        conexao = None
        try:
            conexao = banco.conectar()
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM estoque WHERE id=%s", (id_produto,))
            conexao.commit()
            messagebox.showinfo("Sucesso", "Produto apagado.")
            
            # Limpa campos
            entradas['id'].config(state=tk.NORMAL); entradas['id'].delete(0, tk.END); entradas['id'].config(state=tk.DISABLED)
            entradas['nome'].delete(0, tk.END)
            entradas['codigo'].delete(0, tk.END)
            entradas['qtd'].delete(0, tk.END)
            
            _pesquisar_logic(entry_busca, listbox)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível apagar:\n{e}")
        finally:
            if conexao: conexao.close()


# --- 5. JANELA PRINCIPAL ---
def abrir_janela_consulta(parent):
    # Em vez de Toplevel, usamos Frame
    frame_principal = tk.Frame(parent, bg="white")
    frame_principal.pack(fill="both", expand=True)

    tk.Label(frame_principal, text="Gerenciamento de Estoque", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

    # Layout: Esquerda (Lista) | Direita (Edição)
    frame_esq = tk.Frame(frame_principal, bg="white")
    frame_esq.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)
    
    frame_dir = tk.Frame(frame_principal, bg="white", relief="groove", borderwidth=2)
    frame_dir.pack(side=tk.RIGHT, fill="y", padx=10, pady=10)

    # === LADO ESQUERDO: LISTA ===
    tk.Label(frame_esq, text="🔍 Pesquisar Produto", font=("Arial", 12, "bold"), bg="white").pack(pady=5)
    entry_busca = tk.Entry(frame_esq)
    entry_busca.pack(fill="x", padx=5)
    
    listbox = tk.Listbox(frame_esq, font=("Consolas", 10))
    listbox.pack(fill="both", expand=True, padx=5, pady=5)
    
    tk.Button(frame_esq, text="Pesquisar", command=lambda: _pesquisar_logic(entry_busca, listbox)).pack(fill="x", padx=5)
    entry_busca.bind('<Return>', lambda e: _pesquisar_logic(entry_busca, listbox))

    # === LADO DIREITO: EDIÇÃO ===
    # ... (O resto do código de layout é igual, só mude 'janela' por 'frame_dir' onde precisar) ...
    # IMPORTANTE: Remova o botão "Sair" ou "Fechar Janela", pois agora fica fixo.

    _pesquisar_logic(entry_busca, listbox)