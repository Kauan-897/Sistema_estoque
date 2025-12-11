import tkinter as tk
from tkinter import filedialog, messagebox
import banco
import csv

# =============================================================================
# 1. FUNÇÃO: GERAR MODELO (TEMPLATE)
# =============================================================================
def _gerar_modelo_csv():
    """Gera uma planilha CSV vazia com os cabeçalhos corretos para o usuário preencher."""
    caminho = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("Arquivos CSV", "*.csv")],
        initialfile="modelo_importacao_estoque.csv",
        title="Salvar Modelo de Importação"
    )
    
    if not caminho: return

    try:
        with open(caminho, mode='w', newline='', encoding='utf-8-sig') as file: # utf-8-sig para Excel abrir com acentos
            writer = csv.writer(file, delimiter=';')
            
            # 1. Cabeçalho
            writer.writerow(["Codigo", "Nome do Produto", "Quantidade Inicial", "Estoque Minimo", "Preco Custo", "Preco Venda"])
            
            # 2. Exemplo (Opcional, para ajudar o usuário)
            writer.writerow(["COD001", "Exemplo: Parafuso Inox", "100", "10", "0,50", "1,20"])
            
        messagebox.showinfo("Sucesso", "Modelo gerado com sucesso!\nPreencha este arquivo e use na importação.")
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao criar modelo: {e}")

# =============================================================================
# 2. FUNÇÃO: IMPORTAR O CSV COMPLETO
# =============================================================================
def _cadastrar_itens_logic(janela_pai, memo_widget):
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    memo_widget.insert(tk.END, "Iniciando cadastro via CSV...\n")
    
    conexao = None
    cursor = None 
    itens_cadastrados = 0
    itens_ignorados = 0
    
    try:
        caminho_arquivo = filedialog.askopenfilename(
            parent=janela_pai, 
            title="Selecione a Planilha de Importação",
            filetypes=[("Arquivos CSV", "*.csv")]
        )
        if not caminho_arquivo:
            memo_widget.insert(tk.END, "Cadastro cancelado.")
            memo_widget.config(state=tk.DISABLED)
            return
            
        conexao = banco.conectar()
        if not conexao:
             memo_widget.insert(tk.END, "ERRO: Sem conexão com MySQL.")
             memo_widget.config(state=tk.DISABLED)
             return
        cursor = conexao.cursor()

        # Tenta ler (utf-8-sig é melhor para acentos, mas latin-1 é fallback)
        try:
            arquivo = open(caminho_arquivo, "r", encoding="utf-8-sig")
        except:
            arquivo = open(caminho_arquivo, "r", encoding="latin-1")

        with arquivo:
            leitor = csv.reader(arquivo, delimiter=';')
            
            # Pula o cabeçalho (Linha 1)
            cabecalho = next(leitor, None)
            
            memo_widget.insert(tk.END, "Lendo arquivo...\n-----------------\n")

            for linha in leitor:
                # Valida se a linha tem colunas suficientes (esperamos 6)
                if not linha or len(linha) < 2: continue
                
                # Mapeamento das colunas (Baseado no nosso modelo)
                # 0:Codigo, 1:Nome, 2:Qtd, 3:Min, 4:Custo, 5:Venda
                
                # Tratamento de dados seguro
                try:
                    raw_cod = linha[0].strip()
                    produto_codigo = raw_cod if raw_cod else None # Se vazio, vira None
                    
                    produto_nome = linha[1].strip()
                    if not produto_nome: continue # Sem nome, pula
                    
                    # Funções auxiliares para limpar números
                    def to_float(val): return float(val.replace(',', '.')) if val.strip() else 0.0
                    def to_int(val): return int(val) if val.strip() else 5 # Padrão 5 se vazio

                    qtd = to_float(linha[2]) if len(linha) > 2 else 0.0
                    mini = to_int(linha[3])  if len(linha) > 3 else 5
                    custo = to_float(linha[4]) if len(linha) > 4 else 0.0
                    venda = to_float(linha[5]) if len(linha) > 5 else 0.0

                except ValueError:
                    memo_widget.insert(tk.END, f" -> Erro de formato em '{produto_nome}'\n")
                    continue

                # 1. Verifica duplicidade de NOME
                cursor.execute("SELECT id FROM estoque WHERE nome = %s", (produto_nome,))
                if cursor.fetchone():
                    memo_widget.insert(tk.END, f" -> Ignorado: '{produto_nome}' (Nome existe)\n")
                    itens_ignorados += 1
                    continue
                
                # 2. Verifica duplicidade de CÓDIGO (se fornecido)
                if produto_codigo:
                    cursor.execute("SELECT id FROM estoque WHERE codigo = %s", (produto_codigo,))
                    if cursor.fetchone():
                        memo_widget.insert(tk.END, f" -> Ignorado: '{produto_nome}' (Cód {produto_codigo} existe)\n")
                        itens_ignorados += 1
                        continue

                # 3. Cadastra Completo
                memo_widget.insert(tk.END, f" -> Cadastrando: {produto_nome}...")
                
                cursor.execute("""
                    INSERT INTO estoque (codigo, nome, quantidade, estoque_minimo, preco_custo, preco_venda)
                    VALUES (%s, %s, %s, %s, %s, %s) 
                """, (produto_codigo, produto_nome, qtd, mini, custo, venda))
                
                memo_widget.insert(tk.END, " OK\n")
                itens_cadastrados += 1

            if itens_cadastrados > 0:
                conexao.commit()
                memo_widget.insert(tk.END, f"\nSUCESSO: {itens_cadastrados} cadastrados.")
                messagebox.showinfo("Sucesso", f"{itens_cadastrados} itens importados com sucesso!", parent=janela_pai)
            else:
                memo_widget.insert(tk.END, "\nNenhum item novo cadastrado.")

    except Exception as e:
        if conexao: conexao.rollback()
        memo_widget.insert(tk.END, f"\nERRO CRÍTICO: {e}")
        messagebox.showerror("Erro", f"Falha na importação: {e}", parent=janela_pai)
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()
        memo_widget.config(state=tk.DISABLED)
        
def _cadastrar_manual_logic(memo_widget, e_cod, e_nome, e_qtd, e_min, e_custo, e_venda):
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    
    codigo = e_cod.get().strip()
    nome = e_nome.get().strip()
    
    if not nome:
        messagebox.showwarning("Aviso", "Nome é obrigatório.")
        return
        
    try:
        qtd = float(e_qtd.get().replace(',', '.')) if e_qtd.get() else 0.0
        mini = int(e_min.get()) if e_min.get() else 5
        custo = float(e_custo.get().replace(',', '.')) if e_custo.get() else 0.0
        venda = float(e_venda.get().replace(',', '.')) if e_venda.get() else 0.0
        
        if qtd < 0 or mini < 0 or custo < 0 or venda < 0: raise ValueError
    except ValueError:
        memo_widget.insert(tk.END, "ERRO: Valores numéricos inválidos.")
        memo_widget.config(state=tk.DISABLED)
        return
    
    conexao = banco.conectar()
    if not conexao: return
    cursor = conexao.cursor()
    
    try:
        cursor.execute("SELECT id FROM estoque WHERE nome = %s", (nome,))
        if cursor.fetchone():
            memo_widget.insert(tk.END, f"ERRO: '{nome}' já existe.\n")
        else:
            if codigo:
                cursor.execute("SELECT id FROM estoque WHERE codigo = %s", (codigo,))
                if cursor.fetchone():
                     memo_widget.insert(tk.END, f"ERRO: Código '{codigo}' em uso.\n")
                     return
            
            cursor.execute("""
                INSERT INTO estoque (codigo, nome, quantidade, estoque_minimo, preco_custo, preco_venda)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (codigo, nome, qtd, mini, custo, venda))
            
            conexao.commit()
            memo_widget.insert(tk.END, "\nSUCESSO: Item cadastrado!")
            
            e_cod.delete(0, tk.END); e_nome.delete(0, tk.END)
            e_qtd.delete(0, tk.END); e_min.delete(0, tk.END)
            e_custo.delete(0, tk.END); e_venda.delete(0, tk.END)
            
    except Exception as e:
        conexao.rollback()
        memo_widget.insert(tk.END, f"\nERRO: {e}")
    finally:
        cursor.close(); conexao.close()
        memo_widget.config(state=tk.DISABLED)


# =============================================================================
# JANELA PRINCIPAL (AGORA É UM FRAME)
# =============================================================================
def abrir_janela_cadastro(parent):
    frame_total = tk.Frame(parent, bg="white")
    frame_total.pack(fill="both", expand=True)

    tk.Label(frame_total, text="Cadastro de Produtos", font=("Arial", 16, "bold"), bg="white", fg="#444").pack(pady=15)

    container = tk.Frame(frame_total, bg="white")
    container.pack(fill="both", expand=True, padx=20, pady=10)

    # --- ESQUERDA: MANUAL ---
    frame_manual = tk.Frame(container, bg="#f0f0f0", relief="groove", borderwidth=1)
    frame_manual.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)

    tk.Label(frame_manual, text="Cadastro Manual", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=10)

    # Grid Manual
    grid_frame = tk.Frame(frame_manual, bg="#f0f0f0")
    grid_frame.pack(fill="x", padx=10)

    tk.Label(grid_frame, text="Código:", bg="#f0f0f0").grid(row=0, column=0, sticky="e", pady=5)
    e_cod = tk.Entry(grid_frame, width=15)
    e_cod.grid(row=0, column=1, sticky="w", pady=5)

    tk.Label(grid_frame, text="Nome:", bg="#f0f0f0").grid(row=1, column=0, sticky="e", pady=5)
    e_nome = tk.Entry(grid_frame, width=30)
    e_nome.grid(row=1, column=1, sticky="w", pady=5)

    tk.Label(grid_frame, text="Qtd Inicial:", bg="#f0f0f0").grid(row=2, column=0, sticky="e", pady=5)
    e_qtd = tk.Entry(grid_frame, width=10)
    e_qtd.grid(row=2, column=1, sticky="w", pady=5)

    tk.Label(grid_frame, text="Estoque Mín:", bg="#f0f0f0").grid(row=3, column=0, sticky="e", pady=5)
    e_min = tk.Entry(grid_frame, width=10)
    e_min.grid(row=3, column=1, sticky="w", pady=5)

    tk.Label(grid_frame, text="Preço Custo (R$):", bg="#f0f0f0").grid(row=4, column=0, sticky="e", pady=5)
    e_custo = tk.Entry(grid_frame, width=10)
    e_custo.grid(row=4, column=1, sticky="w", pady=5)

    tk.Label(grid_frame, text="Preço Venda (R$):", bg="#f0f0f0").grid(row=5, column=0, sticky="e", pady=5)
    e_venda = tk.Entry(grid_frame, width=10)
    e_venda.grid(row=5, column=1, sticky="w", pady=5)

    tk.Button(frame_manual, text="Salvar Item", bg="#007bff", fg="white", font=("Arial", 10, "bold"),
              command=lambda: _cadastrar_manual_logic(log_text, e_cod, e_nome, e_qtd, e_min, e_custo, e_venda)).pack(pady=20, fill="x", padx=20)

    # --- DIREITA: CSV ---
    frame_direita = tk.Frame(container, bg="white")
    frame_direita.pack(side=tk.RIGHT, fill="both", expand=True, padx=10, pady=10)

    frame_csv = tk.Frame(frame_direita, bg="#e8f5e9", relief="groove", borderwidth=1)
    frame_csv.pack(fill="x")
    
    tk.Label(frame_csv, text="Importação em Massa (CSV)", font=("Arial", 12, "bold"), bg="#e8f5e9").pack(pady=10)
    
    # Botão de BAIXAR O MODELO (NOVO!)
    tk.Button(frame_csv, text="⬇️ Baixar Planilha Modelo", bg="white", fg="#333",
              command=_gerar_modelo_csv).pack(pady=(0,5), padx=20, fill="x")

    # Botão de IMPORTAR
    tk.Button(frame_csv, text="📂 Importar Planilha Preenchida", bg="#28a745", fg="white", font=("Arial", 10, "bold"),
              command=lambda: _cadastrar_itens_logic(parent, log_text)).pack(pady=(5,10), padx=20, fill="x")

    tk.Label(frame_direita, text="Log de Operações:", bg="white", font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,0))
    
    log_scrollbar = tk.Scrollbar(frame_direita)
    log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    log_text = tk.Text(frame_direita, height=12, width=40, font=("Consolas", 9), state=tk.DISABLED, yscrollcommand=log_scrollbar.set)
    log_text.pack(side=tk.LEFT, fill="both", expand=True)
    log_scrollbar.config(command=log_text.yview)
    
    log_text.insert(tk.END, "Dica: Baixe o modelo antes de importar.")
    log_text.config(state=tk.DISABLED)