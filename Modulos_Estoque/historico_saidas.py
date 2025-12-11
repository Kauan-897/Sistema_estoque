import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import banco
import csv
from datetime import datetime

# =============================================================================
# LÓGICA ABA 1: SAÍDAS GERAIS (VENDAS)
# =============================================================================
def _pesquisar_geral(tree, entry_cliente, entry_produto, label_total):
    # Limpa a tabela
    for i in tree.get_children():
        tree.delete(i)
        
    filtro_cliente = entry_cliente.get().strip()
    filtro_produto = entry_produto.get().strip()
    
    conexao = banco.conectar()
    if not conexao: return
    cursor = conexao.cursor()
    
    try:
        # Busca na tabela SAIDAS
        sql = """
            SELECT s.id, s.DataSaida, e.Nome, s.Quantidade, c.nome, u.username
            FROM saidas s
            JOIN estoque e ON s.estoque_id = e.id
            JOIN clientes c ON s.cliente_id = c.id
            JOIN usuarios u ON s.usuario_id = u.id
            WHERE 1=1
        """
        params = []
        
        if filtro_cliente:
            sql += " AND c.nome LIKE %s"
            params.append(f"%{filtro_cliente}%")
        if filtro_produto:
            sql += " AND e.Nome LIKE %s"
            params.append(f"%{filtro_produto}%")
            
        sql += " ORDER BY s.DataSaida DESC, s.id DESC"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        total_qtd = 0
        for row in rows:
            # Formata Data
            data_fmt = row[1].strftime('%d/%m/%Y') if row[1] else "-"
            tree.insert("", tk.END, values=(row[0], data_fmt, row[2], row[3], row[4], row[5]))
            total_qtd += row[3]
            
        label_total.config(text=f"Total de Itens Baixados: {total_qtd}")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro na busca geral: {e}")
    finally:
        conexao.close()

# =============================================================================
# LÓGICA ABA 2: USO DE CONSIGNADO (DÍVIDA GERADA)
# =============================================================================
def _pesquisar_consignado(tree, entry_fornecedor, entry_produto, label_total):
    for i in tree.get_children():
        tree.delete(i)
        
    filtro_forn = entry_fornecedor.get().strip()
    filtro_prod = entry_produto.get().strip()
    
    conexao = banco.conectar()
    if not conexao: return
    cursor = conexao.cursor()
    
    try:
        # Busca na tabela CONSIGNADO_USOS
        sql = """
            SELECT cu.id, cu.DataUso, e.Nome, f.nome, cu.QuantidadeUsada, cu.ValorUnitario, u.username
            FROM consignado_usos cu
            JOIN estoque e ON cu.estoque_id = e.id
            JOIN fornecedores f ON cu.fornecedor_id = f.id
            JOIN usuarios u ON cu.usuario_id = u.id
            WHERE 1=1
        """
        params = []
        
        if filtro_forn:
            sql += " AND f.nome LIKE %s"
            params.append(f"%{filtro_forn}%")
        if filtro_prod:
            sql += " AND e.Nome LIKE %s"
            params.append(f"%{filtro_prod}%")
            
        sql += " ORDER BY cu.DataUso DESC, cu.id DESC"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        soma_valor_total = 0.0
        
        for row in rows:
            # row: 0=ID, 1=Data, 2=Prod, 3=Forn, 4=Qtd, 5=ValorUn, 6=User
            data_fmt = row[1].strftime('%d/%m/%Y') if row[1] else "-"
            qtd = float(row[4])
            valor_un = float(row[5])
            valor_total = qtd * valor_un # Cálculo do total da linha
            
            # Formata dinheiro
            v_un_fmt = f"R$ {valor_un:.2f}"
            v_tot_fmt = f"R$ {valor_total:.2f}"
            
            tree.insert("", tk.END, values=(row[0], data_fmt, row[2], row[3], row[4], v_un_fmt, v_tot_fmt, row[6]))
            soma_valor_total += valor_total
            
        label_total.config(text=f"Valor Total Devido: R$ {soma_valor_total:.2f}")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro na busca consignado: {e}")
    finally:
        conexao.close()

# =============================================================================
# EXPORTAÇÃO GENÉRICA (CSV)
# =============================================================================
def _exportar_csv(tree, nome_arquivo="relatorio"):
    if not tree.get_children():
        messagebox.showwarning("Aviso", "Sem dados para exportar.")
        return
        
    caminho = filedialog.asksaveasfilename(defaultextension=".csv", 
                                           filetypes=[("CSV", "*.csv")],
                                           initialfile=f"{nome_arquivo}_{datetime.now().strftime('%Y%m%d')}.csv",
                                           title="Salvar Relatório")
    if not caminho: return
    
    try:
        with open(caminho, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            
            # Pega os cabeçalhos da Treeview automaticamente
            colunas = [tree.heading(col)["text"] for col in tree["columns"]]
            writer.writerow(colunas)
            
            # Dados
            for item in tree.get_children():
                row = tree.item(item)['values']
                writer.writerow(row)
                
        messagebox.showinfo("Sucesso", "Relatório salvo com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar: {e}")

# =============================================================================
# JANELA PRINCIPAL (EMBUTIDA NO MENU)
# =============================================================================
def abrir_janela_historico(parent):
    # Cria o Frame Principal
    frame_total = tk.Frame(parent, bg="white")
    frame_total.pack(fill="both", expand=True)

    # Título
    tk.Label(frame_total, text="Histórico de Movimentações", font=("Arial", 16, "bold"), bg="white", fg="#444").pack(pady=15)
    
    # --- SISTEMA DE ABAS ---
    # Estilo para deixar as abas bonitas no fundo branco
    style = ttk.Style()
    style.configure("TNotebook", background="white")
    style.configure("TFrame", background="white")

    abas = ttk.Notebook(frame_total)
    abas.pack(fill="both", expand=True, padx=20, pady=10)
    
    tab1 = tk.Frame(abas, bg="white")
    tab2 = tk.Frame(abas, bg="white")
    
    abas.add(tab1, text="  1. Saídas Gerais (Vendas)  ")
    abas.add(tab2, text="  2. Histórico Consignado (Compras/Uso)  ")
    
    # =========================================================================
    # CONTEÚDO DA ABA 1: SAÍDAS GERAIS
    # =========================================================================
    frame_filtros1 = tk.Frame(tab1, bg="#f9f9f9", bd=1, relief="solid")
    frame_filtros1.pack(fill="x", padx=10, pady=10)
    
    tk.Label(frame_filtros1, text="Cliente:", bg="#f9f9f9").pack(side="left", padx=10, pady=10)
    entry_cli1 = tk.Entry(frame_filtros1, width=25)
    entry_cli1.pack(side="left", padx=5)
    
    tk.Label(frame_filtros1, text="Produto:", bg="#f9f9f9").pack(side="left", padx=10)
    entry_prod1 = tk.Entry(frame_filtros1, width=25)
    entry_prod1.pack(side="left", padx=5)
    
    tk.Button(frame_filtros1, text="🔍 Pesquisar", bg="#e1f5fe",
              command=lambda: _pesquisar_geral(tree1, entry_cli1, entry_prod1, lbl_total1)).pack(side="left", padx=20)

    # Container da Lista 1 (Para scrollbar funcionar bem)
    container_lista1 = tk.Frame(tab1, bg="white")
    container_lista1.pack(fill="both", expand=True, padx=10)

    cols1 = ("ID", "Data", "Produto", "Qtd", "Cliente", "Vendedor")
    tree1 = ttk.Treeview(container_lista1, columns=cols1, show="headings", height=15)
    
    tree1.heading("ID", text="ID")
    tree1.heading("Data", text="Data")
    tree1.heading("Produto", text="Produto")
    tree1.heading("Qtd", text="Quantidade")
    tree1.heading("Cliente", text="Cliente")
    tree1.heading("Vendedor", text="Vendedor")
    
    tree1.column("ID", width=50, anchor="center")
    tree1.column("Data", width=100, anchor="center")
    tree1.column("Produto", width=300)
    tree1.column("Qtd", width=80, anchor="center")
    tree1.column("Cliente", width=200)
    
    scroll1 = ttk.Scrollbar(container_lista1, orient="vertical", command=tree1.yview)
    tree1.configure(yscroll=scroll1.set)
    
    tree1.pack(side="left", fill="both", expand=True)
    scroll1.pack(side="right", fill="y")
    
    # Footer 1
    frame_foot1 = tk.Frame(tab1, bg="white")
    frame_foot1.pack(fill="x", padx=10, pady=10)
    lbl_total1 = tk.Label(frame_foot1, text="Total: 0", font=("Arial", 10, "bold"), bg="white")
    lbl_total1.pack(side="left")
    tk.Button(frame_foot1, text="📂 Exportar CSV", bg="#ccffcc", command=lambda: _exportar_csv(tree1, "saidas_gerais")).pack(side="right")

    # =========================================================================
    # CONTEÚDO DA ABA 2: HISTÓRICO CONSIGNADO
    # =========================================================================
    frame_filtros2 = tk.Frame(tab2, bg="#f9f9f9", bd=1, relief="solid")
    frame_filtros2.pack(fill="x", padx=10, pady=10)
    
    tk.Label(frame_filtros2, text="Fornecedor:", bg="#f9f9f9").pack(side="left", padx=10, pady=10)
    entry_forn2 = tk.Entry(frame_filtros2, width=25)
    entry_forn2.pack(side="left", padx=5)
    
    tk.Label(frame_filtros2, text="Produto:", bg="#f9f9f9").pack(side="left", padx=10)
    entry_prod2 = tk.Entry(frame_filtros2, width=25)
    entry_prod2.pack(side="left", padx=5)
    
    tk.Button(frame_filtros2, text="🔍 Pesquisar", bg="#e1f5fe",
              command=lambda: _pesquisar_consignado(tree2, entry_forn2, entry_prod2, lbl_total2)).pack(side="left", padx=20)

    # Container da Lista 2
    container_lista2 = tk.Frame(tab2, bg="white")
    container_lista2.pack(fill="both", expand=True, padx=10)

    cols2 = ("ID", "Data", "Produto", "Fornecedor", "Qtd", "V. Unit", "V. Total", "Usuário")
    tree2 = ttk.Treeview(container_lista2, columns=cols2, show="headings", height=15)
    
    tree2.heading("ID", text="ID")
    tree2.heading("Data", text="Data Uso")
    tree2.heading("Produto", text="Produto")
    tree2.heading("Fornecedor", text="Fornecedor")
    tree2.heading("Qtd", text="Qtd Usada")
    tree2.heading("V. Unit", text="Custo Un.")
    tree2.heading("V. Total", text="Total Devido")
    tree2.heading("Usuário", text="Quem Usou")
    
    tree2.column("ID", width=50, anchor="center")
    tree2.column("Data", width=100, anchor="center")
    tree2.column("Produto", width=250)
    tree2.column("Fornecedor", width=150)
    tree2.column("Qtd", width=80, anchor="center")
    tree2.column("V. Unit", width=90, anchor="e")
    tree2.column("V. Total", width=100, anchor="e")
    
    scroll2 = ttk.Scrollbar(container_lista2, orient="vertical", command=tree2.yview)
    tree2.configure(yscroll=scroll2.set)

    tree2.pack(side="left", fill="both", expand=True)
    scroll2.pack(side="right", fill="y")
    
    # Footer 2
    frame_foot2 = tk.Frame(tab2, bg="white")
    frame_foot2.pack(fill="x", padx=10, pady=10)
    lbl_total2 = tk.Label(frame_foot2, text="Total Devido: R$ 0.00", font=("Arial", 11, "bold"), fg="red", bg="white")
    lbl_total2.pack(side="left")
    tk.Button(frame_foot2, text="📂 Exportar CSV", bg="#ccffcc", command=lambda: _exportar_csv(tree2, "uso_consignado")).pack(side="right")

    # Inicialização
    entry_cli1.bind('<Return>', lambda e: _pesquisar_geral(tree1, entry_cli1, entry_prod1, lbl_total1))
    entry_forn2.bind('<Return>', lambda e: _pesquisar_consignado(tree2, entry_forn2, entry_prod2, lbl_total2))
    
    _pesquisar_geral(tree1, entry_cli1, entry_prod1, lbl_total1)
    _pesquisar_consignado(tree2, entry_forn2, entry_prod2, lbl_total2)