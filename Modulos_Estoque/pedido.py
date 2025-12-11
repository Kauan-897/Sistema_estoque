import tkinter as tk
from tkinter import filedialog, messagebox
import banco
import csv
from decimal import Decimal, InvalidOperation

# =============================================================================
# 1. FUNÇÃO PARA ABRIR E VALIDAR O CSV
# =============================================================================
def abrir_pedido_csv(janela_pai, memo_widget, botoes_frame, itens_pedido):
    
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    memo_widget.insert(tk.END, "Iniciando leitura do CSV...\n")
    itens_pedido.clear()  
    botoes_frame.pack_forget() 
    
    conexao = None
    cursor = None
    
    try:
        caminho_arquivo = filedialog.askopenfilename(
            parent=janela_pai, 
            title="Selecione o arquivo CSV de Pedido",
            filetypes=[("Arquivos CSV", "*.csv")]
        )

        if not caminho_arquivo:
            memo_widget.insert(tk.END, "Leitura cancelada.\n")
            memo_widget.config(state=tk.DISABLED)
            return

        conexao = banco.conectar()
        if not conexao:
             memo_widget.insert(tk.END, "ERRO: Sem conexão com MySQL.")
             memo_widget.config(state=tk.DISABLED)
             return
        
        cursor = conexao.cursor(buffered=True)
        usuario_id_atual = 1 

        with open(caminho_arquivo, "r", encoding="latin-1") as arquivo:
            leitor = csv.reader(arquivo, delimiter=';')
            
            # 1. Lê a Linha do Cliente (Linha 1)
            linha_cliente = next(leitor, None)
            if not linha_cliente or len(linha_cliente) < 2:
                raise Exception("Formato inválido (Linha 1 deve ter o Cliente).")
            
            cliente_nome = linha_cliente[1].strip()
            
            # Valida Cliente
            cursor.execute("SELECT id FROM clientes WHERE nome = %s", (cliente_nome,))
            res_cliente = cursor.fetchone()
            
            if not res_cliente:
                memo_widget.insert(tk.END, f"\n--- ERRO GRAVE ---\nCliente '{cliente_nome}' não encontrado.\n")
                raise Exception("Cliente não cadastrado")
                
            cliente_id = res_cliente[0]
            memo_widget.insert(tk.END, f"Cliente: {cliente_nome} (ID: {cliente_id})\n")
            
            # 2. Pula a Linha de Cabeçalho dos Itens
            next(leitor, None) 
            
            memo_widget.insert(tk.END, "-"*40 + "\nVerificando itens...\n")

            itens_encontrados = 0
            itens_invalidos = 0
            
            # 3. Lê os Produtos
            for linha in leitor:
                if not linha or len(linha) < 3: continue
                
                produto_nome = linha[1].strip()
                quantidade_str = linha[2].strip().replace(',', '.')
                
                if not produto_nome: continue

                try:
                    quantidade = Decimal(quantidade_str)
                    if quantidade <= 0: continue 

                    cursor.execute("SELECT id, quantidade, status FROM estoque WHERE nome = %s", (produto_nome,))
                    res_produto = cursor.fetchone()

                    if not res_produto:
                        memo_widget.insert(tk.END, f" ❌ ERRO: '{produto_nome}' não cadastrado.\n")
                        itens_invalidos += 1
                        continue 

                    estoque_id = res_produto[0]
                    stock_atual = res_produto[1]
                    status_atual = res_produto[2]

                    if status_atual == 'Inativo':
                        memo_widget.insert(tk.END, f" ⛔ BLOQUEADO: '{produto_nome}' está INATIVO.\n")
                        itens_invalidos += 1
                        continue

                    if stock_atual < quantidade:
                        memo_widget.insert(tk.END, f" ⚠️ FALTA ESTOQUE: '{produto_nome}'.\n")
                        memo_widget.insert(tk.END, f"    (Pedido: {quantidade} / Disp: {stock_atual})\n")
                        itens_invalidos += 1
                        continue 
                    
                    memo_widget.insert(tk.END, f" ✅ OK: {produto_nome} (Qtd: {quantidade})\n")
                    itens_pedido.append({
                        'estoque_id': estoque_id,
                        'quantidade': quantidade,
                        'cliente_id': cliente_id,
                        'usuario_id': usuario_id_atual,
                        'nome_produto': produto_nome
                    })
                    itens_encontrados += 1
                        
                except (ValueError, InvalidOperation):
                    pass 

            memo_widget.insert(tk.END, "-"*40 + "\n")
            
            if itens_encontrados > 0 and itens_invalidos == 0:
                memo_widget.insert(tk.END, f"\nSUCESSO: {itens_encontrados} itens validados.\n")
                botoes_frame.pack() 
            elif itens_encontrados > 0:
                memo_widget.insert(tk.END, f"\nATENÇÃO: {itens_invalidos} itens falharam.\n")
                messagebox.showwarning("Aviso", "Alguns itens falharam. Verifique o log.", parent=janela_pai)
            else:
                memo_widget.insert(tk.END, "\nNenhum item válido encontrado.")
                messagebox.showerror("Erro", "Falha total na validação.", parent=janela_pai)

    except Exception as e:
        memo_widget.insert(tk.END, f"\nERRO TÉCNICO: {e}")
        messagebox.showerror("Erro Crítico", f"{e}", parent=janela_pai)
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()
        memo_widget.config(state=tk.DISABLED)

# =============================================================================
# 2. FUNÇÃO PARA REGISTRAR SAÍDA
# =============================================================================
def registrar_saida(itens_pedido, memo_widget, botoes_frame):
    if not itens_pedido: return

    conexao = None
    try:
        conexao = banco.conectar()
        if not conexao: return
        cursor = conexao.cursor()
        
        memo_widget.config(state=tk.NORMAL)
        memo_widget.insert(tk.END, "\n>>> Processando Saída no Banco... <<<\n")
        
        for item in itens_pedido:
            cursor.execute("UPDATE estoque SET quantidade = quantidade - %s WHERE id = %s", 
                          (item['quantidade'], item['estoque_id']))
            
            cursor.execute("""
                INSERT INTO saidas (estoque_id, cliente_id, usuario_id, Quantidade)
                VALUES (%s, %s, %s, %s)
            """, (item['estoque_id'], item['cliente_id'], item['usuario_id'], item['quantidade']))
            
            memo_widget.insert(tk.END, f" .. Baixado: {item['nome_produto']}\n")
        
        conexao.commit()
        
        messagebox.showinfo("Sucesso", "Saída registrada e estoque atualizado!")
        memo_widget.insert(tk.END, "\n✔️ OPERAÇÃO CONCLUÍDA COM SUCESSO!\n")
        
        itens_pedido.clear()
        botoes_frame.pack_forget() 

    except Exception as e:
        if conexao: conexao.rollback()
        messagebox.showerror("Erro de Banco", f"{e}")
        memo_widget.insert(tk.END, f"\nERRO GRAVE AO SALVAR: {e}\n")
    finally:
        if conexao: conexao.close()
        memo_widget.config(state=tk.DISABLED)


def cancelar_pedido(itens_pedido, memo_widget, botoes_frame):
    itens_pedido.clear()
    memo_widget.config(state=tk.NORMAL)
    memo_widget.insert(tk.END, "\n❌ Pedido cancelado.\n")
    memo_widget.config(state=tk.DISABLED)
    botoes_frame.pack_forget() 


# =============================================================================
# 3. JANELA PRINCIPAL (POPUP)
# =============================================================================
def abrir_janela_pedidos(janela_principal):
    janela = tk.Toplevel(janela_principal)
    janela.title("Processamento de Pedidos (CSV)")
    janela.geometry("700x650")
    janela.transient(janela_principal)
    janela.grab_set()

    itens_pedido = [] 

    # --- Cabeçalho ---
    frame_top = tk.Frame(janela, bg="#f0f0f0", pady=10)
    frame_top.pack(fill="x")
    tk.Label(frame_top, text="Importação de Pedido via CSV", font=("Arial", 14, "bold"), bg="#f0f0f0").pack()
    tk.Label(frame_top, text="Selecione um arquivo .csv para dar baixa automática", bg="#f0f0f0").pack()

    # --- Área Central (Botões) ---
    frame_botoes = tk.Frame(janela, pady=10)
    frame_botoes.pack()

    btn_csv = tk.Button(frame_botoes, text="📂 1. Selecionar Arquivo CSV", font=("Arial", 11), bg="#e1f5fe",
                        command=lambda: abrir_pedido_csv(janela, memo_text, botoes_acao, itens_pedido))
    btn_csv.pack(side=tk.LEFT, padx=10, ipady=5)

    # --- Área de Log (Memo) ---
    frame_log = tk.Frame(janela, padx=20, pady=10)
    frame_log.pack(fill="both", expand=True)
    
    tk.Label(frame_log, text="Relatório de Validação:", anchor="w").pack(fill="x")
    
    scroll = tk.Scrollbar(frame_log)
    scroll.pack(side=tk.RIGHT, fill="y")
    
    memo_text = tk.Text(frame_log, height=15, font=("Consolas", 10), state=tk.DISABLED, yscrollcommand=scroll.set)
    memo_text.pack(side=tk.LEFT, fill="both", expand=True)
    scroll.config(command=memo_text.yview)

    # --- Botões de Ação (Começam Escondidos) ---
    botoes_acao = tk.Frame(janela, pady=10)
    botoes_acao.pack()
    
    btn_confirmar = tk.Button(botoes_acao, text="✅ CONFIRMAR SAÍDA", bg="#ccffcc", fg="green", font=("Arial", 12, "bold"),
                              command=lambda: registrar_saida(itens_pedido, memo_text, botoes_acao))
    btn_confirmar.pack(side=tk.LEFT, padx=10)
    
    btn_cancelar = tk.Button(botoes_acao, text="❌ Cancelar", bg="#ffcccc", font=("Arial", 10),
                             command=lambda: cancelar_pedido(itens_pedido, memo_text, botoes_acao))
    btn_cancelar.pack(side=tk.LEFT, padx=10)
    
    botoes_acao.pack_forget() 

    # --- Botão Fechar (SEMPRE VISÍVEL NO RODAPÉ) ---
    tk.Button(janela, text="Fechar Janela", command=janela.destroy).pack(side="bottom", pady=10)

    janela.wait_window()