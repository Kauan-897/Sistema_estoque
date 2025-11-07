import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import csv

# --- 1. CRIAÇÃO DO BANCO ---
# (Função exatamente como a sua, sem mudanças)
def criar_banco():
    try:
        conexao = sqlite3.connect("pedidos.db")
        cursor = conexao.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS saidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario TEXT,
            cliente TEXT,
            produto TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            data TEXT
        )
        """)

        conexao.commit()
        print("Banco de dados criado/verificado com sucesso!")

    except sqlite3.Error as e:
        print(f"Erro ao criar o banco: {e}")

    finally:
        if conexao:
            conexao.close()


# --- 2. EXECUTA AO ABRIR O SISTEMA ---
criar_banco()


# --- 3. FUNÇÃO PARA ABRIR CSV (MODIFICADA) ---
# Agora, ela recebe o 'memo_widget' como argumento para poder escrever nele
def abrir_pedido_csv(memo_widget):
    
    # --- MUDANÇA A: Limpar o memo antes de começar ---
    memo_widget.config(state=tk.NORMAL) # Habilita o widget para edição
    memo_widget.delete('1.0', tk.END)   # Apaga todo o texto anterior
    memo_widget.insert(tk.END, "Iniciando leitura do CSV...\n")
    
    try:
        # Abre janela para escolher o arquivo
        caminho_arquivo = filedialog.askopenfilename(
            title="Selecioe o arquivo CSV",
            filetypes=[("Arquivos CSV", "*.csv")]
        )

        # Se o usuário cancelar, não faz nada
        if not caminho_arquivo:
            memo_widget.insert(tk.END, "Leitura cancelada pelo usuário.")
            memo_widget.config(state=tk.DISABLED) # Desabilita
            return

        # Lê o CSV separado por ponto e vírgula
        # Usamos 'utf-8-sig' para ser compatível com Excel
        with open(caminho_arquivo, "r", encoding="utf-8-sig") as arquivo:
            leitor = csv.reader(arquivo, delimiter=';')
            
            # --- MUDANÇA B: Ler e mostrar o Cliente ---
            linha_cliente = next(leitor, None)
            if not linha_cliente or len(linha_cliente) < 2:
                raise Exception("Arquivo CSV vazio ou formato inválido.")
            
            cliente = linha_cliente[1].strip()
            memo_widget.insert(tk.END, f"Cliente identificado: {cliente}\n")
            memo_widget.insert(tk.END, "-------------------------------------\n")
            memo_widget.insert(tk.END, "Itens com quantidade > 0:\n")

            itens_encontrados = 0
            
            # --- MUDANÇA C: Ler e mostrar os Produtos ---
            for linha in leitor:
                # Pula linhas mal formatadas
                if not linha or len(linha) < 2:
                    continue
                
                produto = linha[0].strip()
                # Substitui vírgula por ponto para poder virar número
                quantidade_str = linha[1].strip().replace(',', '.')
                
                try:
                    # Converte para número
                    quantidade = float(quantidade_str)
                    
                    # Só mostra se a quantidade for maior que zero
                    if quantidade > 0:
                        memo_widget.insert(tk.END, f"  -> Produto: {produto} (Qtd: {quantidade})\n")
                        itens_encontrados += 1
                        
                except ValueError:
                    # Ignora linhas onde a quantidade não é um número
                    pass

            memo_widget.insert(tk.END, "-------------------------------------\n")
            
            if itens_encontrados > 0:
                memo_widget.insert(tk.END, f"Leitura concluída. {itens_encontrados} itens encontrados.")
            else:
                memo_widget.insert(tk.END, "Leitura concluída. Nenhum item com quantidade > 0 foi encontrado.")

        messagebox.showinfo("Sucesso", f"Arquivo '{caminho_arquivo}' visualizado com sucesso!")

    except Exception as e:
        # Se der erro, mostra no memo também
        memo_widget.insert(tk.END, f"\n--- ERRO ---\nOcorreu um erro: {e}")
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        
    finally:
        # --- MUDANÇA D: Desabilitar o memo ---
        # No final, desabilitamos o memo para que o usuário não possa digitar nele
        memo_widget.config(state=tk.DISABLED)


# --- 4. INTERFACE TKINTER (MODIFICADA) ---
janela = tk.Tk()
janela.title("Pedidos")
janela.geometry("650x550") # Aumentei um pouco a janela para caber o memo

def estoque():
    try:
        import consulta
        consulta.abrir_janela_consulta(janela)
    except ModuleNotFoundError:
        messagebox.showerror("Erro", "Arquivo 'consulta.py' não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um problema ao abrir o estoque:\n{e}")

# --- MENU PRINCIPAL E BOTÕES ---
menu_label = tk.Label(janela, text="Menu", font=("Arial", 12, "bold"))
menu_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

btn_consulta = tk.Button(janela, text="Consultar Estoque", command=estoque)
btn_consulta.grid(row=2, column=0, padx=20, pady=10, sticky="ew") # sticky="ew" faz ele esticar

# --- MUDANÇA E: CRIAÇÃO DO MEMO (LOG) ---
# O "memo" que você pediu, com uma barra de rolagem
memo_label = tk.Label(janela, text="Visualização do Pedido (Logs)")
memo_label.grid(row=3, column=0, padx=20, pady=(10,0), sticky="w")
memo_text = tk.Text(janela, height=20, width=80, state=tk.DISABLED)
memo_text.grid(row=4, column=0, padx=20, pady=5)


# --- MUDANÇA F: Botão CSV (definido DEPOIS do memo) ---
# Movemos o 'btn_csv' para cá
# Usamos 'lambda' para passar o 'memo_text' para a função 'abrir_pedido_csv'
btn_csv = tk.Button(janela, text="Abrir Pedido CSV", 
                    command=lambda: abrir_pedido_csv(memo_text))
btn_csv.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

# --- BOTÃO SAIR ---
btn_sair = tk.Button(janela, text="Sair", command=janela.quit)
btn_sair.grid(row=5, column=0, padx=20, pady=10, sticky="ew")   



janela.mainloop()