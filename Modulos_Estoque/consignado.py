import tkinter as tk
from tkinter import ttk, messagebox
import banco

# =============================================================================
# LÓGICA DE NEGÓCIO (Mantida igual, apenas copiada)
# =============================================================================

def _registrar_chegada_logic(combobox_forn, entry_prod_nome, entry_qtd, entry_valor):
    try:
        nome_fornecedor = combobox_forn.get()
        nome_produto = entry_prod_nome.get().strip()
        qtd_str = entry_qtd.get().strip().replace(',', '.')
        valor_str = entry_valor.get().strip().replace(',', '.')

        if not nome_fornecedor or not nome_produto:
            messagebox.showwarning("Aviso", "Preencha Fornecedor e Produto.")
            return

        quantidade = float(qtd_str)
        valor = float(valor_str)

        conexao = banco.conectar()
        cursor = conexao.cursor()

        cursor.execute("SELECT id FROM fornecedores WHERE nome = %s", (nome_fornecedor,))
        res_forn = cursor.fetchone()
        if not res_forn:
            messagebox.showerror("Erro", "Fornecedor não encontrado.")
            return
        id_forn = res_forn[0]

        cursor.execute("SELECT id FROM estoque WHERE codigo = %s OR nome = %s", (nome_produto, nome_produto))
        res_prod = cursor.fetchone()
        
        if not res_prod:
            messagebox.showerror("Erro", f"Produto '{nome_produto}' não cadastrado no sistema.\nCadastre-o primeiro.")
            return
        id_prod = res_prod[0]

        cursor.execute("""
            INSERT INTO consignado (estoque_id, fornecedor_id, Quantidade, Valor)
            VALUES (%s, %s, %s, %s)
        """, (id_prod, id_forn, quantidade, valor))

        conexao.commit()
        messagebox.showinfo("Sucesso", f"Entrada de {quantidade}x no Consignado!")
        
        entry_qtd.delete(0, tk.END)
        entry_valor.delete(0, tk.END)

    except ValueError:
        messagebox.showerror("Erro", "Quantidade ou Valor inválidos.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    finally:
        if conexao: conexao.close()

def _carregar_lista_consignado(tree, termo_busca=""):
    for i in tree.get_children():
        tree.delete(i)
    
    conexao = banco.conectar()
    cursor = conexao.cursor()
    
    sql = """
        SELECT c.id, e.codigo, e.Nome, f.nome, c.Quantidade, c.Valor, e.id, f.id
        FROM consignado c
        JOIN estoque e ON c.estoque_id = e.id
        JOIN fornecedores f ON c.fornecedor_id = f.id
        WHERE c.Quantidade > 0
    """
    params = ()
    
    if termo_busca:
        sql += " AND (e.Nome LIKE %s OR e.codigo LIKE %s)"
        like = f"%{termo_busca}%"
        params = (like, like)
    
    sql += " ORDER BY e.Nome ASC"
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    
    for row in rows:
        cod_visual = row[1] if row[1] else "-"
        tree.insert("", tk.END, values=(row[0], cod_visual, row[2], row[3], row[4], row[5], row[6], row[7]))
    
    conexao.close()

def _transferir_logic(tree, entry_qtd_transf):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Aviso", "Selecione um item na lista acima.")
        return
    
    item_values = tree.item(selected[0])['values']
    id_consignado = item_values[0]
    nome_prod = item_values[2]
    qtd_disponivel = float(item_values[4])
    valor_unitario = float(item_values[5])
    id_prod = item_values[6]
    id_forn = item_values[7]
    
    try:
        qtd_transferir = float(entry_qtd_transf.get().strip().replace(',', '.'))
        if qtd_transferir <= 0 or qtd_transferir > qtd_disponivel:
            messagebox.showerror("Erro", f"Quantidade inválida.\nMáximo disponível: {qtd_disponivel}")
            return
    except:
        messagebox.showerror("Erro", "Digite um número válido.")
        return

    conexao = banco.conectar()
    cursor = conexao.cursor()
    
    try:
        cursor.execute("UPDATE consignado SET Quantidade = Quantidade - %s WHERE id = %s", (qtd_transferir, id_consignado))
        cursor.execute("UPDATE estoque SET Quantidade = Quantidade + %s WHERE id = %s", (qtd_transferir, id_prod))
        cursor.execute("""
            INSERT INTO consignado_usos (estoque_id, fornecedor_id, usuario_id, QuantidadeUsada, ValorUnitario)
            VALUES (%s, %s, 1, %s, %s)
        """, (id_prod, id_forn, qtd_transferir, valor_unitario))
        
        conexao.commit()
        messagebox.showinfo("Sucesso", f"Transferido {qtd_transferir}x '{nome_prod}' para seu estoque!")
        
        _carregar_lista_consignado(tree) 
        entry_qtd_transf.delete(0, tk.END)

    except Exception as e:
        conexao.rollback()
        messagebox.showerror("Erro", f"Falha na transferência: {e}")
    finally:
        conexao.close()

def _get_fornecedores():
    lista = []
    try:
        con = banco.conectar()
        cur = con.cursor()
        cur.execute("SELECT nome FROM fornecedores ORDER BY nome")
        for row in cur.fetchall(): lista.append(row[0])
        con.close()
    except: pass
    return lista


# =============================================================================
# JANELA PRINCIPAL (AGORA É UM FRAME)
# =============================================================================
def abrir_janela_consignado(parent):
    # Frame Principal
    frame_total = tk.Frame(parent, bg="white")
    frame_total.pack(fill="both", expand=True)

    # Título
    tk.Label(frame_total, text="Controle de Consignado", font=("Arial", 16, "bold"), bg="white", fg="#0056b3").pack(pady=15)
    
    # --- SISTEMA DE ABAS ---
    style = ttk.Style()
    style.configure("TNotebook", background="white")
    style.configure("TFrame", background="white")

    abas = ttk.Notebook(frame_total)
    abas.pack(fill="both", expand=True, padx=20, pady=10)
    
    tab1 = tk.Frame(abas, bg="white")
    tab2 = tk.Frame(abas, bg="white")
    
    abas.add(tab1, text="  1. Receber Material (Entrada)  ")
    abas.add(tab2, text="  2. Usar Material (Transferência)  ")
    
    # --- ABA 1: ENTRADA ---
    frame_tab1_center = tk.Frame(tab1, bg="white")
    frame_tab1_center.pack(expand=True)

    tk.Label(frame_tab1_center, text="Registrar Chegada de Material", font=("Arial", 12, "bold"), bg="white", fg="#555").pack(pady=15)
    
    frame_form = tk.Frame(frame_tab1_center, bg="#f0f8ff", bd=1, relief="solid", padx=20, pady=20)
    frame_form.pack()
    
    tk.Label(frame_form, text="Fornecedor:", bg="#f0f8ff").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    cb_forn = ttk.Combobox(frame_form, values=_get_fornecedores(), width=25)
    cb_forn.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(frame_form, text="Nome/Cód Produto:", bg="#f0f8ff").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_prod = tk.Entry(frame_form, width=28)
    entry_prod.grid(row=1, column=1, padx=5, pady=5)
    
    tk.Label(frame_form, text="Quantidade:", bg="#f0f8ff").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    entry_qtd = tk.Entry(frame_form, width=15)
    entry_qtd.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    
    tk.Label(frame_form, text="Valor Unitário (Custo):", bg="#f0f8ff").grid(row=3, column=0, padx=5, pady=5, sticky="e")
    entry_valor = tk.Entry(frame_form, width=15)
    entry_valor.grid(row=3, column=1, padx=5, pady=5, sticky="w")
    
    tk.Button(frame_form, text="Registrar Entrada", bg="#007bff", fg="white", font=("Arial", 10, "bold"),
              command=lambda: _registrar_chegada_logic(cb_forn, entry_prod, entry_qtd, entry_valor)).grid(row=4, columnspan=2, pady=20)

    # --- ABA 2: TRANSFERÊNCIA ---
    frame_top_tab2 = tk.Frame(tab2, bg="white")
    frame_top_tab2.pack(fill="x", padx=10, pady=10)

    tk.Label(frame_top_tab2, text="Transferir do Consignado para Estoque Próprio", font=("Arial", 12, "bold"), bg="white", fg="#555").pack(side="left")
    
    # Área de Pesquisa
    frame_busca = tk.Frame(tab2, bg="#f0f0f0", pady=5)
    frame_busca.pack(fill="x", padx=10)
    
    tk.Label(frame_busca, text="🔍 Pesquisar:", bg="#f0f0f0").pack(side="left", padx=5)
    entry_busca = tk.Entry(frame_busca, width=30)
    entry_busca.pack(side="left", padx=5)
    
    btn_buscar = tk.Button(frame_busca, text="Filtrar", command=lambda: _carregar_lista_consignado(tree, entry_busca.get()))
    btn_buscar.pack(side="left", padx=5)
    
    entry_busca.bind('<Return>', lambda e: _carregar_lista_consignado(tree, entry_busca.get()))

    # Lista (Treeview)
    frame_lista = tk.Frame(tab2, bg="white")
    frame_lista.pack(fill="both", expand=True, padx=10, pady=5)

    colunas = ("ID", "Cód", "Produto", "Fornecedor", "Qtd Disp.", "Valor Un.", "idp", "idf")
    tree = ttk.Treeview(frame_lista, columns=colunas, show="headings", height=10)
    
    tree.heading("ID", text="ID")
    tree.heading("Cód", text="Cód")
    tree.heading("Produto", text="Produto")
    tree.heading("Fornecedor", text="Fornecedor")
    tree.heading("Qtd Disp.", text="Qtd Disp.")
    tree.heading("Valor Un.", text="Valor Un.")
    
    tree.column("ID", width=30, anchor="center")
    tree.column("Cód", width=80, anchor="center")
    tree.column("Produto", width=250)
    tree.column("idp", width=0, stretch=tk.NO)
    tree.column("idf", width=0, stretch=tk.NO)
    
    scroll = ttk.Scrollbar(frame_lista, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scroll.set)

    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    
    # Área de Ação
    frame_action = tk.Frame(tab2, bg="#f0f0f0", bd=2, relief="groove")
    frame_action.pack(padx=10, pady=10, fill="x")
    
    tk.Label(frame_action, text="Quantidade a Transferir:", bg="#f0f0f0").pack(side="left", padx=10)
    entry_transf = tk.Entry(frame_action, width=10)
    entry_transf.pack(side="left", padx=5)
    
    tk.Button(frame_action, text="CONFIRMAR USO", bg="#28a745", fg="white", font=("Arial", 9, "bold"),
              command=lambda: _transferir_logic(tree, entry_transf)).pack(side="left", padx=20)
    
    tk.Button(tab2, text="Recarregar Lista", command=lambda: _carregar_lista_consignado(tree)).pack(pady=5)
    
    _carregar_lista_consignado(tree)