import tkinter as tk
from tkinter import filedialog, messagebox
import banco
import csv
from datetime import date

# --- 1. FUNÇÃO PARA LER O CSV (AGORA VALIDA COM O BANCO) ---
def abrir_pedido_csv(janela_pai, memo_widget, botoes_frame, itens_pedido):
    
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    memo_widget.insert(tk.END, "Iniciando leitura do CSV...\n")
    itens_pedido.clear()  # Limpa lista antiga
    
    # Esconde os botões de ação
    botoes_frame.grid_remove() 
    
    conexao = None
    cursor = None
    
    try:
        caminho_arquivo = filedialog.askopenfilename(
            parent=janela_pai, # Adicionado
            title="Selecione o arquivo CSV",
            filetypes=[("Arquivos CSV", "*.csv")]
        )

        if not caminho_arquivo:
            memo_widget.insert(tk.END, "Leitura cancelada pelo usuário.")
            memo_widget.config(state=tk.DISABLED)
            return

        # --- MUDANÇA 2: Conexão com MySQL ---
        conexao = banco.conectar()
        if not conexao:
             memo_widget.insert(tk.END, "ERRO: Não foi possível conectar ao banco de dados MySQL.")
             memo_widget.config(state=tk.DISABLED)
             return
        cursor = conexao.cursor()
        
        # ID do usuário (quando tivermos login, isto virá de lá)
        usuario_id_atual = 1 # "Fingindo" ser o Admin

        with open(caminho_arquivo, "r", encoding="latin-1") as arquivo: # Mudado para latin-1
            leitor = csv.reader(arquivo, delimiter=';')
            
            # --- VALIDAÇÃO DO CLIENTE ---
            linha_cliente = next(leitor, None)
            if not linha_cliente or len(linha_cliente) < 2:
                raise Exception("Arquivo CSV vazio ou formato inválido.")
            
            cliente_nome = linha_cliente[1].strip()
            
            # Procura o ID do cliente no banco
            cursor.execute("SELECT id FROM clientes WHERE nome = %s", (cliente_nome,))
            res_cliente = cursor.fetchone()
            
            if not res_cliente:
                memo_widget.insert(tk.END, f"\n--- ERRO GRAVE ---\nCliente '{cliente_nome}' não encontrado no banco.\n")
                memo_widget.insert(tk.END, "Cadastre o cliente primeiro ou corrija o nome no CSV.")
                raise Exception("Cliente não cadastrado")
                
            cliente_id = res_cliente[0]
            memo_widget.insert(tk.END, f"Cliente: {cliente_nome} (ID: {cliente_id})\n")
            memo_widget.insert(tk.END, "-------------------------------------\n")
            memo_widget.insert(tk.END, "Verificando itens e stock...\n")

            itens_encontrados = 0
            itens_invalidos = 0
            
            # --- VALIDAÇÃO DOS PRODUTOS ---
            for linha in leitor:
                if not linha or not linha[0] or len(linha) < 2:
                    continue
                
                produto_nome = linha[0].strip()
                quantidade_str = linha[1].strip().replace(',', '.')
                
                try:
                    quantidade = float(quantidade_str)
                    if quantidade <= 0:
                        continue # Ignora itens com 0 ou menos

                    # Procura o ID e o stock do produto
                    cursor.execute("SELECT id, quantidade FROM estoque WHERE nome = %s", (produto_nome,))
                    res_produto = cursor.fetchone()

                    if not res_produto:
                        memo_widget.insert(tk.END, f"  -> ERRO: Produto '{produto_nome}' não cadastrado.\n")
                        itens_invalidos += 1
                        continue # Próximo item

                    estoque_id = res_produto[0]
                    stock_atual = res_produto[1]

                    if stock_atual < quantidade:
                        memo_widget.insert(tk.END, f"  -> ERRO: Stock insuficiente para '{produto_nome}'.\n")
                        memo_widget.insert(tk.END, f"     (Pedido: {quantidade} / Em stock: {stock_atual})\n")
                        itens_invalidos += 1
                        continue # Próximo item
                    
                    # Se passou em tudo, adiciona à lista
                    memo_widget.insert(tk.END, f"  -> OK: {produto_nome} (Qtd: {quantidade})\n")
                    itens_pedido.append({
                        'estoque_id': estoque_id,
                        'quantidade': quantidade,
                        'cliente_id': cliente_id,
                        'usuario_id': usuario_id_atual,
                        'nome_produto': produto_nome # (só para o log)
                    })
                    itens_encontrados += 1
                        
                except ValueError:
                    pass # Ignora linhas com quantidade inválida

            memo_widget.insert(tk.END, "-------------------------------------\n")
            
            if itens_encontrados > 0 and itens_invalidos == 0:
                memo_widget.insert(tk.END, f"SUCESSO: {itens_encontrados} itens validados e prontos para baixa.\n")
                messagebox.showinfo("Sucesso", "Pedido carregado e validado com sucesso!\nClique em 'Cadastrar Saída' para confirmar.", parent=janela_pai)
                botoes_frame.grid() # Mostra os botões de ação
            elif itens_encontrados > 0 and itens_invalidos > 0:
                memo_widget.insert(tk.END, f"ATENÇÃO: {itens_encontrados} itens são válidos, mas {itens_invalidos} falharam.\n")
                memo_widget.insert(tk.END, "O pedido NÃO será processado. Corrija o CSV ou o stock.")
                messagebox.showwarning("Aviso", "Pedido com erros. Alguns itens falharam na validação (ver log).", parent=janela_pai)
            else:
                memo_widget.insert(tk.END, f"Nenhum item válido foi encontrado no pedido.")
                if itens_invalidos > 0:
                    messagebox.showerror("Erro", "Todos os itens do pedido falharam na validação (ver log).", parent=janela_pai)
                else:
                    messagebox.showinfo("Aviso", "Nenhum item com quantidade > 0 encontrado.", parent=janela_pai)

    except Exception as e:
        memo_widget.insert(tk.END, f"\n--- ERRO ---\nOcorreu um erro: {e}")
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}", parent=janela_pai)
        
    finally:
        # --- MUDANÇA 5: Fechar manualmente ---
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
        memo_widget.config(state=tk.DISABLED)


# --- 2. FUNÇÃO PARA REGISTRAR SAÍDA (MUITO MAIS INTELIGENTE) ---
def registrar_saida(itens_pedido, memo_widget, botoes_frame):
    if not itens_pedido:
        messagebox.showwarning("Aviso", "Nenhum pedido carregado.")
        return

    conexao = None
    cursor = None
    try:
        conexao = banco.conectar()
        if not conexao:
             messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados MySQL.")
             return
        cursor = conexao.cursor()
        
        memo_widget.config(state=tk.NORMAL)
        memo_widget.insert(tk.END, "\n--- Confirmando Saída no Banco ---\n")
        
        for item in itens_pedido:
            # 1️⃣ Atualiza estoque
            cursor.execute("""
                UPDATE estoque 
                SET quantidade = quantidade - %s 
                WHERE id = %s
            """, (item['quantidade'], item['estoque_id']))
            
            # 2️⃣ Registra saída
            cursor.execute("""
                INSERT INTO saidas (estoque_id, cliente_id, usuario_id, Quantidade)
                VALUES (%s, %s, %s, %s)
            """, (item['estoque_id'], item['cliente_id'], item['usuario_id'], item['quantidade']))
            
            memo_widget.insert(tk.END, f"  -> Baixado: {item['nome_produto']} (Qtd: {item['quantidade']})\n")
        
        conexao.commit()
        
        messagebox.showinfo("Sucesso", "Saída registrada e estoque atualizado!")
        memo_widget.insert(tk.END, "✔️ Saída registrada com sucesso!\n")
        
        # Limpa e esconde
        itens_pedido.clear()
        botoes_frame.grid_remove() 

    except Exception as e:
        if conexao:
            conexao.rollback()
        messagebox.showerror("Erro", f"Erro ao registrar saída: {e}")
        memo_widget.insert(tk.END, f"\n--- ERRO: {e} ---\nOperação cancelada.\n")
        
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
        memo_widget.config(state=tk.DISABLED)


# --- 3. FUNÇÃO PARA CANCELAR PEDIDO ---
def cancelar_pedido(itens_pedido, memo_widget, botoes_frame):
    itens_pedido.clear()
    memo_widget.config(state=tk.NORMAL)
    memo_widget.insert(tk.END, "\n❌ Pedido cancelado pelo usuário.\n")
    memo_widget.config(state=tk.DISABLED)
    botoes_frame.grid_remove() # Correção: usar .grid_remove()


# --- 4. FUNÇÃO PARA ABRIR JANELA TOPLEVEL ---
def abrir_janela_pedidos(janela_principal):
    janela_pedidos = tk.Toplevel(janela_principal)
    janela_pedidos.title("Pedidos (Baixa de Estoque via CSV)")
    janela_pedidos.geometry("650x600")

    itens_pedido = []  # armazenar itens do pedido atual

    def estoque():
        try:
            import consulta
            consulta.abrir_janela_consulta(janela_pedidos)
        except ModuleNotFoundError:
            messagebox.showerror("Erro", "Arquivo 'consulta.py' não encontrado.", parent=janela_pedidos)
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um problema ao abrir o estoque:\n{e}", parent=janela_pedidos)

    # MENU PRINCIPAL
    menu_label = tk.Label(janela_pedidos, text="Menu", font=("Arial", 12, "bold"))
    menu_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

    # BOTÃO CSV
    btn_csv = tk.Button(
        janela_pedidos,
        text="1. Abrir Pedido CSV",
        # O command será definido depois que o 'botoes_frame' existir
    )
    btn_csv.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

    # CONSULTA ESTOQUE
    btn_consulta = tk.Button(janela_pedidos, text="2. Consultar Estoque", command=estoque)
    btn_consulta.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

    # ÁREA DE LOG (com barra de rolagem)
    memo_label = tk.Label(janela_pedidos, text="Visualização do Pedido (Logs)")
    memo_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
    
    memo_frame = tk.Frame(janela_pedidos)
    memo_frame.grid(row=4, column=0, padx=20, pady=5)
    memo_scrollbar = tk.Scrollbar(memo_frame)
    memo_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    memo_text = tk.Text(memo_frame, height=15, width=70, yscrollcommand=memo_scrollbar.set)
    memo_text.pack(side=tk.LEFT)
    memo_scrollbar.config(command=memo_text.yview)
    memo_text.insert(tk.END, "Aguarde a seleção de um arquivo CSV...")
    memo_text.config(state=tk.DISABLED)

    # FRAME DE BOTÕES (Cadastrar / Cancelar)
    botoes_frame = tk.Frame(janela_pedidos)
    botoes_frame.grid(row=5, column=0, padx=20, pady=10)
    
    btn_cadastrar = tk.Button(botoes_frame, text="✅ Confirmar e Cadastrar Saída", width=25, fg="green",
                              command=lambda: registrar_saida(itens_pedido, memo_text, botoes_frame))
    btn_cancelar = tk.Button(botoes_frame, text="❌ Cancelar Pedido", width=25, fg="red",
                             command=lambda: cancelar_pedido(itens_pedido, memo_text, botoes_frame))

    btn_cadastrar.pack(side=tk.LEFT, padx=5, ipady=5)
    btn_cancelar.pack(side=tk.LEFT, padx=5, ipady=5)
    
    botoes_frame.grid_remove()  # Esconde o frame ao iniciar

    # --- BOTÃO SAIR (O seu pedido) ---
    btn_sair = tk.Button(janela_pedidos, text="Fechar Janela", command=janela_pedidos.destroy)
    btn_sair.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

    # --- CONFIGURA O COMMAND DO BTN_CSV AGORA ---
    btn_csv.config(command=lambda: abrir_pedido_csv(janela_pedidos, memo_text, botoes_frame, itens_pedido))

    janela_pedidos.transient(janela_principal)
    janela_pedidos.grab_set()
    janela_pedidos.wait_window()

