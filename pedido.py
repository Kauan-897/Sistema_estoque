import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import csv

# --- 3. FUNÇÃO PARA ABRIR CSV ---
def abrir_pedido_csv(memo_widget):
    memo_widget.config(state=tk.NORMAL)
    memo_widget.delete('1.0', tk.END)
    memo_widget.insert(tk.END, "Iniciando leitura do CSV...\n")
    
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

            itens_encontrados = 0
            
            for linha in leitor:
                if not linha or len(linha) < 2:
                    continue
                
                produto = linha[0].strip()
                quantidade_str = linha[1].strip().replace(',', '.')
                
                try:
                    quantidade = float(quantidade_str)
                    if quantidade > 0:
                        memo_widget.insert(tk.END, f"  -> Produto: {produto} (Qtd: {quantidade})\n")
                        itens_encontrados += 1
                except ValueError:
                    pass

            memo_widget.insert(tk.END, "-------------------------------------\n")
            
            if itens_encontrados > 0:
                memo_widget.insert(tk.END, f"Leitura concluída. {itens_encontrados} itens encontrados.")
            else:
                memo_widget.insert(tk.END, "Leitura concluída. Nenhum item com quantidade > 0 foi encontrado.")

        messagebox.showinfo("Sucesso", f"Arquivo '{caminho_arquivo}' visualizado com sucesso!")

    except Exception as e:
        memo_widget.insert(tk.END, f"\n--- ERRO ---\nOcorreu um erro: {e}")
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        
    finally:
        memo_widget.config(state=tk.DISABLED)


# --- 4. FUNÇÃO PARA ABRIR A JANELA COMO TOPLEVEL ---
def abrir_janela_pedidos(janela_principal):
    janela_pedidos = tk.Toplevel(janela_principal)
    janela_pedidos.title("Pedidos")
    janela_pedidos.geometry("650x550")

    def estoque():
        try:
            import consulta
            consulta.abrir_janela_consulta(janela_pedidos)
        except ModuleNotFoundError:
            messagebox.showerror("Erro", "Arquivo 'consulta.py' não encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um problema ao abrir o estoque:\n{e}")

    # --- MENU PRINCIPAL E BOTÕES ---
    menu_label = tk.Label(janela_pedidos, text="Menu", font=("Arial", 12, "bold"))
    menu_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

    btn_csv = tk.Button(
        janela_pedidos,
        text="Abrir Pedido CSV",
        command=lambda: abrir_pedido_csv(memo_text)
    )
    btn_csv.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

    btn_consulta = tk.Button(janela_pedidos, text="Consultar Estoque", command=estoque)
    btn_consulta.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

    # --- ÁREA DE LOG ---
    memo_label = tk.Label(janela_pedidos, text="Visualização do Pedido (Logs)")
    memo_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
    
    memo_text = tk.Text(janela_pedidos, height=20, width=80, state=tk.DISABLED)
    memo_text.grid(row=4, column=0, padx=20, pady=5)

    btn_sair = tk.Button(janela_pedidos, text="Fechar", command=janela_pedidos.destroy)
    btn_sair.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

    janela_pedidos.transient(janela_principal)  # Mantém sobre a janela principal
    janela_pedidos.grab_set()  # Bloqueia interação com a janela principal até fechar


# --- TESTE LOCAL (opcional) ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Janela Principal")
    root.geometry("300x200")

    btn_teste = tk.Button(root, text="Abrir Pedidos", command=lambda: abrir_janela_pedidos(root))
    btn_teste.pack(pady=50)

    root.mainloop()
