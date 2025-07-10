import flet as ft
from app.logic import set_etapa, validar_arquivo_pdf, estado
from pathlib import Path

def main(page: ft.Page):
    # Importar e definir o flet_page global
    from app.logic import flet_page
    import app.logic
    app.logic.flet_page = page
    
    page.title = "Analisador de PDF - Flet"
    page.bgcolor = "#FFFFFF"
    page.fonts = {"redhat": "https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@400;700&display=swap"}
    page.theme = ft.Theme(font_family="Gotham")
    page.window.width = 900
    page.window.height = 800
    page.window.resizable = False

    
    # Configurar FilePicker para abrir arquivos
    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            valido, mensagem = validar_arquivo_pdf(file_path)
            if valido:
                estado["file_path"] = file_path  # type: ignore
                set_etapa(4)  # Ir para tela de confirmação
            else:
                page.add(ft.SnackBar(ft.Text(f"Arquivo inválido: {mensagem}"), bgcolor="#d32f2f"))
                page.update()
    
    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(pick_files_dialog)
    
    # Configurar FilePickers para salvar arquivos
    def save_txt_result(e: ft.FilePickerResultEvent):
        if e.path:
            import app.logic
            app.logic.salvar_txt_em_local(e.path)
    
    def save_csv_result(e: ft.FilePickerResultEvent):
        if e.path:
            import app.logic
            app.logic.salvar_csv_em_local(e.path)
    
    save_txt_dialog = ft.FilePicker(on_result=save_txt_result)
    save_csv_dialog = ft.FilePicker(on_result=save_csv_result)
    
    page.overlay.extend([save_txt_dialog, save_csv_dialog])
    
    # Função para abrir o FilePicker
    def abrir_file_picker(e=None):
        pick_files_dialog.pick_files(
            dialog_title="Selecione um arquivo PDF",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["pdf"],
            allow_multiple=False,
        )
    
    # Funções para abrir janelas de salvar
    def abrir_save_txt(e=None):
        nome_arquivo = Path(estado["file_path"]).stem if estado["file_path"] else "relatorio"
        save_txt_dialog.save_file(
            dialog_title="Salvar arquivo TXT",
            file_name=f"{nome_arquivo}_relatorio.txt",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["txt"],
        )
    
    def abrir_save_csv(e=None):
        nome_arquivo = Path(estado["file_path"]).stem if estado["file_path"] else "relatorio"
        save_csv_dialog.save_file(
            dialog_title="Salvar arquivo CSV",
            file_name=f"{nome_arquivo}_dados.csv",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["csv"],
        )
    
    # Conectar as funções ao logic
    setattr(app.logic, 'pick_file', abrir_file_picker)
    app.logic.save_txt_dialog_func = abrir_save_txt
    app.logic.save_csv_dialog_func = abrir_save_csv
    
    page.update()
    
    # Inicializar com a tela de boas-vindas usando o sistema de navegação
    set_etapa(1)

if __name__ == "__main__":
    Path("results").mkdir(exist_ok=True)
    ft.app(target=main, view=ft.AppView.FLET_APP) 