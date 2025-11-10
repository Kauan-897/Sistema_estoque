import tkinter as tk
from tkinter import messagebox 
import banco 

# --- Inicialização do Banco de Dados ---
banco.inicializar_banco()

# --- Funções do Menu ---
def sair():
    janela.quit()

def cadastrar():
    print("Chamando a tela de cadastro...") 
    try:
        import cadastro # (Este é o 'cadastro_itens.py')
        cadastro.abrir_janela_cadastro(janela)
    except ModuleNotFoundError:
        messagebox.showerror("Erro", "Arquivo 'cadastro.py' não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um problema ao abrir o cadastro:\n{e}")

def entrada_estoque():# chamada da tela de entrada de estoque
    print("Chamando a tela de Entrada de Estoque...")
    try:
        import entrada_estoque # 1. Importa o novo ficheiro
        entrada_estoque.abrir_janela_entrada(janela) # 2. Chama a função
    except ModuleNotFoundError:
        messagebox.showerror("Erro", "Arquivo 'entrada_estoque.py' não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um problema ao abrir a entrada de estoque:\n{e}")

def saida_estoque():
    print("Chamando a tela de saída de estoque...") # Placeholder para teste
    import saida_estoque
    saida_estoque()

def orcamento():
    print("Chamando a tela de gráfico...") # Placeholder para teste
    import orcamento
    orcamento()

def consulta():
    print("Chamando a tela de consulta...")
    try:
        import consulta 
        consulta.abrir_janela_consulta(janela)
    except ModuleNotFoundError:
        messagebox.showerror("Erro", "Arquivo 'consulta.py' não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um problema ao abrir a consulta:\n{e}")

def pedidos():
    print("Chamando a tela de pedidos...")
    try:
        import pedido 
        pedido.abrir_janela_pedidos(janela) 
    except ModuleNotFoundError:
        messagebox.showerror("Erro", "Arquivo 'pedido.py' não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um problema ao abrir pedidos:\n{e}")

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

botao_cadastrar = tk.Button(barra_lateral, text="Cadastrar (Item Novo)", command=cadastrar)
botao_cadastrar.pack(fill='x', pady=5)
# -------------------------
botao_entrada = tk.Button(barra_lateral, text="Entrada de Estoque (+)", fg="green", command=entrada_estoque)
botao_entrada.pack(fill='x', pady=5)
# -------------------------

botao_saida = tk.Button(barra_lateral, text="Saída de Estoque (Manual)", command=saida_estoque)
botao_saida.pack(fill='x', pady=5)

botao_orcamento = tk.Button(barra_lateral, text="Orçamento", command=orcamento)
botao_orcamento.pack(fill='x', pady=5)

botao_consulta = tk.Button(barra_lateral, text="Consulta de Estoque", command=consulta)
botao_consulta.pack(fill='x', pady=5)

botao_pedidos = tk.Button(barra_lateral, text="Pedidos (Baixa via CSV)", command=pedidos) 
botao_pedidos.pack(fill='x', pady=6)

botao_sair = tk.Button(barra_lateral, text="Sair", command=sair, fg="red")
botao_sair.pack(side='bottom', fill='x', pady=20)

try:
    logo_original = tk.PhotoImage(file="logo.png")
    logo_redimensionada = logo_original.subsample(3, 3)# função para redimensionar a imagem
    label_logo = tk.Label(area_conteudo, image=logo_redimensionada, bg="white")
    label_logo.image = logo_redimensionada #Guarda uma referência da imagem sem esta linha, a imagem pode desaparecer!  
    label_logo.pack(expand=True, anchor="n", pady=20)
    
except tk.TclError:
    label_logo = tk.Label(area_conteudo, text="Imagem 'logo.png' não encontrada.", bg="white", fg="red")
    label_logo.pack(expand=True, anchor="n", pady=20)

janela.mainloop()