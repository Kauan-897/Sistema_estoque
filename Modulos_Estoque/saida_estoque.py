import tkinter as tk
from tkinter import messagebox
import banco
from decimal import Decimal, InvalidOperation

# =============================================================================
# LÓGICA (MANTIDA IGUAL)
# =============================================================================

def _remover_stock_logic(memo_widget, entry_nome, entry_qntd, entry_cliente_id):
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    
    termo_busca = entry_nome.get().strip()
    qntd_str = entry_qntd.get().strip().replace(',', '.')
    cliente_id_str = entry_cliente_id.get().strip()
    
    if not termo_busca:
        memo_widget.insert(tk.END, "ERRO: Campo 'Produto' vazio.")
        memo_widget.config(state=tk.DISABLED)
        return
        
    try:
        quantidade = Decimal(qntd_str)
        if quantidade <= 0: raise ValueError
    except (ValueError, InvalidOperation):
        memo_widget.insert(tk.END, f"ERRO: Quantidade inválida.\n")
        memo_widget.config(state=tk.DISABLED)
        return

    try:
        cliente_id = int(cliente_id_str)
    except ValueError:
        memo_widget.insert(tk.END, f"ERRO: ID Cliente inválido.\n")
        memo_widget.config(state=tk.DISABLED)
        return

    usuario_id_fixo = 1 
    
    conexao = None
    cursor = None
    try:
        conexao = banco.conectar()
        if not conexao:
             memo_widget.insert(tk.END, "ERRO: Sem conexão MySQL.")
             return
        cursor = conexao.cursor(buffered=True)
        
        # Busca Produto
        cursor.execute("SELECT id, nome, quantidade FROM estoque WHERE codigo = %s", (termo_busca,))
        produto = cursor.fetchone()
        if not produto:
            cursor.execute("SELECT id, nome, quantidade FROM estoque WHERE nome = %s", (termo_busca,))
            produto = cursor.fetchone()
            
        if not produto:
            memo_widget.insert(tk.END, f"ERRO: Produto '{termo_busca}' não encontrado.\n")
            raise Exception("Produto inexistente")

        estoque_id = produto[0]
        nome_real = produto[1]
        stock_atual = produto[2]

        if stock_atual < quantidade:
            memo_widget.insert(tk.END, f"ERRO: Stock insuficiente!\n Disp: {stock_atual} / Pedido: {quantidade}")
            raise Exception("Stock insuficiente")

        # Busca Cliente
        cursor.execute("SELECT id, nome FROM clientes WHERE id = %s", (cliente_id,))
        cliente = cursor.fetchone()
        if not cliente:
            memo_widget.insert(tk.END, f"ERRO: Cliente ID {cliente_id} inexistente.\n")
            raise Exception("Cliente inexistente")

        # Executa Saída
        novo_stock = stock_atual - quantidade
        cursor.execute("UPDATE estoque SET quantidade = %s WHERE id = %s", (novo_stock, estoque_id))
        cursor.execute("""
            INSERT INTO saidas (estoque_id, cliente_id, usuario_id, Quantidade) 
            VALUES (%s, %s, %s, %s)
        """, (estoque_id, cliente_id, usuario_id_fixo, quantidade))
        
        conexao.commit()
        
        memo_widget.insert(tk.END, f"SUCESSO: Saída registrada!\n")
        memo_widget.insert(tk.END, f"  Cliente: {cliente[1]}\n")
        memo_widget.insert(tk.END, f"  Produto: {nome_real}\n")
        memo_widget.insert(tk.END, f"  Novo Stock: {novo_stock}")
        
        entry_nome.delete(0, tk.END)
        entry_qntd.delete(0, tk.END)
        entry_cliente_id.delete(0, tk.END)
            
    except Exception as e:
        if conexao: conexao.rollback()
        if "ERRO" not in memo_widget.get("1.0", tk.END):
            memo_widget.insert(tk.END, f"\nERRO TÉCNICO: {e}")
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()
        memo_widget.config(state=tk.DISABLED)

# --- FUNÇÕES DE PESQUISA ---
def _pesquisar_produto(entry_busca, listbox):
    termo = entry_busca.get().strip()
    listbox.delete(0, tk.END)
    
    conexao = banco.conectar()
    if not conexao: return
    cursor = conexao.cursor()
    
    try:
        sql = "SELECT codigo, nome, quantidade FROM estoque WHERE nome LIKE %s OR codigo LIKE %s ORDER BY nome ASC"
        like = f"%{termo}%"
        cursor.execute(sql, (like, like))
        for row in cursor.fetchall():
            cod = row[0] if row[0] else "-"
            listbox.insert(tk.END, f"[{cod}] {row[1]} (Qtd: {row[2]})")
        if listbox.size() == 0: listbox.insert(tk.END, "Nenhum produto encontrado.")
    finally:
        cursor.close(); conexao.close()

def _selecionar_produto(event, listbox, entry_alvo):
    sel = listbox.curselection()
    if not sel: return
    texto = listbox.get(sel[0])
    if "Nenhum" in texto: return
    try:
        nome = texto.split('] ', 1)[1].split(' (Qtd:', 1)[0]
        entry_alvo.delete(0, tk.END); entry_alvo.insert(0, nome.strip())
    except: pass

def _pesquisar_cliente(entry_busca, listbox):
    termo = entry_busca.get().strip()
    listbox.delete(0, tk.END)
    conexao = banco.conectar()
    if not conexao: return
    cursor = conexao.cursor()
    try:
        sql = "SELECT id, nome FROM clientes WHERE nome LIKE %s ORDER BY nome ASC"
        cursor.execute(sql, (f"%{termo}%",))
        for row in cursor.fetchall():
            listbox.insert(tk.END, f"[{row[0]}] {row[1]}")
        if listbox.size() == 0: listbox.insert(tk.END, "Nenhum cliente encontrado.")
    finally:
        cursor.close(); conexao.close()

def _selecionar_cliente(event, listbox, entry_id_alvo):
    sel = listbox.curselection()
    if not sel: return
    texto = listbox.get(sel[0])
    if "Nenhum" in texto: return
    try:
        id_c = texto.split('] ', 1)[0].replace('[', '')
        entry_id_alvo.delete(0, tk.END); entry_id_alvo.insert(0, id_c)
    except: pass

# --- FUNÇÃO PARA ABRIR POPUP DE PEDIDOS ---
def pedidos(janela_pai):
    try:
        # Importa corretamente da pasta Modulos_Estoque
        from Modulos_Estoque import pedido 
        pedido.abrir_janela_pedidos(janela_pai) 
    except ImportError:
        messagebox.showerror("Erro", "Módulo 'pedido.py' não encontrado na pasta Modulos_Estoque.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir pedidos:\n{e}")


# =============================================================================
# JANELA PRINCIPAL (AGORA É UM FRAME)
# =============================================================================
def abrir_janela_saida(parent):
    
    # 1. Cria o Frame Principal (ocupa todo o espaço do pai)
    frame_total = tk.Frame(parent, bg="white")
    frame_total.pack(fill="both", expand=True)

    # Título
    tk.Label(frame_total, text="Saída de Estoque (Venda/Baixa)", font=("Arial", 16, "bold"), bg="white", fg="#d9534f").pack(pady=15)

    # 2. Container das 3 Colunas
    container = tk.Frame(frame_total, bg="white")
    container.pack(fill="both", expand=True, padx=10, pady=5)

    # --- LAYOUT EM 3 COLUNAS ---
    # Coluna 1: Formulário | Coluna 2: Busca Produto | Coluna 3: Busca Cliente
    frame_form = tk.Frame(container, bg="#fff5f5", relief="groove", borderwidth=2) # Fundo avermelhado leve
    frame_form.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
    
    frame_prod = tk.Frame(container, bg="white", relief="sunken", borderwidth=1)
    frame_prod.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
    
    frame_cli = tk.Frame(container, bg="white", relief="sunken", borderwidth=1)
    frame_cli.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

    # === COLUNA 1: FORMULÁRIO DE SAÍDA ===
    tk.Label(frame_form, text="DADOS DA SAÍDA", font=("Arial", 11, "bold"), bg="#fff5f5", fg="red").pack(pady=10)
    
    tk.Label(frame_form, text="Produto Selecionado:", bg="#fff5f5").pack(anchor="w", padx=10)
    entry_nome = tk.Entry(frame_form, bg="white"); entry_nome.pack(fill="x", padx=10, pady=2)
    
    tk.Label(frame_form, text="ID Cliente:", bg="#fff5f5").pack(anchor="w", padx=10)
    entry_cliente_id = tk.Entry(frame_form, bg="white"); entry_cliente_id.pack(fill="x", padx=10, pady=2)
    
    tk.Label(frame_form, text="Quantidade a Remover:", bg="#fff5f5").pack(anchor="w", padx=10)
    entry_qntd = tk.Entry(frame_form, bg="white"); entry_qntd.pack(fill="x", padx=10, pady=2)
    
    btn_confirmar = tk.Button(frame_form, text="CONFIRMAR SAÍDA", bg="#ffcccc", fg="red", font=("Arial", 10, "bold"),
                              command=lambda: _remover_stock_logic(log_text, entry_nome, entry_qntd, entry_cliente_id))
    btn_confirmar.pack(fill="x", padx=10, pady=20)

    # Botão Pedido CSV (Chama o popup)
    # Importante: Passamos 'parent' como master para o popup
    btn_pedido_csv = tk.Button(frame_form, text="📂 Importar Pedido (CSV)", bg="#fff0e0", fg="orange", font=("Arial", 9, "bold"),
                               command=lambda: pedidos(parent))
    btn_pedido_csv.pack(fill="x", padx=10, pady=(0,10))
    
    # Log
    tk.Label(frame_form, text="Log da Operação:", bg="#fff5f5").pack(anchor="w", padx=10)
    log_text = tk.Text(frame_form, height=10, width=30, state=tk.DISABLED)
    log_text.pack(fill="both", expand=True, padx=10, pady=5)


    # === COLUNA 2: BUSCA PRODUTO ===
    tk.Label(frame_prod, text="🔍 Buscar Produto", font=("Arial", 10, "bold"), bg="white").pack(pady=5)
    entry_busca_prod = tk.Entry(frame_prod)
    entry_busca_prod.pack(fill="x", padx=5)
    
    list_prod = tk.Listbox(frame_prod, height=25)
    list_prod.pack(fill="both", expand=True, padx=5, pady=5)
    
    entry_busca_prod.bind('<Return>', lambda e: _pesquisar_produto(entry_busca_prod, list_prod))
    tk.Button(frame_prod, text="Pesquisar", command=lambda: _pesquisar_produto(entry_busca_prod, list_prod)).pack(fill="x", padx=5)
    list_prod.bind('<<ListboxSelect>>', lambda e: _selecionar_produto(e, list_prod, entry_nome))
    
    _pesquisar_produto(entry_busca_prod, list_prod) # Init


    # === COLUNA 3: BUSCA CLIENTE ===
    tk.Label(frame_cli, text="👤 Buscar Cliente", font=("Arial", 10, "bold"), bg="white").pack(pady=5)
    entry_busca_cli = tk.Entry(frame_cli)
    entry_busca_cli.pack(fill="x", padx=5)
    
    list_cli = tk.Listbox(frame_cli, height=25)
    list_cli.pack(fill="both", expand=True, padx=5, pady=5)
    
    entry_busca_cli.bind('<Return>', lambda e: _pesquisar_cliente(entry_busca_cli, list_cli))
    tk.Button(frame_cli, text="Pesquisar", command=lambda: _pesquisar_cliente(entry_busca_cli, list_cli)).pack(fill="x", padx=5)
    list_cli.bind('<<ListboxSelect>>', lambda e: _selecionar_cliente(e, list_cli, entry_cliente_id))

    _pesquisar_cliente(entry_busca_cli, list_cli) # Init