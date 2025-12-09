import tkinter as tk
from tkinter import messagebox 
import banco 

# --- Inicialização do Banco de Dados ---
banco.inicializar_banco()

# --- Funções do Menu ---
def sair():
    janela.quit()

def cadastrar_item(): # Mudei o nome desta função para ser mais claro
    print("Chamando a tela de cadastro de Itens...") 
    try:
        import cadastro # (Este é o seu 'cadastro_itens.py')
        cadastro.abrir_janela_cadastro(janela)
    except ModuleNotFoundError:
        messagebox.showerror("Erro", "Arquivo 'cadastro.py' não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um problema ao abrir o cadastro de itens:\n{e}")

# --- >>> FUNÇÃO NOVA <<< ---
def cadastrar_cliente():
    print("Chamando a tela de Cadastro de Clientes...")
    try:
        # 1. Importa o novo arquivo
        import cadastro_clientes 
        # 2. Chama a função principal dele
        cadastro_clientes.abrir_janela_cadastro_cliente(janela)
    except ModuleNotFoundError:
        messagebox.showerror("Erro", "Arquivo 'cadastro_clientes.py' não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um problema ao abrir o cadastro de clientes:\n{e}")
# -------------------------

def entrada_estoque():
    print("Chamando a tela de Entrada de Estoque...")
    try:
        import entrada_estoque 
        entrada_estoque.abrir_janela_entrada(janela) 
    except ModuleNotFoundError:
        messagebox.showerror("Erro", "Arquivo 'entrada_estoque.py' não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um problema ao abrir a entrada de estoque:\n{e}")

def saida_estoque():
    print("Chamando a tela de saída de estoque...")
    try:
        import saida_estoque 
        saida_estoque.abrir_janela_saida(janela) 
    except ModuleNotFoundError:
        messagebox.showerror("Erro", "Arquivo 'saida_estoque.py' não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um problema ao abrir a saida de estoque:\n{e}")


def compra():
    print("Chamando a tela de gráfico...") # Placeholder para teste
    # import compra
    # compra()

def fornecedores():
    print("Chamando Fornecedores...")
    try:
        import cadastro_fornecedores
        cadastro_fornecedores.abrir_janela_fornecedores(janela)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir fornecedores: {e}")

def consulta():
    print("Chamando a tela de consulta...")
    try:
        import consulta 
        consulta.abrir_janela_consulta(janela)
    except ModuleNotFoundError:
        messagebox.showerror("Erro", "Arquivo 'consulta.py' não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um problema ao abrir a consulta:\n{e}")

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

botao_cadastrar_item = tk.Button(barra_lateral, text="Cadastrar Itens", command=cadastrar_item)
botao_cadastrar_item.pack(fill='x', pady=5)

botao_cadastrar_cliente = tk.Button(barra_lateral, text="Cadastrar Clientes", fg="blue", command=cadastrar_cliente)
botao_cadastrar_cliente.pack(fill='x', pady=5)

botao_entrada = tk.Button(barra_lateral, text="Entrada de Estoque (+)", fg="green", command=entrada_estoque)
botao_entrada.pack(fill='x', pady=5)

botao_saida = tk.Button(barra_lateral, text="Saída de Estoque (Manual)", command=saida_estoque)
botao_saida.pack(fill='x', pady=5)

botao_pedido_compra = tk.Button(barra_lateral, text="Pedido de compra", state='disabled', command=compra)
botao_pedido_compra.pack(fill='x', pady=5)

botao_consulta = tk.Button(barra_lateral, text="Consulta de Estoque", command=consulta)
botao_consulta.pack(fill='x', pady=5)


botao_consignado = tk.Button(barra_lateral, text="Consignado (Em Breve)", state='disabled')
botao_consignado.pack(fill='x', pady=5)

botao_historico = tk.Button(barra_lateral, text="Histórico (Em Breve)", state='disabled')
botao_historico.pack(fill='x', pady=5)

botao_fornecedor = tk.Button(barra_lateral, text="Cadastrar Fornecedores", command=fornecedores)
botao_fornecedor.pack(fill='x', pady=5)

botao_sair = tk.Button(barra_lateral, text="Sair", command=sair, fg="red")
botao_sair.pack(side='bottom', fill='x', pady=20)



# --- Adicionando o Logo à ÁREA DE CONTEÚDO ---
try:
    # 1. Carrega a imagem original
    logo_original = tk.PhotoImage(file="logo.png")
    # 2. REDIMENSIONA a imagem (ex: para metade do tamanho)
    logo_redimensionada = logo_original.subsample(3, 3)
    # 3. Usa a imagem REDIMENSIONADA no Label
    label_logo = tk.Label(area_conteudo, image=logo_redimensionada, bg="white")
    # 4. [MUITO IMPORTANTE] Guarda uma referência da imagem
    label_logo.image = logo_redimensionada 
    label_logo.pack(expand=True, anchor="n", pady=20)
except tk.TclError:
    label_logo = tk.Label(area_conteudo, text="Imagem 'logo.png' não encontrada.", bg="white", fg="red")
    label_logo.pack(expand=True, anchor="n", pady=20)

# --- Iniciar a aplicação ---
janela.mainloop()