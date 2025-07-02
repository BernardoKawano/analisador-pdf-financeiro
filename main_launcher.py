import subprocess
import sys
import os

def install_and_run():
    # Instala dependências se necessário
    try:
        import PyPDF2
        import tkinterdnd2
    except ImportError:
        print("Instalando dependências...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependências instaladas com sucesso!")

    # Executa a interface
    try:
        from app.interface_dragdrop import main
        main()
    except Exception as e:
        print("Erro ao iniciar a interface:", e)
        print("Tente executar novamente ou verifique se o Python está instalado.")

if __name__ == "__main__":
    print("Bem-vindo ao Analisador de PDF!")
    print("Se for a primeira vez, aguarde a instalação automática dos requisitos.")
    install_and_run() 