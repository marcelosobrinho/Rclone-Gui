import subprocess
import os
import tkinter as tk
from tkinter import messagebox

class RcloneGoogleDriveConfigurator:
    def __init__(self, root):
        self.root = root
        self.root.title("Configurar e Mapear Google Drive com Rclone")
        self.remote_name = "Docs"  # Nome do remote será sempre "Docs"
        self.mount_point = "G:" if os.name == 'nt' else "/mnt/drive"
        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self.root, text=f"Remote: {self.remote_name}", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn_new_remote = tk.Button(self.root, text="Criar Remote e Mapear", command=self.create_and_mount_remote)
        self.btn_new_remote.pack(pady=5)

        self.btn_mount_remote = tk.Button(self.root, text="Mapear Remote", command=self.mount_remote)
        self.btn_mount_remote.pack(pady=5)

        self.btn_delete_remote = tk.Button(self.root, text="Deletar Remote", command=self.delete_remote)
        self.btn_delete_remote.pack(pady=5)

        self.btn_status_remote = tk.Button(self.root, text="Status do Remote", command=self.check_remote_status)
        self.btn_status_remote.pack(pady=5)

        self.btn_quit = tk.Button(self.root, text="Sair", command=self.root.quit)
        self.btn_quit.pack(pady=5)

    def create_and_mount_remote(self):
        """Cria o remote com o nome 'Docs' e monta automaticamente na letra G:"""
        try:
            # Criar o remote com Google Drive e nome 'Docs'
            subprocess.run(f'rclone config create {self.remote_name} drive', shell=True)

            # Verificar se foi criado corretamente
            remotes = subprocess.check_output("rclone listremotes", shell=True).decode('utf-8').strip()
            if self.remote_name not in remotes:
                messagebox.showerror("Erro", "Erro ao criar o remote. O remote não foi configurado corretamente.")
                return

            # Após a configuração, monta o remote automaticamente
            self.mount_remote(self.remote_name)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Erro", f"Erro ao criar o remote: {str(e)}")

    def mount_remote(self, remote_name=None):
        """Mapear o remote para a letra G: ou diretório padrão"""
        try:
            if not remote_name:
                remote_name = self.remote_name

            # Tentar montar o remote
            result = subprocess.run(f'rclone mount {remote_name}: {self.mount_point} --vfs-cache-mode full', shell=True, capture_output=True, text=True)

            # Verifica se o erro é relacionado ao WinFSP
            if "cgofuse: cannot find winfsp" in result.stderr:
                messagebox.showerror("Erro", "WinFSP não está instalado. Instale o WinFSP para montar o repositório no Windows.\nBaixe em: https://winfsp.dev/rel/")
            elif result.returncode != 0:
                if "interactive login" in result.stderr:
                    messagebox.showerror("Erro", "O Rclone está pedindo o login interativo novamente. Certifique-se de que o token foi salvo corretamente.")
                else:
                    messagebox.showerror("Erro", f"Erro ao mapear o remote: {result.stderr}")
            else:
                messagebox.showinfo("Sucesso", f"Remote '{remote_name}' mapeado com sucesso em {self.mount_point}!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Erro", f"Erro ao mapear o remote: {str(e)}")

    def delete_remote(self):
        """Desmontar e deletar o remote"""
        try:
            # Desmontar a unidade antes de deletar o remote
            if os.name == 'nt':
                subprocess.run(f'rmdir {self.mount_point}', shell=True)
            else:
                subprocess.run(f'umount {self.mount_point}', shell=True)

            # Deletar o remote
            subprocess.run(f'rclone config delete {self.remote_name}', shell=True)
            messagebox.showinfo("Sucesso", f"Remote '{self.remote_name}' deletado e desmontado com sucesso!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Erro", f"Erro ao deletar o remote: {str(e)}")

    def check_remote_status(self):
        """Checar o status do remote (se está acessível ou não)"""
        try:
            # Verifica se o remote está acessível
            result = subprocess.run(f'rclone lsd {self.remote_name}:', shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                messagebox.showinfo("Status do Remote", f"O remote '{self.remote_name}' está acessível e funcionando.")
            else:
                messagebox.showerror("Erro no Remote", f"Erro ao acessar o remote '{self.remote_name}': {result.stderr}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Erro", f"Erro ao verificar o status do remote: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = RcloneGoogleDriveConfigurator(root)
    root.mainloop()
