import tkinter as tk
from tkinter import ttk
import banco

def carregar_dados_dashboard(lbl_total_itens, lbl_valor_estoque, tree_alertas):
    for i in tree_alertas.get_children(): tree_alertas.delete(i)
    
    conexao = banco.conectar()
    if not conexao: return
    cursor = conexao.cursor()
    
    try:
        # 1. Total Itens
        cursor.execute("SELECT COUNT(*) FROM estoque WHERE status = 'Ativo'")
        total_itens = cursor.fetchone()[0]
        lbl_total_itens.config(text=f"{total_itens}")

        # 2. VALOR TOTAL EM ESTOQUE (CUSTO) - NOVO!
        # Soma (Quantidade * Preço de Custo) de todos os itens ativos
        cursor.execute("SELECT SUM(quantidade * preco_custo) FROM estoque WHERE status = 'Ativo'")
        valor_total = cursor.fetchone()[0]
        if valor_total is None: valor_total = 0.0
        lbl_valor_estoque.config(text=f"R$ {valor_total:,.2f}")

        # 3. Alerta Estoque Baixo
        cursor.execute("""
            SELECT codigo, nome, quantidade, estoque_minimo
            FROM estoque 
            WHERE status = 'Ativo' AND quantidade < estoque_minimo 
            ORDER BY quantidade ASC LIMIT 20
        """)
        for row in cursor.fetchall():
            cod = row[0] if row[0] else "-"
            tree_alertas.insert("", tk.END, values=(cod, row[1], row[2], row[3]))

    except Exception as e:
        print(f"Erro dashboard: {e}")
    finally:
        conexao.close()

def abrir_dashboard(parent):
    frame_total = tk.Frame(parent, bg="white")
    frame_total.pack(fill="both", expand=True)

    frame_header = tk.Frame(frame_total, bg="#0056b3", height=80)
    frame_header.pack(fill="x")
    tk.Label(frame_header, text="Painel de Controle Financeiro", font=("Arial", 22, "bold"), bg="#0056b3", fg="white").pack(pady=20)

    # --- CARDS ---
    frame_kpi = tk.Frame(frame_total, bg="white")
    frame_kpi.pack(fill="x", padx=40, pady=20)

    # Card 1: Itens
    card1 = tk.Frame(frame_kpi, bg="#f8f9fa", bd=1, relief="solid", width=250, height=120)
    card1.pack(side="left", padx=20)
    card1.pack_propagate(False)
    tk.Label(card1, text="📦 Produtos Ativos", bg="#f8f9fa", fg="gray").pack(pady=(15,5))
    lbl_total = tk.Label(card1, text="...", font=("Arial", 24, "bold"), bg="#f8f9fa", fg="#0056b3")
    lbl_total.pack()

    # Card 2: Valor em Estoque (NOVO)
    card2 = tk.Frame(frame_kpi, bg="#e3f2fd", bd=1, relief="solid", width=300, height=120)
    card2.pack(side="left", padx=20)
    card2.pack_propagate(False)
    tk.Label(card2, text="💰 Valor Total em Estoque (Custo)", bg="#e3f2fd", fg="gray").pack(pady=(15,5))
    lbl_valor = tk.Label(card2, text="R$ 0,00", font=("Arial", 24, "bold"), bg="#e3f2fd", fg="#2e7d32")
    lbl_valor.pack()

    # --- TABELA ALERTAS ---
    tk.Label(frame_total, text="⚠️ ALERTA DE REPOSIÇÃO", font=("Arial", 14, "bold"), bg="white", fg="#d9534f").pack(anchor="w", padx=40, pady=(20,10))
    
    frame_tabela = tk.Frame(frame_total, bg="white")
    frame_tabela.pack(fill="both", expand=True, padx=40, pady=10)

    colunas = ("Cód", "Produto", "Qtd Atual", "Meta Mínima")
    tree = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=10)
    tree.heading("Cód", text="Cód"); tree.column("Cód", width=80, anchor="center")
    tree.heading("Produto", text="Produto"); tree.column("Produto", width=400)
    tree.heading("Qtd Atual", text="Qtd Atual"); tree.column("Qtd Atual", width=100, anchor="center")
    tree.heading("Meta Mínima", text="Meta"); tree.column("Meta Mínima", width=100, anchor="center")
    
    tree.pack(side="left", fill="both", expand=True)
    
    # Botão Atualizar
    tk.Button(frame_total, text="🔄 Atualizar Dados", 
              command=lambda: carregar_dados_dashboard(lbl_total, lbl_valor, tree)).pack(pady=10)

    carregar_dados_dashboard(lbl_total, lbl_valor, tree)