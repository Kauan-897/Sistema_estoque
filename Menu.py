import tkinter as tk
from tkinter import messagebox 
import banco 

# --- Inicialização do Banco ---
try:
    banco.inicializar_banco()
except Exception as e:
    messagebox.showerror("Erro Fatal", f"Erro ao iniciar banco:\n{e}")

# =============================================================================
# SISTEMA DE NAVEGAÇÃO (SINGLE PAGE APPLICATION)
# =============================================================================
def mostrar_tela(funcao_modulo):
    """
    1. Limpa a área branca (direita).
    2. Executa a função do módulo passando a área limpa como 'parent'.
    """
    # Limpa tudo o que estiver na área de conteúdo
    for widget in area_conteudo.winfo_children():
        widget.destroy()
    
    # Chama a função do módulo
    try:
        funcao_modulo(area_conteudo)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar módulo:\n{e}")
        mostrar_logo() # Se der erro, volta para o início

def mostrar_logo():
    """Restaura a tela inicial com o logo."""
    for widget in area_conteudo.winfo_children():
        widget.destroy()
        
    try:
        global logo_redimensionada 
        logo_original = tk.PhotoImage(file="logo.png")
        logo_redimensionada = logo_original.subsample(4, 4)
        
        lbl = tk.Label(area_conteudo, image=logo_redimensionada, bg="white")
        lbl.image = logo_redimensionada 
        lbl.pack(expand=True)
    except tk.TclError:
        tk.Label(area_conteudo, text="SISTEMA DE GESTÃO", font=("Arial", 30, "bold"), bg="white", fg="#333").pack(expand=True)

def sair():
    if messagebox.askyesno("Sair", "Deseja realmente sair do sistema?"):
        janela.quit()

# =============================================================================
# FUNÇÕES DE CHAMADA DOS MÓDULOS (Wrappers)
# =============================================================================

# --- CADASTROS ---
def ir_cadastro_item():
    from Modulos_Cadastro import cadastro
    # O módulo deve ter a função: abrir_janela_cadastro(parent)
    mostrar_tela(cadastro.abrir_janela_cadastro)

def ir_cadastro_cliente():
    from Modulos_Cadastro import cadastro_clientes 
    mostrar_tela(cadastro_clientes.abrir_janela_cadastro_cliente)

def ir_cadastro_fornecedor():
    from Modulos_Cadastro import cadastro_fornecedores
    mostrar_tela(cadastro_fornecedores.abrir_janela_fornecedores)

# --- ESTOQUE ---
def ir_entrada():
    from Modulos_Estoque import entrada_estoque
    mostrar_tela(entrada_estoque.abrir_janela_entrada)

def ir_saida():
    from Modulos_Estoque import saida_estoque 
    mostrar_tela(saida_estoque.abrir_janela_saida)

def ir_consignado():
    from Modulos_Estoque import consignado
    mostrar_tela(consignado.abrir_janela_consignado)

# --- GESTÃO ---
def ir_consulta():
    from Modulos_Estoque import consulta 
    mostrar_tela(consulta.abrir_janela_consulta)

def ir_historico():
    from Modulos_Estoque import historico_saidas 
    mostrar_tela(historico_saidas.abrir_janela_historico)

def ir_compra():
    messagebox.showinfo("Em Breve", "Módulo de Compras em desenvolvimento.")


# =============================================================================
# INTERFACE PRINCIPAL
# =============================================================================
janela = tk.Tk()
janela.title("Sistema Integrado de Gestão")
janela.state('zoomed') # Tela cheia

# --- Layout: Barra Lateral (Esquerda) + Conteúdo (Direita) ---
barra_lateral = tk.Frame(janela, bg="#f0f0f0", width=250)
barra_lateral.pack(side="left", fill="y")
# Impede que a barra lateral encolha se o texto for pequeno
barra_lateral.pack_propagate(False) 

area_conteudo = tk.Frame(janela, bg="white")
area_conteudo.pack(side="right", fill="both", expand=True)

# --- BOTÕES DO MENU ---
tk.Label(barra_lateral, text="MENU PRINCIPAL", font=("Arial", 14, "bold"), bg="#f0f0f0", fg="#444").pack(pady=(20, 20))

# Estilo padrão dos botões
btn_style = {'bg': '#e0e0e0', 'activebackground': '#d0d0d0', 'relief': 'flat', 'height': 2}

# Grupo Cadastros
tk.Label(barra_lateral, text="CADASTROS", font=("Arial", 9, "bold"), bg="#f0f0f0", fg="gray").pack(anchor="w", padx=10)
tk.Button(barra_lateral, text="📦  Produtos", command=ir_cadastro_item, **btn_style).pack(fill='x', pady=1, padx=5)
tk.Button(barra_lateral, text="👥  Clientes", command=ir_cadastro_cliente, **btn_style).pack(fill='x', pady=1, padx=5)
tk.Button(barra_lateral, text="🏭  Fornecedores", command=ir_cadastro_fornecedor, **btn_style).pack(fill='x', pady=1, padx=5)

tk.Frame(barra_lateral, height=10, bg="#f0f0f0").pack() # Espaçador

# Grupo Estoque
tk.Label(barra_lateral, text="MOVIMENTAÇÃO", font=("Arial", 9, "bold"), bg="#f0f0f0", fg="gray").pack(anchor="w", padx=10)
tk.Button(barra_lateral, text="📥  Entrada (+)", fg="green", command=ir_entrada, **btn_style).pack(fill='x', pady=1, padx=5)
tk.Button(barra_lateral, text="📤  Saída (-)", fg="red", command=ir_saida, **btn_style).pack(fill='x', pady=1, padx=5)
tk.Button(barra_lateral, text="🔄  Consignado", command=ir_consignado, **btn_style).pack(fill='x', pady=1, padx=5)

tk.Frame(barra_lateral, height=10, bg="#f0f0f0").pack() # Espaçador

# Grupo Gestão
tk.Label(barra_lateral, text="GESTÃO", font=("Arial", 9, "bold"), bg="#f0f0f0", fg="gray").pack(anchor="w", padx=10)
tk.Button(barra_lateral, text="🔍  Consulta Geral", command=ir_consulta, **btn_style).pack(fill='x', pady=1, padx=5)
tk.Button(barra_lateral, text="📜  Histórico", command=ir_historico, **btn_style).pack(fill='x', pady=1, padx=5)
tk.Button(barra_lateral, text="🛒  Compras", command=ir_compra, **btn_style).pack(fill='x', pady=1, padx=5)

# Botão Início e Sair
tk.Frame(barra_lateral, height=20, bg="#f0f0f0").pack()
tk.Button(barra_lateral, text="🏠  Início", command=mostrar_logo, bg="white").pack(fill='x', padx=5, pady=5)
tk.Button(barra_lateral, text="❌  Sair", command=sair, bg="#ffcccc", fg="red").pack(side='bottom', fill='x', padx=5, pady=20)

# --- Iniciar ---
mostrar_logo()
janela.mainloop()