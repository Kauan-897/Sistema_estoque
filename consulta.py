import tkinter as tk
import sqlite3
from tkinter import messagebox

# 1. Todo o código da janela foi movido para dentro de uma função.
#    Ela recebe a 'janela_mae' (a janela principal) como argumento.
def abrir_janela_consulta(janela_mae):

    # 2. Criamos uma Toplevel (janela "filha") em vez de um novo Tk()
    janela_consulta = tk.Toplevel(janela_mae)
    janela_consulta.title("Consulta de Estoque")
    janela_consulta.geometry("600x450")

    # 3. (Opcional) Estas linhas "travam" a janela principal
    #    enquanto esta estiver aberta.
    janela_consulta.transient(janela_mae)
    janela_consulta.grab_set()

    # --- Funções Internas ---
    # (Elas só existem dentro desta janela)

    def carregar_estoque():
        # 4. Corrigido: O nome do banco agora é "pedidos.db" (minúsculo)
        # 5. Usando 'with' para garantir que a conexão feche sozinha
        try:
            with sqlite3.connect("pedidos.db") as conexao:
                cursor = conexao.cursor()
                # Selecionando colunas específicas para garantir a ordem
                cursor.execute("SELECT id, nome, quantidade, valor FROM estoque")
                registros = cursor.fetchall()

            # Limpa o Text antes de mostrar
            text_estoque.delete("1.0", tk.END)

            if registros:
                text_estoque.insert(tk.END, f"{'ID':<5} {'Produto':<20} {'Qtd':<10} {'Preço':<10}\n")
                text_estoque.insert(tk.END, "-"*50 + "\n")
                for row in registros:
                    # [0]=id, [1]=nome, [2]=quantidade, [3]=valor
                    text_estoque.insert(tk.END, f"{row[0]:<5} {row[1]:<20} {row[2]:<10} {row[3]:<10.2f}\n")
            else:
                text_estoque.insert(tk.END, "Nenhum produto cadastrado no estoque.\n")
        
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Erro ao carregar estoque: {e}", parent=janela_consulta)

    def apagar_produto():
        try:
            produto_id = int(entry_id.get())
        except ValueError:
            # 6. Adicionado 'parent=janela_consulta' para o popup aparecer na frente
            messagebox.showerror("Erro", "Digite um ID válido!", parent=janela_consulta)
            return

        # 4. Corrigido: O nome do banco agora é "pedidos.db"
        # 5. Usando 'with' para garantir que a conexão feche sozinha
        try:
            with sqlite3.connect("pedidos.db") as conexao:
                cursor = conexao.cursor()

                # Verifica se o produto existe
                cursor.execute("SELECT * FROM estoque WHERE id = ?", (produto_id,))
                produto = cursor.fetchone()
                if not produto:
                    messagebox.showerror("Erro", "Produto não encontrado!", parent=janela_consulta)
                    return # O 'with' fecha a conexão automaticamente

                # Apaga do banco
                cursor.execute("DELETE FROM estoque WHERE id = ?", (produto_id,))
                conexao.commit() # Commit é necessário para salvar a exclusão

            messagebox.showinfo("Sucesso", f"Produto ID {produto_id} apagado com sucesso!", parent=janela_consulta)
            carregar_estoque()  # Atualiza a lista
        
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Erro ao apagar produto: {e}", parent=janela_consulta)

    def sair():
        # 7. Toplevel usa .destroy() para fechar (em vez de .quit())
        janela_consulta.destroy()

    # ================= Janela ==================
    # 8. Todos os widgets agora são "filhos" da 'janela_consulta'

    btn_carregar = tk.Button(janela_consulta, text="Atualizar Estoque", command=carregar_estoque)
    btn_carregar.pack(pady=10)

    # Precisamos definir 'text_estoque' antes de 'carregar_estoque' ser chamada
    text_estoque = tk.Text(janela_consulta, height=15, width=70)
    text_estoque.pack(pady=10)

    frame_apagar = tk.Frame(janela_consulta)
    frame_apagar.pack(pady=5)

    lbl_id = tk.Label(frame_apagar, text="ID para apagar:")
    lbl_id.pack(side=tk.LEFT, padx=5)

    # Precisamos definir 'entry_id' antes de 'apagar_produto' ser chamada
    entry_id = tk.Entry(frame_apagar, width=10)
    entry_id.pack(side=tk.LEFT, padx=5)

    btn_apagar = tk.Button(frame_apagar, text="Apagar Produto", command=apagar_produto)
    btn_apagar.pack(side=tk.LEFT, padx=5)

    btn_sair = tk.Button(janela_consulta, text="Sair", command=sair)
    btn_sair.pack(pady=5)

    # Carrega os dados logo ao abrir
    carregar_estoque()

    # 9. REMOVEMOS o janela.mainloop()
    # A janela principal (janela_mae) já está rodando o mainloop.