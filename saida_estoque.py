import tkinter as tk

# --- Funções (permanecem as mesmas) ---
def sair():
    janela.quit()


janela = tk.Tk()
janela.title("Menu Inicial com Barra Fixa")
janela.geometry("800x500")



botao_sair = tk.Button(janela, text="Sair", command=sair, fg="red")
botao_sair.pack(side='bottom', fill='x', pady=20)


# --- Iniciar a aplicação ---
janela.mainloop()