import tkinter as tk
from tkinter import messagebox, ttk
import banco

def _pesquisar_logic(entry_busca, listbox):
    termo = entry_busca.get().strip()
    listbox.delete(0, tk.END)
    conexao = banco.conectar()
    if not conexao: return
    cursor = conexao.cursor()
    
    try:
        # SQL Atualizado
        sql = """
            SELECT id, codigo, nome, quantidade, status, estoque_minimo, preco_custo, preco_venda 
            FROM estoque 
            WHERE nome LIKE %s OR codigo LIKE %s 
            ORDER BY nome ASC
        """
        like = f"%{termo}%"
        cursor.execute(sql, (like, like))
        for row in cursor.fetchall():
            # row: 0=id, 1=cod, 2=nome, 3=qtd, 4=status, 5=min, 6=custo, 7=venda
            cod = row[1] if row[1] else "-"
            status_icon = "🟢" if row[4] == "Ativo" else "🔴"
            alerta = "⚠️" if row[3] < row[5] else ""
            
            display = f"[{status_icon}{alerta}] {row[2]} (Qtd: {row[3]}) | ID:{row[0]}"
            listbox.insert(tk.END, display)
    finally:
        conexao.close()

def _selecionar_item(event, listbox, entradas):
    sel = listbox.curselection()
    if not sel: return
    texto = listbox.get(sel[0])
    if "Nenhum" in texto: return

    try:
        id_produto = int(texto.split('| ID:')[1].strip())
        conexao = banco.conectar()
        cursor = conexao.cursor()
        cursor.execute("SELECT id, codigo, nome, quantidade, status, estoque_minimo, preco_custo, preco_venda FROM estoque WHERE id = %s", (id_produto,))
        row = cursor.fetchone()
        conexao.close()
        
        if row:
            # Preenche tudo
            entradas['id'].config(state=tk.NORMAL); entradas['id'].delete(0, tk.END); entradas['id'].insert(0, row[0]); entradas['id'].config(state=tk.DISABLED)
            entradas['codigo'].delete(0, tk.END); entradas['codigo'].insert(0, row[1] if row[1] else "")
            entradas['nome'].delete(0, tk.END); entradas['nome'].insert(0, row[2])
            entradas['qtd'].delete(0, tk.END); entradas['qtd'].insert(0, row[3])
            entradas['min'].delete(0, tk.END); entradas['min'].insert(0, row[5])
            entradas['custo'].delete(0, tk.END); entradas['custo'].insert(0, row[6]) # Custo
            entradas['venda'].delete(0, tk.END); entradas['venda'].insert(0, row[7]) # Venda
            entradas['status'].set(row[4])

    except Exception as e:
        print(f"Erro: {e}")

def _salvar_edicao(entradas, listbox, entry_busca):
    id_prod = entradas['id'].get()
    if not id_prod: return 
    
    try:
        n_cod = entradas['codigo'].get().strip()
        n_nome = entradas['nome'].get().strip()
        n_qtd = float(entradas['qtd'].get().replace(',', '.'))
        n_min = int(entradas['min'].get())
        n_custo = float(entradas['custo'].get().replace(',', '.'))
        n_venda = float(entradas['venda'].get().replace(',', '.'))
        n_stat = entradas['status'].get()
        
        conexao = banco.conectar()
        cursor = conexao.cursor()
        
        cursor.execute("""
            UPDATE estoque 
            SET codigo=%s, nome=%s, quantidade=%s, status=%s, estoque_minimo=%s, preco_custo=%s, preco_venda=%s
            WHERE id=%s
        """, (n_cod, n_nome, n_qtd, n_stat, n_min, n_custo, n_venda, id_prod))
        
        conexao.commit()
        messagebox.showinfo("Sucesso", "Produto atualizado!")
        _pesquisar_logic(entry_busca, listbox)
        
    except ValueError:
        messagebox.showerror("Erro", "Verifique se os números (Qtd, Preços) estão corretos.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro no banco: {e}")
    finally:
        if conexao: conexao.close()

def _excluir_produto(entradas, listbox, entry_busca):
    # (Mantido igual, sem alterações necessárias)
    id_produto = entradas['id'].get()
    if not id_produto: return
    if messagebox.askyesno("Confirmar", "Tem certeza que deseja apagar?"):
        try:
            con = banco.conectar()
            cur = con.cursor()
            cur.execute("DELETE FROM estoque WHERE id=%s", (id_produto,))
            con.commit()
            messagebox.showinfo("Sucesso", "Apagado.")
            _pesquisar_logic(entry_busca, listbox)
            # Limpar campos... (simplificado)
        except Exception as e:
            messagebox.showerror("Erro", f"{e}")
        finally: con.close()

def abrir_janela_consulta(parent):
    frame_total = tk.Frame(parent, bg="white")
    frame_total.pack(fill="both", expand=True)
    
    tk.Label(frame_total, text="Gerenciamento e Preços", font=("Arial", 16, "bold"), bg="white", fg="#444").pack(pady=15)
    container = tk.Frame(frame_total, bg="white")
    container.pack(fill="both", expand=True, padx=20, pady=10)

    # Esquerda: Lista
    frame_esq = tk.Frame(container, bg="white")
    frame_esq.pack(side=tk.LEFT, fill="both", expand=True, padx=10)
    
    entry_busca = tk.Entry(frame_esq, font=("Arial", 11))
    entry_busca.pack(fill="x", pady=5)
    
    listbox = tk.Listbox(frame_esq, font=("Consolas", 10))
    listbox.pack(fill="both", expand=True)
    
    tk.Button(frame_esq, text="Pesquisar", command=lambda: _pesquisar_logic(entry_busca, listbox)).pack(fill="x", pady=5)
    entry_busca.bind('<Return>', lambda e: _pesquisar_logic(entry_busca, listbox))

    # Direita: Edição
    frame_dir = tk.Frame(container, bg="#f9f9f9", relief="groove", borderwidth=2)
    frame_dir.pack(side=tk.RIGHT, fill="y", padx=10, ipadx=10)
    
    entradas = {}
    
    tk.Label(frame_dir, text="Dados do Produto", font=("Arial", 12, "bold"), bg="#f9f9f9").pack(pady=10)
    
    # Grid simples
    frm_grid = tk.Frame(frame_dir, bg="#f9f9f9")
    frm_grid.pack()
    
    tk.Label(frm_grid, text="ID:", bg="#f9f9f9").grid(row=0, column=0, sticky='e'); 
    entradas['id'] = tk.Entry(frm_grid, bg="#eee", width=10); entradas['id'].grid(row=0, column=1, sticky='w')
    
    tk.Label(frm_grid, text="Código:", bg="#f9f9f9").grid(row=1, column=0, sticky='e'); 
    entradas['codigo'] = tk.Entry(frm_grid); entradas['codigo'].grid(row=1, column=1, sticky='w')
    
    tk.Label(frm_grid, text="Nome:", bg="#f9f9f9").grid(row=2, column=0, sticky='e'); 
    entradas['nome'] = tk.Entry(frm_grid); entradas['nome'].grid(row=2, column=1, sticky='w')
    
    tk.Label(frm_grid, text="Qtd:", bg="#f9f9f9").grid(row=3, column=0, sticky='e'); 
    entradas['qtd'] = tk.Entry(frm_grid); entradas['qtd'].grid(row=3, column=1, sticky='w')
    
    tk.Label(frm_grid, text="Mínimo:", bg="#f9f9f9").grid(row=4, column=0, sticky='e'); 
    entradas['min'] = tk.Entry(frm_grid); entradas['min'].grid(row=4, column=1, sticky='w')
    
    # NOVOS CAMPOS
    tk.Label(frm_grid, text="Custo (R$):", bg="#f9f9f9", fg="blue").grid(row=5, column=0, sticky='e'); 
    entradas['custo'] = tk.Entry(frm_grid); entradas['custo'].grid(row=5, column=1, sticky='w')
    
    tk.Label(frm_grid, text="Venda (R$):", bg="#f9f9f9", fg="green").grid(row=6, column=0, sticky='e'); 
    entradas['venda'] = tk.Entry(frm_grid); entradas['venda'].grid(row=6, column=1, sticky='w')
    
    tk.Label(frm_grid, text="Status:", bg="#f9f9f9").grid(row=7, column=0, sticky='e'); 
    entradas['status'] = ttk.Combobox(frm_grid, values=["Ativo", "Inativo"], state="readonly")
    entradas['status'].grid(row=7, column=1, sticky='w')

    tk.Button(frame_dir, text="💾 Salvar Alterações", bg="#ccffcc", fg="green",
              command=lambda: _salvar_edicao(entradas, listbox, entry_busca)).pack(fill="x", padx=20, pady=20)
              
    tk.Button(frame_dir, text="🗑️ Excluir", bg="#ffcccc", fg="red",
              command=lambda: _excluir_produto(entradas, listbox, entry_busca)).pack(fill="x", padx=20)

    listbox.bind('<<ListboxSelect>>', lambda e: _selecionar_item(e, listbox, entradas))
    _pesquisar_logic(entry_busca, listbox)