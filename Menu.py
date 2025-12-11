import tkinter as tk
from tkinter import messagebox 
import banco 
import login # Importa a tela de login que criamos

# Variável global para saber quem está logado
USUARIO_ATUAL = {} 

# --- Inicialização do Banco ---
try:
    banco.inicializar_banco()
except Exception as e:
    messagebox.showerror("Erro Fatal", f"Erro ao iniciar banco:\n{e}")

# =============================================================================
# SISTEMA DE NAVEGAÇÃO
# =============================================================================
def mostrar_tela(funcao_modulo):
    for widget in area_conteudo.winfo_children():
        widget.destroy()
    try:
        funcao_modulo(area_conteudo)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar módulo:\n{e}")
        mostrar_logo()

def mostrar_logo():
    # Limpa a área
    for widget in area_conteudo.winfo_children(): widget.destroy()
    
    try:
        # Tenta carregar o Dashboard Financeiro
        from Modulos_Estoque import dashboard
        # Precisamos passar o 'area_conteudo' como pai
        dashboard.abrir_dashboard(area_conteudo)
    except ImportError:
        # Se o arquivo dashboard.py não existir, mostra o padrão antigo
        tk.Label(area_conteudo, text=f"Bem-vindo, {USUARIO_ATUAL.get('nome', 'Usuário')}!", font=("Arial", 30), bg="white").pack(expand=True)
    except Exception as e:
        messagebox.showerror("Erro Dashboard", f"Erro ao carregar painel: {e}")
        
def sair():
    janela.quit()

# =============================================================================
# WRAPPERS (CHAMADAS DOS MÓDULOS)
# =============================================================================
def ir_admin_usuarios():
    from Modulos_Admin import admin_usuarios
    mostrar_tela(admin_usuarios.abrir_admin_usuarios)

def ir_cadastro_item():
    from Modulos_Cadastro import cadastro
    mostrar_tela(cadastro.abrir_janela_cadastro)

def ir_cadastro_cliente():
    from Modulos_Cadastro import cadastro_clientes
    mostrar_tela(cadastro_clientes.abrir_janela_cadastro_cliente)

def ir_cadastro_fornecedor():
    from Modulos_Cadastro import cadastro_fornecedores
    mostrar_tela(cadastro_fornecedores.abrir_janela_fornecedores)

def ir_entrada():
    from Modulos_Estoque import entrada_estoque
    mostrar_tela(entrada_estoque.abrir_janela_entrada)

def ir_saida():
    from Modulos_Estoque import saida_estoque
    mostrar_tela(saida_estoque.abrir_janela_saida)

def ir_consignado():
    from Modulos_Estoque import consignado
    mostrar_tela(consignado.abrir_janela_consignado)

def ir_consulta():
    from Modulos_Estoque import consulta
    mostrar_tela(consulta.abrir_janela_consulta)

def ir_historico():
    from Modulos_Estoque import historico_saidas
    mostrar_tela(historico_saidas.abrir_janela_historico)

def ir_compra():
    messagebox.showinfo("Info", "Módulo em desenvolvimento.")

# =============================================================================
# FUNÇÃO QUE INICIA O MENU APÓS O LOGIN
# =============================================================================
def iniciar_menu_principal(dados_usuario):
    # dados_usuario vem do banco: (id, username, nivel, nome)
    # Precisamos tratar isso com cuidado
    
    global USUARIO_ATUAL
    
    # Lógica inteligente para o nome:
    # Se o banco retornou 4 campos e o 4º (nome) não for vazio, usa ele.
    # Senão, usa o username (login).
    if len(dados_usuario) > 3 and dados_usuario[3]:
        nome_exibicao = dados_usuario[3] # Nome Real
    else:
        nome_exibicao = dados_usuario[1] # Login (ex: admin)

    USUARIO_ATUAL = {
        'id': dados_usuario[0], 
        'nome': nome_exibicao, 
        'nivel': dados_usuario[2]
    }
    
    global janela, area_conteudo 
    
    janela = tk.Tk()
    janela.title(f"Sistema de Gestão - Usuário: {USUARIO_ATUAL['nome']}")
    janela.state('zoomed')

    # Layout
    barra_lateral = tk.Frame(janela, bg="#f0f0f0", width=250)
    barra_lateral.pack(side="left", fill="y")
    barra_lateral.pack_propagate(False) 

    area_conteudo = tk.Frame(janela, bg="white")
    area_conteudo.pack(side="right", fill="both", expand=True)

    # --- MENU LATERAL ---
    tk.Label(barra_lateral, text="MENU", font=("Arial", 14, "bold"), bg="#f0f0f0", fg="#444").pack(pady=(20, 10))
    
    btn_style = {'bg': '#e0e0e0', 'activebackground': '#d0d0d0', 'relief': 'flat', 'height': 2}

    # 1. ADMINISTRAÇÃO (Apenas para admins)
    if USUARIO_ATUAL['nivel'] == 'admin':
        tk.Label(barra_lateral, text="ADMINISTRAÇÃO", font=("Arial", 8, "bold"), bg="#f0f0f0", fg="red").pack(anchor="w", padx=10, pady=(10,0))
        tk.Button(barra_lateral, text="🔐 Usuários e Acessos", command=ir_admin_usuarios, **btn_style).pack(fill='x', pady=1, padx=5)

    # 2. CADASTROS
    tk.Label(barra_lateral, text="CADASTROS", font=("Arial", 8, "bold"), bg="#f0f0f0", fg="gray").pack(anchor="w", padx=10, pady=(10,0))
    tk.Button(barra_lateral, text="📦 Produtos", command=ir_cadastro_item, **btn_style).pack(fill='x', pady=1, padx=5)
    tk.Button(barra_lateral, text="👥 Clientes", command=ir_cadastro_cliente, **btn_style).pack(fill='x', pady=1, padx=5)
    tk.Button(barra_lateral, text="🏭 Fornecedores", command=ir_cadastro_fornecedor, **btn_style).pack(fill='x', pady=1, padx=5)

    # 3. ESTOQUE
    tk.Label(barra_lateral, text="ESTOQUE", font=("Arial", 8, "bold"), bg="#f0f0f0", fg="gray").pack(anchor="w", padx=10, pady=(10,0))
    tk.Button(barra_lateral, text="📥 Entrada", fg="green", command=ir_entrada, **btn_style).pack(fill='x', pady=1, padx=5)
    tk.Button(barra_lateral, text="📤 Saída", fg="red", command=ir_saida, **btn_style).pack(fill='x', pady=1, padx=5)
    tk.Button(barra_lateral, text="🔄 Consignado", command=ir_consignado, **btn_style).pack(fill='x', pady=1, padx=5)

    # 4. GESTÃO
    tk.Label(barra_lateral, text="GESTÃO", font=("Arial", 8, "bold"), bg="#f0f0f0", fg="gray").pack(anchor="w", padx=10, pady=(10,0))
    tk.Button(barra_lateral, text="🔍 Consulta", command=ir_consulta, **btn_style).pack(fill='x', pady=1, padx=5)
    tk.Button(barra_lateral, text="📜 Histórico", command=ir_historico, **btn_style).pack(fill='x', pady=1, padx=5)

    # Rodapé
    tk.Frame(barra_lateral, height=20, bg="#f0f0f0").pack()
    tk.Button(barra_lateral, text="🏠 Painel Inicial", command=mostrar_logo, bg="white").pack(fill='x', padx=5, pady=2)
    tk.Label(barra_lateral, text=f"👤 {USUARIO_ATUAL['nome']}", bg="#f0f0f0", fg="blue").pack(side="bottom", pady=5)
    tk.Button(barra_lateral, text="❌ Sair", command=sair, bg="#ffcccc", fg="red").pack(side='bottom', fill='x', padx=5, pady=5)

    mostrar_logo()
    janela.mainloop()

# =============================================================================
# PONTO DE PARTIDA (MAIN)
# =============================================================================
if __name__ == "__main__":
    # Cria a janela de login (invisível no inicio, mas o app desenha nela)
    root_login = tk.Tk()
    
    # Callback: O que fazer quando o login der certo?
    def login_sucesso(dados_usuario):
        # dados_usuario = (id, login, nivel, nome) 
        iniciar_menu_principal(dados_usuario)

    # Inicia App de Login
    try:
        app = login.LoginApp(root_login, login_sucesso)
        root_login.mainloop()
    except Exception as e:
        messagebox.showerror("Erro Crítico", f"Falha ao iniciar login: {e}")