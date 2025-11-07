import tkinter as tk
import sqlite3
from tkinter import messagebox

def abrir_janela_consulta(janela_mae):

    janela_consulta = tk.Toplevel(janela_mae)
    janela_consulta.title("Consulta de Estoque")
    janela_consulta.geometry("600x450")

    janela_consulta.transient(janela_mae)
    janela_consulta.grab_set()

    # --- Funções Internas ---

    def carregar_estoque():
        try:
            with sqlite3.connect("pedidos.db") as conexao:
                cursor = conexao.cursor()
                
                # O seu SELECT está CORRETO!
                cursor.execute("SELECT id, nome, quantidade FROM estoque") # Poderia adicionar o comando  (ORDER BY nome ASC) depois do from estoque se quiser ordenar por alfateic
                registros = cursor.fetchall()

            text_estoque.delete("1.0", tk.END)

            if registros:
                # --- CORRIGIDO ---
                # Removi a coluna "Valor" do cabeçalho
                text_estoque.insert(tk.END, f"{'ID':<5} {'Produto':<30} {'Qtd':<10}\n")
                text_estoque.insert(tk.END, "-"*50 + "\n")
                
                for row in registros:
                    # [0]=id, [1]=nome, [2]=quantidade
                    
                    # --- CORRIGIDO ---
                    # Removi {row[3]:<10.2f} do final
                    # Aumentei o espaço do nome para <30
                    text_estoque.insert(tk.END, f"{row[0]:<5} {row[1]:<30} {row[2]:<10}\n")
            else:
                text_estoque.insert(tk.END, "Nenhum produto cadastrado no estoque.\n")
        
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Erro ao carregar estoque: {e}", parent=janela_consulta)

    # --- (O resto das suas funções 'apagar_produto' e 'sair' estão PERFEITAS) ---
    def apagar_produto():
        try:
            produto_id = int(entry_id.get())
        except ValueError:
            messagebox.showerror("Erro", "Digite um ID válido!", parent=janela_consulta)
            return

        try:
            with sqlite3.connect("pedidos.db") as conexao:
                cursor = conexao.cursor()

                cursor.execute("SELECT * FROM estoque WHERE id = ?", (produto_id,))
                produto = cursor.fetchone()
                if not produto:
                    messagebox.showerror("Erro", "Produto não encontrado!", parent=janela_consulta)
                    return 

                cursor.execute("DELETE FROM estoque WHERE id = ?", (produto_id,))
                conexao.commit() 

            messagebox.showinfo("Sucesso", f"Produto ID {produto_id} apagado com sucesso!", parent=janela_consulta)
            carregar_estoque()  # Atualiza a lista
        
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Erro ao apagar produto: {e}", parent=janela_consulta)

    def sair():
        janela_consulta.destroy()

    # ================= Janela ==================
    # (Toda a sua interface está PERFEITA)

    btn_carregar = tk.Button(janela_consulta, text="Atualizar Estoque", command=carregar_estoque)
    btn_carregar.pack(pady=10)

    text_estoque = tk.Text(janela_consulta, height=15, width=70)
    text_estoque.pack(pady=10)

    frame_apagar = tk.Frame(janela_consulta)
    frame_apagar.pack(pady=5)

    lbl_id = tk.Label(frame_apagar, text="ID para apagar:")
    lbl_id.pack(side=tk.LEFT, padx=5)

    entry_id = tk.Entry(frame_apagar, width=10)
    entry_id.pack(side=tk.LEFT, padx=5)

    btn_apagar = tk.Button(frame_apagar, text="Apagar Produto", command=apagar_produto)
    btn_apagar.pack(side=tk.LEFT, padx=5)

    btn_sair = tk.Button(janela_consulta, text="Sair", command=sair)
    btn_sair.pack(pady=5)
    carregar_estoque()