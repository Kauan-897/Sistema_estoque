import tkinter as tk
from tkinter import messagebox # <-- ADICIONADO

# --- Funções (permanecem as mesmas) ---
def sair():
    janela.quit()

def cadastrar():
    print("Chamando a tela de cadastro...") # Placeholder para teste
    import cadastro
    cadastro.abrir_janela_cadastro(janela)

def orcamento():
    print("Chamando a tela de gráfico...") # Placeholder para teste
    # import orcamento
    # orcamento()

def consulta():
    print("Chamando a tela de consulta...")
    try:
        import consulta 
        consulta.abrir_janela_consulta(janela)
    except ModuleNotFoundError:
        messagebox.showerror("Erro", "Arquivo 'consulta.py' não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um problema ao abrir a consulta:\n{e}")

# --- FUNÇÃO PEDIDOS (MODIFICADA) ---
def pedidos():
    print("Chamando a tela de pedidos...")
    try:
        import pedido # 1. Importa o arquivo pedido.py
        
        # 2. Chama a função 'abrir_janela_pedidos' de dentro do arquivo
        #    e passa a 'janela' principal do menu como argumento
        pedido.abrir_janela_pedidos(janela) 
        
    except ModuleNotFoundError:
        messagebox.showerror("Erro", "Arquivo 'pedido.py' não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um problema ao abrir pedidos:\n{e}")

def saida_estoque():
    print("Chamando a tela de saída de estoque...") # Placeholder para teste
    # import saida_estoque
    # saida_estoque()

# --- Configuração da Janela Principal ---
janela = tk.Tk()
janela.title("Menu Inicial com Barra Fixa")
janela.geometry("800x500")

# --- Criação da Barra Lateral Fixa (Frame) ---
barra_lateral = tk.Frame(janela, bg="#f0f0f0", padx=10, pady=10)
barra_lateral.pack(side="left", fill="y")

# --- Criação da Área de Conteúdo Principal ---
area_conteudo = tk.Frame(janela, bg="white")
area_conteudo.pack(side="right", fill="both", expand=True)


# --- Adicionando os Botões à BARRA LATERAL ---
tk.Label(barra_lateral, text="Menu", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)

botao_cadastrar = tk.Button(barra_lateral, text="Cadastrar", command=cadastrar)
botao_cadastrar.pack(fill='x', pady=5)

botao_saida = tk.Button(barra_lateral, text="Saída de Estoque", command=saida_estoque)
botao_saida.pack(fill='x', pady=5)

botao_orcamento = tk.Button(barra_lateral, text="Orçamento", command=orcamento)
botao_orcamento.pack(fill='x', pady=5)

botao_consulta = tk.Button(barra_lateral, text="Consulta de Estoque", command=consulta)
botao_consulta.pack(fill='x', pady=5)

# Este botão agora chama a função 'pedidos' modificada
botao_pedidos = tk.Button(barra_lateral, text="Pedidos", command=pedidos) 
botao_pedidos.pack(fill='x', pady=6)

botao_sair = tk.Button(barra_lateral, text="Sair", command=sair, fg="red")
botao_sair.pack(side='bottom', fill='x', pady=20)


# --- Iniciar a aplicação ---
janela.mainloop()