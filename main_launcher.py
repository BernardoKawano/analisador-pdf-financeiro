# main_launcher.py
# Ponto de entrada principal da aplicação Analisador PDF Financeiro.
import subprocess
import sys
import os

def main():
    # Executa a interface Flet
    python_exe = sys.executable
    script_path = os.path.join(os.path.dirname(__file__), "main_flet.py")
    subprocess.run([python_exe, script_path])

if __name__ == "__main__":
    main() 