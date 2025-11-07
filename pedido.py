import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import csv

# --- FUNÇÃO PARA CONEXÃO COM BANCO ---
def conectar_banco():
    return sqlite3.connect("pedidos.db")

# --- 1. FUNÇÃO PARA ABRIR CSV ---
def abrir_pedido_csv(memo_widget, botoes_frame, itens_pedido):
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    memo_widget.insert(tk.END, "Iniciando leitura do CSV...\n")
    itens_pedido.clear()  # limpa lista antiga
    
    try:
        caminho_arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo CSV",
            filetypes=[("Arquivos CSV", "*.csv")]
        )

        if not caminho_arquivo:
            memo_widget.insert(tk.END, "Leitura cancelada pelo usuário.")
            memo_widget.config(state=tk.DISABLED)
            return

        with open(caminho_arquivo, "r", encoding="utf-8-sig") as arquivo:
            leitor = csv.reader(arquivo, delimiter=';')
            
            linha_cliente = next(leitor, None)
            if not linha_cliente or len(linha_cliente) < 2:
                raise Exception("Arquivo CSV vazio ou formato inválido.")
            
            cliente = linha_cliente[1].strip()
            memo_widget.insert(tk.END, f"Cliente identificado: {cliente}\n")
            memo_widget.insert(tk.END, "-------------------------------------\n")
            memo_widget.insert(tk.END, "Itens com quantidade > 0:\n")

            for linha in leitor:
                if not linha or len(linha) < 2:
                    continue
                
                produto = linha[0].strip()
                quantidade_str = linha[1].strip().replace(',', '.')
                
                try:
                    quantidade = float(quantidade_str)
                    if quantidade > 0:
                        memo_widget.insert(tk.END, f"  -> Produto: {produto} (Qtd: {quantidade})\n")
                        itens_pedido.append((produto, quantidade, cliente))
                except ValueError:
                    pass

            memo_widget.insert(tk.END, "-------------------------------------\n")
            memo_widget.insert(tk.END, f"{len(itens_pedido)} itens carregados.\n")

        if len(itens_pedido) > 0:
            messagebox.showinfo("Sucesso", "Pedido carregado com sucesso!")
            # Mostra os botões de ação (Cadastrar e Cancelar)
            for widget in botoes_frame.winfo_children():
                widget.pack(pady=5)
        else:
            messagebox.showinfo("Aviso", "Nenhum item com quantidade > 0 encontrado.")

    except Exception as e:
        memo_widget.insert(tk.END, f"\n--- ERRO ---\nOcorreu um erro: {e}")
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        
    finally:
        memo_widget.config(state=tk.DISABLED)


# --- 2. FUNÇÃO PARA REGISTRAR SAÍDA ---
def registrar_saida(itens_pedido, memo_widget, botoes_frame):
    if not itens_pedido:
        messagebox.showwarning("Aviso", "Nenhum pedido carregado.")
        return

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()
        for produto, quantidade, cliente in itens_pedido:
            # 1️⃣ Atualiza estoque
            cursor.execute("UPDATE estoque SET quantidade = quantidade - ? WHERE nome = ?", (quantidade, produto))
            # 2️⃣ Registra saída
            cursor.execute("""
                INSERT INTO saidas (funcionario, cliente, produto, quantidade, data)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, ("Sistema", cliente, produto, quantidade))
        conexao.commit()
        conexao.close()
        
        messagebox.showinfo("Sucesso", "Saída registrada e estoque atualizado!")
        memo_widget.config(state=tk.NORMAL)
        memo_widget.insert(tk.END, "\n✔️ Saída registrada com sucesso!\n")
        memo_widget.config(state=tk.DISABLED)
        botoes_frame.pack_forget()  # esconde botões

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao registrar saída: {e}")


# --- 3. FUNÇÃO PARA CANCELAR PEDIDO ---
def cancelar_pedido(itens_pedido, memo_widget, botoes_frame):
    itens_pedido.clear()
    memo_widget.config(state=tk.NORMAL)
    memo_widget.insert(tk.END, "\n❌ Pedido cancelado pelo usuário.\n")
    memo_widget.config(state=tk.DISABLED)
    botoes_frame.pack_forget()


# --- 4. FUNÇÃO PARA ABRIR JANELA TOPLEVEL ---
def abrir_janela_pedidos(janela_principal):
    janela_pedidos = tk.Toplevel(janela_principal)
    janela_pedidos.title("Pedidos")
    janela_pedidos.geometry("650x600")

    itens_pedido = []  # armazenar itens do pedido atual

    def estoque():
        try:
            import consulta
            consulta.abrir_janela_consulta(janela_pedidos)
        except ModuleNotFoundError:
            messagebox.showerror("Erro", "Arquivo 'consulta.py' não encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um problema ao abrir o estoque:\n{e}")

    # MENU PRINCIPAL
    menu_label = tk.Label(janela_pedidos, text="Menu", font=("Arial", 12, "bold"))
    menu_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

    # BOTÃO CSV
    btn_csv = tk.Button(
        janela_pedidos,
        text="Abrir Pedido CSV",
        command=lambda: abrir_pedido_csv(memo_text, botoes_frame, itens_pedido)
    )
    btn_csv.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

    # CONSULTA ESTOQUE
    btn_consulta = tk.Button(janela_pedidos, text="Consultar Estoque", command=estoque)
    btn_consulta.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

    # ÁREA DE LOG
    memo_label = tk.Label(janela_pedidos, text="Visualização do Pedido (Logs)")
    memo_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
    memo_text = tk.Text(janela_pedidos, height=20, width=80, state=tk.DISABLED)
    memo_text.grid(row=4, column=0, padx=20, pady=5)

    # FRAME DE BOTÕES (Cadastrar / Cancelar)
    botoes_frame = tk.Frame(janela_pedidos)
    botoes_frame.grid(row=5, column=0, padx=20, pady=10)
    botoes_frame.pack_forget  # esconde até carregar um pedido

    btn_cadastrar = tk.Button(botoes_frame, text="✅ Cadastrar Saída", width=25,
                              command=lambda: registrar_saida(itens_pedido, memo_text, botoes_frame))
    btn_cancelar = tk.Button(botoes_frame, text="❌ Cancelar Pedido", width=25,
                             command=lambda: cancelar_pedido(itens_pedido, memo_text, botoes_frame))

    btn_cadastrar.pack(pady=5)
    btn_cancelar.pack(pady=5)
    botoes_frame.pack_forget()  # inicialmente escondido

    btn_sair = tk.Button(janela_pedidos, text="Fechar", command=janela_pedidos.destroy)
    btn_sair.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

    janela_pedidos.transient(janela_principal)
    janela_pedidos.grab_set()


# --- TESTE LOCAL ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Janela Principal")
    root.geometry("300x200")

    btn_teste = tk.Button(root, text="Abrir Pedidos", command=lambda: abrir_janela_pedidos(root))
    btn_teste.pack(pady=50)

    root.mainloop()
