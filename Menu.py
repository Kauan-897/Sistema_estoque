import tkinter as tk
from tkinter import messagebox 
import banco 

# --- Inicialização do Banco de Dados ---
try:
    banco.inicializar_banco()
except Exception as e:
    messagebox.showerror("Erro Fatal", f"Erro ao iniciar banco de dados:\n{e}")

# --- Funções do Menu ---
def sair():
    janela.quit()

# === MÓDULO: CADASTRO ===

def cadastrar_item():
    try:
        from Modulos_Cadastro import cadastro
        cadastro.abrir_janela_cadastro(janela)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir cadastro de itens:\n{e}")

def cadastrar_cliente():
    try:
        from Modulos_Cadastro import cadastro_clientes 
        cadastro_clientes.abrir_janela_cadastro_cliente(janela)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir cadastro de clientes:\n{e}")

def cadastrar_fornecedor():
    try:
        from Modulos_Cadastro import cadastro_fornecedores
        cadastro_fornecedores.abrir_janela_fornecedores(janela)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir fornecedores:\n{e}")

# === MÓDULO: ESTOQUE ===

def entrada_estoque():
    try:
        from Modulos_Estoque import entrada_estoque
        entrada_estoque.abrir_janela_entrada(janela)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir entrada:\n{e}")

def saida_estoque():
    try:
        from Modulos_Estoque import saida_estoque 
        saida_estoque.abrir_janela_saida(janela) 
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir saída:\n{e}")

def abrir_consignado():
    try:
        from Modulos_Estoque import consignado
        consignado.abrir_janela_consignado(janela)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir consignado:\n{e}")

def consulta_estoque():
    try:
        from Modulos_Estoque import consulta 
        consulta.abrir_janela_consulta(janela)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir consulta:\n{e}")

def historico():
    try:
        from Modulos_Estoque import historico_saidas 
        historico_saidas.abrir_janela_historico(janela)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir histórico:\n{e}")

def compra(): # Placeholder se tiver um modulo de compra
    messagebox.showinfo("Em Breve", "Módulo de Pedido de Compra em desenvolvimento.")
    # try:
    #     from Modulos_Estoque import compra   
    #     compra.abrir_janela_compra(janela)
    # except Exception as e: ...


# --- Configuração da Janela Principal ---
janela = tk.Tk()
janela.title("Menu Inicial - Sistema de Gestão")
janela.state('zoomed') # Maximiza a janela

# --- Criação da Barra Lateral Fixa (Frame) ---
barra_lateral = tk.Frame(janela, bg="#f0f0f0", padx=10, pady=10)
barra_lateral.pack(side="left", fill="y")

# --- Criação da Área de Conteúdo Principal ---
area_conteudo = tk.Frame(janela, bg="white")
area_conteudo.pack(side="right", fill="both", expand=True)


# --- Adicionando os Botões à BARRA LATERAL ---
tk.Label(barra_lateral, text="MENU PRINCIPAL", font=("Arial", 14, "bold"), bg="#f0f0f0", fg="#333").pack(pady=(10, 20))

# Grupo Cadastro
tk.Label(barra_lateral, text="Cadastros", font=("Arial", 10, "bold"), bg="#f0f0f0", fg="gray").pack(anchor="w")
tk.Button(barra_lateral, text="📦 Cadastrar Itens", command=cadastrar_item).pack(fill='x', pady=2)
tk.Button(barra_lateral, text="👥 Cadastrar Clientes", command=cadastrar_cliente).pack(fill='x', pady=2)
tk.Button(barra_lateral, text="🏭 Cadastrar Fornecedores", command=cadastrar_fornecedor).pack(fill='x', pady=2)

# Separador visual
tk.Frame(barra_lateral, height=2, bg="#ccc").pack(fill='x', pady=10)

# Grupo Estoque
tk.Label(barra_lateral, text="Movimentação", font=("Arial", 10, "bold"), bg="#f0f0f0", fg="gray").pack(anchor="w")
tk.Button(barra_lateral, text="📥 Entrada de Estoque", fg="green", command=entrada_estoque).pack(fill='x', pady=2)
tk.Button(barra_lateral, text="📤 Saída de Estoque", fg="red", command=saida_estoque).pack(fill='x', pady=2)
tk.Button(barra_lateral, text="🔄 Consignado", command=abrir_consignado).pack(fill='x', pady=2)

# Separador visual
tk.Frame(barra_lateral, height=2, bg="#ccc").pack(fill='x', pady=10)

# Grupo Gestão
tk.Label(barra_lateral, text="Gestão", font=("Arial", 10, "bold"), bg="#f0f0f0", fg="gray").pack(anchor="w")
tk.Button(barra_lateral, text="🔍 Consulta Geral", command=consulta_estoque).pack(fill='x', pady=2)
tk.Button(barra_lateral, text="📜 Histórico de Saídas", command=historico).pack(fill='x', pady=2)
tk.Button(barra_lateral, text="🛒 Pedido de Compra", state='normal', command=compra).pack(fill='x', pady=2)

# Botão Sair
tk.Button(barra_lateral, text="❌ Sair do Sistema", command=sair, fg="white", bg="#d9534f").pack(side='bottom', fill='x', pady=20)


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