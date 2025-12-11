import tkinter as tk
from tkinter import messagebox, filedialog
import banco      
import csv
from decimal import Decimal, InvalidOperation

# =============================================================================
# LÓGICA DE NEGÓCIO (Mantida igual, só copiando)
# =============================================================================

def _adicionar_stock_logic(memo_widget, entry_input, entry_qntd):
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    
    termo_busca = entry_input.get().strip()
    qntd_str = entry_qntd.get().strip().replace(',', '.')
    
    if not termo_busca:
        memo_widget.insert(tk.END, "ERRO: O campo 'Nome/Código' não pode estar vazio.")
        memo_widget.config(state=tk.DISABLED)
        return
        
    try:
        quantidade = Decimal(qntd_str)
        if quantidade <= 0: raise ValueError
    except (ValueError, InvalidOperation):
        memo_widget.insert(tk.END, f"ERRO: Quantidade inválida.\n")
        memo_widget.config(state=tk.DISABLED)
        return
    
    conexao = None
    cursor = None
    try:
        conexao = banco.conectar()
        if not conexao:
             memo_widget.insert(tk.END, "ERRO: Sem conexão com MySQL.")
             return
        
        cursor = conexao.cursor(buffered=True)
        memo_widget.insert(tk.END, f"Procurando por: '{termo_busca}'...\n")

        produto_encontrado = None
        cursor.execute("SELECT id, nome, quantidade FROM estoque WHERE codigo = %s", (termo_busca,))
        produto_encontrado = cursor.fetchone()

        if not produto_encontrado:
            cursor.execute("SELECT id, nome, quantidade FROM estoque WHERE nome = %s", (termo_busca,))
            produto_encontrado = cursor.fetchone()
        
        if not produto_encontrado:
            memo_widget.insert(tk.END, f"ERRO: Item não encontrado no banco.\n")
        else:
            prod_id = produto_encontrado[0]
            prod_nome = produto_encontrado[1]
            stock_antigo = produto_encontrado[2]
            stock_novo = stock_antigo + quantidade
            
            cursor.execute("UPDATE estoque SET quantidade = quantidade + %s WHERE id = %s", (quantidade, prod_id))
            conexao.commit()
            
            memo_widget.insert(tk.END, f"SUCESSO: '{prod_nome}' atualizado!\n")
            memo_widget.insert(tk.END, f"  Estoque: {stock_antigo} -> {stock_novo}")
            entry_qntd.delete(0, tk.END)
            
    except Exception as e:
        if conexao: conexao.rollback()
        memo_widget.insert(tk.END, f"\nERRO TÉCNICO: {e}") 
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()
        memo_widget.config(state=tk.DISABLED)

def _entrada_csv_logic(janela_pai, memo_widget):
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    memo_widget.insert(tk.END, "Iniciando entrada via CSV...\n")
    
    conexao = None
    cursor = None 
    itens_atualizados = 0
    
    try:
        caminho_arquivo = filedialog.askopenfilename(
            parent=janela_pai, 
            title="Selecione CSV (Código; Nome; Qtd)",
            filetypes=[("Arquivos CSV", "*.csv")]
        )
        if not caminho_arquivo:
            memo_widget.insert(tk.END, "Operação cancelada.")
            memo_widget.config(state=tk.DISABLED)
            return
            
        conexao = banco.conectar()
        if not conexao:
             memo_widget.insert(tk.END, "ERRO: Sem conexão com MySQL.")
             memo_widget.config(state=tk.DISABLED)
             return
        
        cursor = conexao.cursor(buffered=True)

        with open(caminho_arquivo, "r", encoding="latin-1") as arquivo:
            leitor = csv.reader(arquivo, delimiter=';')
            next(leitor, None) 
            
            memo_widget.insert(tk.END, "Processando arquivo...\n-----------------\n")

            for linha in leitor:
                if not linha or len(linha) < 3: continue
                
                csv_codigo = linha[0].strip()
                csv_nome = linha[1].strip()
                qntd_str = linha[2].strip().replace(',', '.')
                
                try:
                    quantidade = Decimal(qntd_str)
                    if quantidade <= 0: continue
                except (ValueError, InvalidOperation):
                    continue 

                prod_id = None
                prod_nome_banco = None
                
                if csv_codigo:
                    cursor.execute("SELECT id, nome FROM estoque WHERE codigo = %s", (csv_codigo,))
                    res = cursor.fetchone()
                    if res:
                        prod_id = res[0]
                        prod_nome_banco = res[1]

                if not prod_id and csv_nome:
                    cursor.execute("SELECT id, nome FROM estoque WHERE nome = %s", (csv_nome,))
                    res = cursor.fetchone()
                    if res:
                        prod_id = res[0]
                        prod_nome_banco = res[1]

                if prod_id:
                    cursor.execute("UPDATE estoque SET quantidade = quantidade + %s WHERE id = %s", (quantidade, prod_id))
                    memo_widget.insert(tk.END, f" -> +{quantidade} em '{prod_nome_banco}'\n")
                    itens_atualizados += 1
                else:
                    memo_widget.insert(tk.END, f" -> Ignorado: '{csv_nome}' (Não encontrado)\n")

            if itens_atualizados > 0:
                conexao.commit()
                memo_widget.insert(tk.END, f"\nSUCESSO: {itens_atualizados} itens atualizados.")
                messagebox.showinfo("Sucesso", "Entrada em massa concluída!", parent=janela_pai)
            else:
                memo_widget.insert(tk.END, "\nNenhum item atualizado.")

    except Exception as e:
        if conexao: conexao.rollback()
        memo_widget.insert(tk.END, f"\nERRO: {e}")
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}", parent=janela_pai)
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()
        memo_widget.config(state=tk.DISABLED)

def _pesquisar_produto_logic(entry_busca, listbox_resultados):
    termo = entry_busca.get().strip()
    listbox_resultados.delete(0, tk.END)
    
    conexao = None
    cursor = None
    try:
        conexao = banco.conectar()
        if not conexao: return
        cursor = conexao.cursor(buffered=True)
        
        sql = "SELECT codigo, nome, quantidade FROM estoque WHERE nome LIKE %s OR codigo LIKE %s ORDER BY nome ASC"
        termo_like = f"%{termo}%"
        cursor.execute(sql, (termo_like, termo_like))
        resultados = cursor.fetchall()
        
        if resultados:
            for row in resultados:
                cod = row[0] if row[0] else "---"
                texto_display = f"[{cod}] {row[1]} (Atual: {row[2]})"
                listbox_resultados.insert(tk.END, texto_display)
        else:
            listbox_resultados.insert(tk.END, "Nenhum produto encontrado.")
            
    except Exception as e:
        messagebox.showerror("Erro", f"Erro na pesquisa: {e}")
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()

def _selecionar_produto_evento(event, listbox_resultados, entry_nome):
    selecao = listbox_resultados.curselection()
    if not selecao: return
    texto = listbox_resultados.get(selecao[0])
    if texto == "Nenhum produto encontrado.": return

    try:
        parte1 = texto.split('] ', 1)[1] 
        nome_real = parte1.split(' (Atual:', 1)[0]
        entry_nome.delete(0, tk.END)
        entry_nome.insert(0, nome_real.strip())
    except IndexError:
        pass 


# =============================================================================
# JANELA PRINCIPAL (AGORA É UM FRAME)
# =============================================================================
def abrir_janela_entrada(parent):
    # Cria o frame principal que ocupará a área branca do menu
    frame_total = tk.Frame(parent, bg="white")
    frame_total.pack(fill="both", expand=True)

    # Título
    tk.Label(frame_total, text="Entrada de Estoque", font=("Arial", 16, "bold"), bg="white", fg="#28a745").pack(pady=15)

    # Layout
    frame_esquerda = tk.Frame(frame_total, bg="white")
    frame_esquerda.pack(side=tk.LEFT, fill="both", expand=True, padx=20, pady=10)
    
    frame_direita = tk.Frame(frame_total, bg="#f9f9f9", relief="groove", borderwidth=2)
    frame_direita.pack(side=tk.RIGHT, fill="y", padx=20, pady=10, ipadx=10)

    # --- LADO ESQUERDO: MANUAL E CSV ---
    
    # Bloco Manual
    frame_manual = tk.Frame(frame_esquerda, bg="#f0fff4", relief="groove", borderwidth=1)
    frame_manual.pack(fill="x", pady=10, ipady=10)

    tk.Label(frame_manual, text="Entrada Manual", font=("Arial", 12, "bold"), bg="#f0fff4", fg="#28a745").pack(pady=5)
    
    tk.Label(frame_manual, text="Nome ou Código do Item:", bg="#f0fff4").pack(anchor="w", padx=10)
    entry_nome = tk.Entry(frame_manual, width=40, bg="white") 
    entry_nome.pack(padx=10, pady=2, fill="x")

    tk.Label(frame_manual, text="Quantidade a Adicionar:", bg="#f0fff4").pack(anchor="w", padx=10)
    entry_qntd = tk.Entry(frame_manual, width=15, bg="white")
    entry_qntd.pack(padx=10, pady=2, anchor="w") 

    btn_adicionar = tk.Button(frame_manual, text="CONFIRMAR ENTRADA", bg="#28a745", fg="white", font=("Arial", 10, "bold"),
                             command=lambda: _adicionar_stock_logic(log_text, entry_nome, entry_qntd))
    btn_adicionar.pack(pady=10, fill="x", padx=10)
    
    # Bloco CSV
    frame_csv = tk.Frame(frame_esquerda, bg="white", relief="groove", borderwidth=1)
    frame_csv.pack(fill="x", pady=10, ipady=5)
    
    tk.Label(frame_csv, text="Entrada em Massa (CSV)", font=("Arial", 11, "bold"), bg="white").pack(pady=5)
    btn_csv = tk.Button(frame_csv, text="📂 Selecionar Arquivo CSV", bg="#e8f5e9",
                        command=lambda: _entrada_csv_logic(parent, log_text))
    btn_csv.pack(padx=10, pady=5, fill='x')

    # Log Area
    frame_log = tk.Frame(frame_esquerda, bg="white")
    frame_log.pack(fill="both", expand=True)
    tk.Label(frame_log, text="Log de Operações:", bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
    
    log_scrollbar = tk.Scrollbar(frame_log)
    log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    log_text = tk.Text(frame_log, height=8, width=40, yscrollcommand=log_scrollbar.set, font=("Consolas", 9))
    log_text.pack(side=tk.LEFT, fill="both", expand=True)
    log_scrollbar.config(command=log_text.yview)
    log_text.insert(tk.END, "Aguardando operação...")
    log_text.config(state=tk.DISABLED) 

    # --- LADO DIREITO: PESQUISA ---
    tk.Label(frame_direita, text="🔍 Pesquisar Produto", font=("Arial", 11, "bold"), bg="#f9f9f9").pack(pady=10)
    
    entry_busca = tk.Entry(frame_direita, font=("Arial", 11))
    entry_busca.pack(fill="x", padx=10, pady=5)
    
    # Lista Resultados
    listbox_frame = tk.Frame(frame_direita)
    listbox_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    scrollbar_lista = tk.Scrollbar(listbox_frame)
    scrollbar_lista.pack(side=tk.RIGHT, fill=tk.Y)
    
    listbox_resultados = tk.Listbox(listbox_frame, width=35, height=20, yscrollcommand=scrollbar_lista.set, font=("Consolas", 10))
    listbox_resultados.pack(side=tk.LEFT, fill="both", expand=True)
    scrollbar_lista.config(command=listbox_resultados.yview)

    # Botão Pesquisar
    btn_pesquisar = tk.Button(frame_direita, text="Pesquisar", bg="#e1f5fe",
                              command=lambda: _pesquisar_produto_logic(entry_busca, listbox_resultados))
    btn_pesquisar.pack(fill="x", padx=10, pady=5)

    # Bindings
    entry_busca.bind('<Return>', lambda event: _pesquisar_produto_logic(entry_busca, listbox_resultados))
    listbox_resultados.bind('<<ListboxSelect>>', 
                            lambda event: _selecionar_produto_evento(event, listbox_resultados, entry_nome))

    # Inicia com lista vazia ou carrega tudo
    _pesquisar_produto_logic(entry_busca, listbox_resultados)