import tkinter as tk
from tkinter import messagebox
import banco

class LoginApp:
    def __init__(self, root, on_success_callback):
        self.root = root
        self.on_success = on_success_callback
        
        self.root.title("Login - Sistema de Estoque")
        self.root.geometry("400x450")
        self.root.resizable(False, False)
        self.root.configure(bg="white")

        # --- LAYOUT ---
        
        # Logo (Emoji ou Imagem)
        tk.Label(self.root, text="🔐", font=("Arial", 50), bg="white").pack(pady=(40, 10))
        tk.Label(self.root, text="Acesso ao Sistema", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        # Campos
        frame_login = tk.Frame(self.root, bg="white")
        frame_login.pack(pady=20)

        tk.Label(frame_login, text="Usuário:", bg="white", font=("Arial", 10)).pack(anchor="w")
        self.entry_user = tk.Entry(frame_login, width=30, font=("Arial", 11))
        self.entry_user.pack(pady=(0, 10))

        tk.Label(frame_login, text="Senha:", bg="white", font=("Arial", 10)).pack(anchor="w")
        self.entry_pass = tk.Entry(frame_login, width=30, font=("Arial", 11), show="*")
        self.entry_pass.pack(pady=(0, 20))
        
        # Atalho: Apertar Enter para entrar
        self.entry_pass.bind('<Return>', lambda e: self.verificar_login())

        # Botão Entrar
        tk.Button(self.root, text="ENTRAR", command=self.verificar_login, 
                  bg="#0056b3", fg="white", font=("Arial", 11, "bold"), width=20, height=2).pack()

        tk.Label(self.root, text="© Sistema de Gestão v1.0", bg="white", fg="gray").pack(side="bottom", pady=10)

    def verificar_login(self):
        usuario = self.entry_user.get().strip()
        senha = self.entry_pass.get().strip()

        if not usuario or not senha:
            messagebox.showwarning("Aviso", "Por favor, digite usuário e senha.")
            return

        conexao = None
        try:
            conexao = banco.conectar()
            if not conexao:
                messagebox.showerror("Erro Crítico", "Sem conexão com o banco de dados.")
                return
            
            cursor = conexao.cursor()
            
            # Busca usuário, nível e NOME (sua alteração correta aqui)
            cursor.execute("SELECT id, username, nivel, nome FROM usuarios WHERE username = %s AND password_hash = %s", (usuario, senha))
            user_data = cursor.fetchone()
            
            if user_data:
                # Login Sucesso!
                # user_data = (id, login, nivel, nome)
                self.root.destroy() # Fecha a janela de login
                self.on_success(user_data) # Manda os dados para o menu.py iniciar
            else:
                # --- MUDANÇA AQUI: Mensagem personalizada ---
                messagebox.showwarning(
                    "Acesso Negado", 
                    "Usuário ou senha incorretos.\n\nCaso não tenha cadastro ou tenha esquecido a senha, favor contatar o Administrador do sistema."
                )

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao tentar login: {e}")
        finally:
            if conexao: conexao.close()