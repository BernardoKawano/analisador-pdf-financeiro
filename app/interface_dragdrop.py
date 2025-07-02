#!/usr/bin/env python3
"""
Interface Gráfica Moderna, Modular e Profissional para Upload e Análise de PDF
- Drag & Drop real (tkinterdnd2)
- Feedback visual, animações, acessibilidade
- Modular: DropZoneFrame, ProgressFrame, CardFrame, ResultFrame
- Integração com AnalisadorPDF
"""
import os
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD

try:
    from app.sergio import AnalisadorPDF
except ImportError:
    AnalisadorPDF = None  # Simulação se não existir

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS  # type: ignore
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative)

def abrir_local(caminho):
    # Abre o local do arquivo no sistema operacional
    if sys.platform.startswith('win'):
        os.startfile(os.path.dirname(caminho))
    elif sys.platform == 'darwin':
        os.system(f'open "{os.path.dirname(caminho)}"')
    else:
        os.system(f'xdg-open "{os.path.dirname(caminho)}"')

def analisar_pdf_simulado(pdf_path, callback):
    # Simula processamento e salva relatório
    nome = Path(pdf_path).stem
    pasta = Path('results')
    pasta.mkdir(exist_ok=True)
    relatorio = pasta / f"{nome}_relatorio.txt"
    with open(relatorio, 'w', encoding='utf-8') as f:
        f.write(f"Relatório de análise do PDF: {pdf_path}\nStatus: OK\n")
    callback(str(relatorio))

class DropZoneFrame(tk.Frame):
    def __init__(self, master, on_file_selected, **kwargs):
        super().__init__(master, **kwargs)
        self.on_file_selected = on_file_selected
        self.configure(bg="#232946", bd=0, relief="flat")
        self.hover = False
        self.icon_label = tk.Label(self, text="🔽", font=("Arial", 60, "bold"), bg="#232946", fg="#3DDC97")
        self.icon_label.pack(pady=(30, 0))
        self.text_label = tk.Label(self, text="Arraste e solte o PDF aqui", font=("Arial", 16, "bold"), bg="#232946", fg="#EDEDED")
        self.text_label.pack(pady=(10, 0))
        self.sub_label = tk.Label(self, text="ou clique em Selecionar arquivo", font=("Arial", 12), bg="#232946", fg="#B8C1EC")
        self.sub_label.pack(pady=(0, 10))
        self.file_label = tk.Label(self, text="", font=("Arial", 10), bg="#232946", fg="#F6C177")
        self.file_label.pack(pady=(5, 0))
        self.btn_select = ttk.Button(self, text="Selecionar arquivo", command=self.select_file, style="Accent.TButton")
        self.btn_select.pack(pady=(15, 0))
        self.drop_target_register(DND_FILES)  # type: ignore
        self.dnd_bind('<<Drop>>', self.on_drop)  # type: ignore
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.icon_label.bind("<Enter>", self.on_enter)
        self.icon_label.bind("<Leave>", self.on_leave)
        self.text_label.bind("<Enter>", self.on_enter)
        self.text_label.bind("<Leave>", self.on_leave)
        self.sub_label.bind("<Enter>", self.on_enter)
        self.sub_label.bind("<Leave>", self.on_leave)
        self.file_label.bind("<Enter>", self.on_enter)
        self.file_label.bind("<Leave>", self.on_leave)
    def on_enter(self, event=None):
        self.hover = True
        self.configure(bg="#1A1A2E")
        self.icon_label.configure(bg="#1A1A2E", fg="#F6C177")
        self.text_label.configure(bg="#1A1A2E", fg="#F6C177")
        self.sub_label.configure(bg="#1A1A2E", fg="#F6C177")
        self.file_label.configure(bg="#1A1A2E", fg="#F6C177")
    def on_leave(self, event=None):
        self.hover = False
        self.configure(bg="#232946")
        self.icon_label.configure(bg="#232946", fg="#3DDC97")
        self.text_label.configure(bg="#232946", fg="#EDEDED")
        self.sub_label.configure(bg="#232946", fg="#B8C1EC")
        self.file_label.configure(bg="#232946", fg="#F6C177")
    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        if files and files[0].lower().endswith('.pdf') and os.path.isfile(files[0]):
            self.file_label.config(text=Path(files[0]).name)
            self.on_file_selected(files[0])
        else:
            self.file_label.config(text="Arquivo inválido!", fg="#FF6F61")
            self.after(1200, lambda: self.file_label.config(text="", fg="#F6C177"))
    def select_file(self):
        file = filedialog.askopenfilename(
            title="Selecionar arquivo PDF",
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")]
        )
        if file:
            self.file_label.config(text=Path(file).name)
            self.on_file_selected(file)

class ProgressFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg="#232946")
        self.label = tk.Label(self, text="Analisando PDF...", font=("Arial", 12, "bold"), bg="#232946", fg="#F6C177")
        self.label.pack(pady=(10, 0))
        self.progress = ttk.Progressbar(self, mode='indeterminate', length=300)
        self.progress.pack(pady=(10, 10))
        self.progress.start(10)

class CardFrame(tk.Frame):
    def __init__(self, master, title, value, color, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg="#232946", highlightbackground=color, highlightthickness=2, bd=0)
        self.title = tk.Label(self, text=title, font=("Arial", 11, "bold"), bg="#232946", fg=color)
        self.title.pack(pady=(8, 0))
        self.value = tk.Label(self, text=value, font=("Consolas", 16, "bold"), bg="#232946", fg="#EDEDED")
        self.value.pack(pady=(0, 8))
        self.attributes = 0
        self.after(10, self.fade_in)
    def fade_in(self):
        if self.attributes < 10:
            fg = f"#{hex(35 + self.attributes*22)[2:]:>02}C1EC"
            self.value.config(fg=fg)
            self.attributes += 1
            self.after(30, self.fade_in)
        else:
            self.value.config(fg="#EDEDED")

class ResultFrame(tk.Frame):
    def __init__(self, master, relatorio, caminho, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg="#232946")
        self.path_label = tk.Label(self, text=f"Relatório salvo em:\n{caminho}", font=("Arial", 11, "bold"), bg="#232946", fg="#B8C1EC", cursor="hand2")
        self.path_label.pack(pady=(40, 0))
        self.path_label.bind("<Button-1>", lambda e: self.abrir_local(caminho))

    def parse_relatorio(self, relatorio):
        def extrai(tag):
            for linha in relatorio.splitlines():
                if tag in linha:
                    return linha.split(":")[-1].strip()
            return "0,00"
        return (
            extrai("Total Demonstrativo"),
            extrai("Total FUNARPEN"),
            extrai("Total ISSQN"),
            extrai("Total Líquido")
        )
    def abrir_local(self, caminho):
        import subprocess, platform
        pasta = str(Path(caminho).parent.absolute())
        if platform.system() == "Windows":
            subprocess.run(["explorer", pasta])
        elif platform.system() == "Darwin":
            subprocess.run(["open", pasta])
        else:
            subprocess.run(["xdg-open", pasta])

class DragDropPDFApp(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#232946")
        self.pack(fill="both", expand=True)
        self.master = master
        self.selected_file = None
        self.relatorio_path = None
        self.setup_styles()
        self.create_widgets()
        self.set_state("dropzone")
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Accent.TButton", font=("Arial", 12, "bold"), background="#3DDC97", foreground="#232946")
        style.map("Accent.TButton",
                  background=[("active", "#F6C177"), ("disabled", "#B8C1EC")],
                  foreground=[("active", "#232946")])
    def create_widgets(self):
        self.dropzone = DropZoneFrame(self, self.on_file_selected)
        self.dropzone.pack(pady=(32, 24))
        self.btn_analisar = ttk.Button(self, text="ANALISAR PDF", style="Accent.TButton", command=self.analisar_pdf, state="disabled")
        self.btn_analisar.pack(pady=(0, 40))
        self.progress_frame = None
        self.result_frame = None
    def set_state(self, state):
        if state == "dropzone":
            self.dropzone.lift()
            self.btn_analisar.config(state="disabled")
            if self.progress_frame:
                self.progress_frame.pack_forget()
            if self.result_frame:
                self.result_frame.pack_forget()
        elif state == "ready":
            self.btn_analisar.config(state="normal")
        elif state == "processing":
            self.btn_analisar.config(state="disabled")
            self.progress_frame = ProgressFrame(self)
            self.progress_frame.pack(pady=(0, 30))
        elif state == "result":
            if self.progress_frame:
                self.progress_frame.pack_forget()
            if self.result_frame:
                self.result_frame.pack_forget()
            self.result_frame = ResultFrame(self, self.relatorio, self.relatorio_path)
            self.result_frame.pack(pady=(40, 0))
    def on_file_selected(self, file):
        self.selected_file = file
        self.set_state("ready")
    def analisar_pdf(self):
        if not self.selected_file:
            return
        self.set_state("processing")
        threading.Thread(target=self.simular_backend, daemon=True).start()
    def simular_backend(self):
        self.after(1800, self.finalizar_analise)
    def finalizar_analise(self):
        if AnalisadorPDF and self.selected_file:
            analisador = AnalisadorPDF(str(self.selected_file))
            analisador.analisar_pdf()
            self.relatorio = analisador.gerar_relatorio()
        else:
            self.relatorio = (
                "Total Demonstrativo: 1.234,56\n"
                "Total FUNARPEN: 123,45\n"
                "Total ISSQN: 67,89\n"
                "Total Líquido: 1.043,22\n"
            )
        if self.selected_file:
            nome_arquivo = Path(self.selected_file).stem
        else:
            nome_arquivo = "relatorio"
        self.relatorio_path = Path("results") / f"{nome_arquivo}_relatorio.txt"
        Path("results").mkdir(exist_ok=True)
        with open(self.relatorio_path, "w", encoding="utf-8") as f:
            f.write(self.relatorio)
        self.set_state("result")

def main():
    root = TkinterDnD.Tk()
    root.title("Analisador de PDF - Profissional")
    root.geometry("720x600")
    root.configure(bg="#232946")
    root.minsize(600, 500)
    root.option_add("*Font", "Arial 11")
    app = DragDropPDFApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 