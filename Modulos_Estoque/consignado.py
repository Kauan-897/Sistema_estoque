import tkinter as tk
from tkinter import ttk, messagebox
import banco

# =============================================================================
# LÓGICA: REGISTRAR CHEGADA (ENTRADA NO CONSIGNADO)
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

        # 1. Pega ID do Fornecedor
        cursor.execute("SELECT id FROM fornecedores WHERE nome = %s", (nome_fornecedor,))
        res_forn = cursor.fetchone()
        if not res_forn:
            messagebox.showerror("Erro", "Fornecedor não encontrado.")
            return
        id_forn = res_forn[0]

        # 2. Pega ID do Produto (Tem que existir no cadastro básico)
        # Tenta pelo Código OU Nome
        cursor.execute("SELECT id FROM estoque WHERE codigo = %s OR nome = %s", (nome_produto, nome_produto))
        res_prod = cursor.fetchone()
        
        if not res_prod:
            messagebox.showerror("Erro", f"Produto '{nome_produto}' não cadastrado no sistema.\nCadastre-o primeiro em 'Cadastrar Itens'.")
            return
        id_prod = res_prod[0]

        # 3. Insere na tabela CONSIGNADO
        cursor.execute("""
            INSERT INTO consignado (estoque_id, fornecedor_id, Quantidade, Valor)
            VALUES (%s, %s, %s, %s)
        """, (id_prod, id_forn, quantidade, valor))

        conexao.commit()
        messagebox.showinfo("Sucesso", f"Entrada de {quantidade}x no Consignado!")
        
        # Limpar campos
        entry_qtd.delete(0, tk.END)
        entry_valor.delete(0, tk.END)

    except ValueError:
        messagebox.showerror("Erro", "Quantidade ou Valor inválidos.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    finally:
        if conexao: conexao.close()

# =============================================================================
# LÓGICA: TRANSFERIR (COM PESQUISA)
# =============================================================================
def _carregar_lista_consignado(tree, termo_busca=""):
    # Limpa a lista
    for i in tree.get_children():
        tree.delete(i)
    
    conexao = banco.conectar()
    cursor = conexao.cursor()
    
    # SQL Base: Traz itens com quantidade > 0
    sql = """
        SELECT c.id, e.codigo, e.Nome, f.nome, c.Quantidade, c.Valor, e.id, f.id
        FROM consignado c
        JOIN estoque e ON c.estoque_id = e.id
        JOIN fornecedores f ON c.fornecedor_id = f.id
        WHERE c.Quantidade > 0
    """
    
    params = ()
    
    # Se tiver busca, adiciona o filtro
    if termo_busca:
        sql += " AND (e.Nome LIKE %s OR e.codigo LIKE %s)"
        like = f"%{termo_busca}%"
        params = (like, like)
    
    sql += " ORDER BY e.Nome ASC"
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    
    for row in rows:
        # row: 0=id_consignado, 1=COD, 2=Prod, 3=Forn, 4=Qtd, 5=Valor, 6=id_prod, 7=id_forn
        cod_visual = row[1] if row[1] else "-"
        tree.insert("", tk.END, values=(row[0], cod_visual, row[2], row[3], row[4], row[5], row[6], row[7]))
    
    conexao.close()

def _transferir_logic(tree, entry_qtd_transf):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Aviso", "Selecione um item na lista acima.")
        return
    
    # Pega valores da linha selecionada
    item_values = tree.item(selected[0])['values']
    # values: 0=id_consig, 1=COD, 2=Prod, 3=Forn, 4=QtdDisp, 5=Valor, 6=id_prod, 7=id_forn
    
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
        # 1. Diminui do Consignado
        cursor.execute("UPDATE consignado SET Quantidade = Quantidade - %s WHERE id = %s", (qtd_transferir, id_consignado))
        
        # 2. Aumenta no Estoque Próprio
        cursor.execute("UPDATE estoque SET Quantidade = Quantidade + %s WHERE id = %s", (qtd_transferir, id_prod))
        
        # 3. Registra Uso
        cursor.execute("""
            INSERT INTO consignado_usos (estoque_id, fornecedor_id, usuario_id, QuantidadeUsada, ValorUnitario)
            VALUES (%s, %s, 1, %s, %s)
        """, (id_prod, id_forn, qtd_transferir, valor_unitario))
        
        conexao.commit()
        messagebox.showinfo("Sucesso", f"Transferido {qtd_transferir}x '{nome_prod}' para seu estoque!")
        
        _carregar_lista_consignado(tree) # Atualiza a lista geral
        entry_qtd_transf.delete(0, tk.END)

    except Exception as e:
        conexao.rollback()
        messagebox.showerror("Erro", f"Falha na transferência: {e}")
    finally:
        conexao.close()

# --- AUXILIARES ---
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
# JANELA PRINCIPAL
# =============================================================================
def abrir_janela_consignado(janela_raiz):
    janela = tk.Toplevel(janela_raiz)
    janela.title("Controle de Consignado")
    janela.geometry("900x650")
    
    abas = ttk.Notebook(janela)
    abas.pack(fill="both", expand=True, padx=10, pady=10)
    
    tab1 = tk.Frame(abas)
    tab2 = tk.Frame(abas)
    
    abas.add(tab1, text="1. Receber Material (Entrada)")
    abas.add(tab2, text="2. Usar Material (Transferência)")
    
    # --- ABA 1: ENTRADA ---
    tk.Label(tab1, text="Registrar Chegada de Material Consignado", font=("Arial", 12, "bold")).pack(pady=15)
    
    frame_form = tk.Frame(tab1)
    frame_form.pack()
    
    tk.Label(frame_form, text="Fornecedor:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    cb_forn = ttk.Combobox(frame_form, values=_get_fornecedores())
    cb_forn.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(frame_form, text="Nome/Cód Produto:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_prod = tk.Entry(frame_form)
    entry_prod.grid(row=1, column=1, padx=5, pady=5)
    
    tk.Label(frame_form, text="Quantidade:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    entry_qtd = tk.Entry(frame_form)
    entry_qtd.grid(row=2, column=1, padx=5, pady=5)
    
    tk.Label(frame_form, text="Valor Unitário (Custo):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
    entry_valor = tk.Entry(frame_form)
    entry_valor.grid(row=3, column=1, padx=5, pady=5)
    
    tk.Button(tab1, text="Registrar Entrada", bg="#e1f5fe", 
              command=lambda: _registrar_chegada_logic(cb_forn, entry_prod, entry_qtd, entry_valor)).pack(pady=20)

    # --- ABA 2: TRANSFERÊNCIA (COM PESQUISA) ---
    tk.Label(tab2, text="Transferir do Consignado para Estoque Próprio", font=("Arial", 12, "bold")).pack(pady=10)
    
    # Área de Pesquisa
    frame_busca = tk.Frame(tab2, bg="#f0f0f0", pady=5)
    frame_busca.pack(fill="x", padx=10)
    
    tk.Label(frame_busca, text="🔍 Pesquisar:", bg="#f0f0f0").pack(side="left", padx=5)
    entry_busca = tk.Entry(frame_busca, width=30)
    entry_busca.pack(side="left", padx=5)
    
    btn_buscar = tk.Button(frame_busca, text="Filtrar", command=lambda: _carregar_lista_consignado(tree, entry_busca.get()))
    btn_buscar.pack(side="left", padx=5)
    
    # Bind Enter key
    entry_busca.bind('<Return>', lambda e: _carregar_lista_consignado(tree, entry_busca.get()))

    tk.Label(tab2, text="Selecione o item abaixo e diga quanto vai usar:", fg="gray").pack(pady=(10,0))
    
    # Lista (Treeview)
    colunas = ("ID", "Cód", "Produto", "Fornecedor", "Qtd Disp.", "Valor Un.", "idp", "idf")
    tree = ttk.Treeview(tab2, columns=colunas, show="headings", height=12)
    
    tree.heading("ID", text="ID")
    tree.heading("Cód", text="Cód")
    tree.heading("Produto", text="Produto")
    tree.heading("Fornecedor", text="Fornecedor")
    tree.heading("Qtd Disp.", text="Qtd Disp.")
    tree.heading("Valor Un.", text="Valor Un.")
    
    tree.column("ID", width=30)
    tree.column("Cód", width=80)
    tree.column("Produto", width=200)
    tree.column("idp", width=0, stretch=tk.NO) # Escondido
    tree.column("idf", width=0, stretch=tk.NO) # Escondido
    
    tree.pack(padx=10, pady=5, fill="x")
    
    # Área de Ação
    frame_action = tk.Frame(tab2, bg="#f0f0f0", bd=2, relief="groove")
    frame_action.pack(padx=10, pady=10, fill="x")
    
    tk.Label(frame_action, text="Quantidade a Transferir:", bg="#f0f0f0").pack(side="left", padx=10)
    entry_transf = tk.Entry(frame_action, width=10)
    entry_transf.pack(side="left", padx=5)
    
    tk.Button(frame_action, text="CONFIRMAR USO", bg="#ccffcc", fg="green", font=("Arial", 9, "bold"),
              command=lambda: _transferir_logic(tree, entry_transf)).pack(side="left", padx=20)
    
    # Botão de Resetar Lista
    tk.Button(tab2, text="Recarregar Lista Completa", 
              command=lambda: _carregar_lista_consignado(tree)).pack(pady=5)
    
    # Carregar dados iniciais
    _carregar_lista_consignado(tree)