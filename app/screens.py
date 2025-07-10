# app/screens.py
import flet as ft
from app.components import *
from pathlib import Path
from app.logic import (
    abrir_historico, abrir_upload, baixar_txt, baixar_csv,
    voltar_nova_analise, ir_para_exportacao, voltar_pagina_anterior, ir_para_home,
    estado, gerar_miniatura_pdf, set_etapa, carregar_historico, carregar_historico_ordenado, remover_entrada_historico
)

# Função local para copiar valor para a área de transferência
from app.logic import flet_page

def copiar_para_clipboard(valor, e=None):
    if flet_page and hasattr(flet_page, 'set_clipboard') and callable(flet_page.set_clipboard):
        flet_page.set_clipboard(str(valor))
        if hasattr(flet_page, 'add') and callable(flet_page.add):
            flet_page.add(ft.SnackBar(ft.Text("Valor copiado!"), bgcolor="#4caf50"))
            if hasattr(flet_page, 'update') and callable(flet_page.update):
                flet_page.update()

# Funções de construção das telas principais

def tela_boas_vindas():
    return ft.Column([
        ft.Container(
            ft.Image(src="images/Logotipo-LumaLector.png", width=450, height=120),  # Diminuído 30%: 585→410, 135→95
            alignment=ft.alignment.center,
            margin=ft.margin.only(top=30, bottom=30)  # Espaço diminuído: 60→40 (-20px)
        ),
        ft.Container(
            ft.Text(
                spans=[
                    ft.TextSpan(
                        "Olá, seja bem-vindo ",
                        style=ft.TextStyle(
                            color="#004054",
                            size=32,  # Aumentado em 8: 30→38
                            font_family="Gotham",
                            weight=ft.FontWeight.NORMAL,
                        ),
                    ),
                    ft.TextSpan(
                        "Sergio!",
                        style=ft.TextStyle(
                            color="#004054",
                            size=38,  # Aumentado em 8: 30→38
                            font_family="Gotham",
                            weight=ft.FontWeight.BOLD,
                        ),
                    ),
                ],
                text_align=ft.TextAlign.CENTER,
            ),
            margin=ft.margin.only(bottom=40)  # Espaço até os botões: 60→40
        ),
        ft.Row([
            BotaoCardMenu("Histórico de", "análises", "images/historyiconsvg.svg", on_click=abrir_historico),
            BotaoCardMenu("Analisar um", "Documento", "images/searchiconsvg.svg", on_click=abrir_upload),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=32),
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

def tela_upload():
    from app.logic import pick_file
    return ft.Stack([
        # Conteúdo principal da tela
        ft.Container(
            ft.Column([
                ft.Container(height=120),
                ft.Text(
                    "Adicione o documento que será analisado no ",
                    color="#004054",
                    size=20,
                    font_family="Gotham",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "formato .PDF",
                    color="#004054",
                    size=20,
                    font_family="Gotham",
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=32),
                BotaoPrincipal("SELECIONE O ARQUIVO", on_click=pick_file),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            # Garantir que não interfira com os botões
            margin=ft.margin.only(top=80, left=80, right=80, bottom=20)
        ),
        # Logo
        ft.Container(
            ft.Image(src="images/Logotipo-LumaLector.png", width=260, height=60),
            alignment=ft.alignment.top_center,
            margin=ft.margin.only(top=32)
        ),
        # Botões de navegação com z-index mais alto
        ft.Container(
            ft.Row([
                BotaoIconeCircular("arrow_back", on_click=voltar_pagina_anterior, bgcolor="#008EBC", icon_color="#FFFFFF", size=56),
                ft.Container(expand=True),  # Espaçador
                BotaoIconeCircular("home", on_click=ir_para_home, bgcolor="#008EBC", icon_color="#FFFFFF", size=56),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            alignment=ft.alignment.top_center,
            margin=ft.margin.only(top=24, left=24, right=24),
            height=56,
        ),
    ])

def tela_confirmacao():
    nome_arquivo = Path(estado["file_path"]).name if estado["file_path"] else "(nenhum arquivo)"
    nome_sem_extensao = Path(estado["file_path"]).stem if estado["file_path"] else "(nenhum arquivo)"
    miniatura_path = None
    if estado["file_path"]:
        miniatura_path = gerar_miniatura_pdf(estado["file_path"])
    
    def avancar_para_analise(e=None):
        import threading
        import time
        from app.logic import adicionar_ao_historico
        from app.analise_pdf import AnalisadorPDF
        from pathlib import Path
        
        # Ir para tela de análise
        set_etapa(5)
        
        def executar_analise():
            try:
                # Verificar se o arquivo existe
                if not estado["file_path"]:
                    raise ValueError("Nenhum arquivo selecionado")
                
                # Criar analisador PDF
                analisador = AnalisadorPDF(estado["file_path"])
                
                # Executar análise
                sucesso = analisador.analisar_pdf()
                
                if sucesso:
                    # Obter totais da análise
                    totais = analisador.calcular_totais()
                    totais_diarios = analisador.calcular_totais_diarios()
                    
                    # Calcular intervalo de datas
                    datas = [t.data for t in totais_diarios if t.data != "Data não identificada"]
                    if datas:
                        datas_ordenadas = sorted(datas)
                        intervalo_datas = f"{datas_ordenadas[0]} - {datas_ordenadas[-1]}" if len(datas_ordenadas) > 1 else datas_ordenadas[0]
                    else:
                        intervalo_datas = "Não identificado"
                    
                    # Contar páginas do PDF
                    try:
                        import PyPDF2
                        with open(estado["file_path"], 'rb') as arquivo:
                            leitor = PyPDF2.PdfReader(arquivo)
                            qtd_pgs = str(len(leitor.pages))
                    except:
                        qtd_pgs = "Não identificado"
                    
                    # Formatar valores para exibição
                    resumo_dados = {
                        "qtd_pgs": qtd_pgs,
                        "intervalo_datas": intervalo_datas,
                        "valor_liquido": f"R$ {totais['valor_liquido']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                        "valor_demonstrativo": f"R$ {totais['total_demonstrativos']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                        "valor_funarpen": f"R$ {totais['total_funarpen']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                        "valor_issqn": f"R$ {totais['total_issqn']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                    }
                    
                    estado["resumo"] = resumo_dados  # type: ignore
                    adicionar_ao_historico(nome_sem_extensao, resumo_dados)
                    
                    # Gerar relatório
                    analisador.gerar_relatorio(estado["file_path"])
                    
                    # Ir para tela de resumo
                    set_etapa(6)
                else:
                    # Erro na análise - voltar para tela anterior
                    from app.logic import flet_page
                    if flet_page and hasattr(flet_page, 'add') and callable(flet_page.add):
                        flet_page.add(ft.SnackBar(ft.Text("Erro na análise do PDF"), bgcolor="#d32f2f"))
                        if hasattr(flet_page, 'update') and callable(flet_page.update):
                            flet_page.update()
                    set_etapa(4)  # Voltar para tela de confirmação
                    
            except Exception as e:
                # Erro na análise - mostrar erro e voltar
                from app.logic import flet_page
                if flet_page and hasattr(flet_page, 'add') and callable(flet_page.add):
                    flet_page.add(ft.SnackBar(ft.Text(f"Erro na análise: {str(e)}"), bgcolor="#d32f2f"))
                    if hasattr(flet_page, 'update') and callable(flet_page.update):
                        flet_page.update()
                set_etapa(4)  # Voltar para tela de confirmação
        
        # Executar análise em thread separada
        thread = threading.Thread(target=executar_analise)
        thread.daemon = True
        thread.start()
    
    return ft.Stack([
        # Conteúdo principal da tela
        ft.Container(
            ft.Column([
                ft.Container(height=120),
                ft.Container(
                    ft.Image(src=miniatura_path if miniatura_path else "images/placeholder.png", width=180, height=240, fit=ft.ImageFit.CONTAIN) if miniatura_path else ft.Text("MINIATURA\nPRIMEIRA\nPAGINA", color="#004054", size=16, font_family="Gotham", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    width=220,
                    height=280,
                    bgcolor="#FFFFFF",
                    border_radius=24,
                    shadow=ft.BoxShadow(blur_radius=18, color="#00000022", offset=ft.Offset(0, 6)),
                    alignment=ft.alignment.center,
                ),
                ft.Text(f'"{nome_sem_extensao}"', color="#004054", size=18, font_family="Gotham", text_align=ft.TextAlign.CENTER),
                ft.Container(height=24),
                BotaoPrincipal("ANALISAR", on_click=avancar_para_analise),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            margin=ft.margin.only(top=80, left=80, right=80, bottom=20)
        ),
        # Logo
        ft.Container(
            ft.Image(src="images/Logotipo-LumaLector.png", width=260, height=60),
            alignment=ft.alignment.top_center,
            margin=ft.margin.only(top=32)
        ),
        # Botões de navegação com z-index mais alto
        ft.Container(
            ft.Row([
                BotaoIconeCircular("arrow_back", on_click=voltar_pagina_anterior, bgcolor="#008EBC", icon_color="#FFFFFF", size=56),
                ft.Container(expand=True),  # Espaçador
                BotaoIconeCircular("home", on_click=ir_para_home, bgcolor="#008EBC", icon_color="#FFFFFF", size=56),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            alignment=ft.alignment.top_center,
            margin=ft.margin.only(top=24, left=24, right=24),
            height=56,
        ),
    ])

def tela_analisando():
    return ft.Stack([
        # Conteúdo principal da tela
        ft.Container(
            ft.Column([
                ft.Container(height=120),
                ft.Container(
                    ft.Image(
                        src="images/loadingscene.gif", 
                        width=200, 
                        height=200,
                        fit=ft.ImageFit.CONTAIN
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=20)
                ),
                ft.Text("Analisando documentos...", color="#004054", size=20, font_family="Gotham", text_align=ft.TextAlign.CENTER),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            margin=ft.margin.only(top=80, left=80, right=80, bottom=20)
        ),
        # Logo
        ft.Container(
            ft.Image(src="images/Logotipo-LumaLector.png", width=260, height=60),
            alignment=ft.alignment.top_center,
            margin=ft.margin.only(top=32)
        ),
        # Botões de navegação com z-index mais alto
        ft.Container(
            ft.Row([
                BotaoIconeCircular("arrow_back", on_click=voltar_pagina_anterior, bgcolor="#008EBC", icon_color="#FFFFFF", size=56),
                ft.Container(expand=True),  # Espaçador
                BotaoIconeCircular("home", on_click=ir_para_home, bgcolor="#008EBC", icon_color="#FFFFFF", size=56),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            alignment=ft.alignment.top_center,
            margin=ft.margin.only(top=24, left=24, right=24),
            height=56,
        ),
    ])

def tela_resumo():
    resumo = estado["resumo"] or {
        "qtd_pgs": "-",
        "intervalo_datas": "-",
        "valor_liquido": "-",
        "valor_demonstrativo": "-",
        "valor_funarpen": "-",
        "valor_issqn": "-"
    }
    def LinhaResumo(label, valor, width=200):
        return ft.Row([
            ft.Text(label, color="#004054", size=22, font_family="Gotham"),
            ft.Container(
                ft.Row([
                    ft.Text(valor, color="#004054", size=20, font_family="Gotham"),
                    ft.IconButton(
                        icon="content_copy", 
                        icon_color="#004054", 
                        icon_size=22, 
                        tooltip="Copiar", 
                        on_click=lambda e, v=valor: copiar_para_clipboard(v, e)
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=0),
                bgcolor="#E8E8E8",
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                width=width,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
    return ft.Stack([
        # Conteúdo principal da tela
        ft.Container(
            ft.Column([
                ft.Container(height=30),
                ft.Text("Resumo da Análise", color="#004054", size=32, font_family="Gotham", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Container(height=24),
                ft.Container(
                    ft.Column([
                        LinhaResumo("Intervalo de datas:", resumo["intervalo_datas"], width=300),
                        ft.Container(height=10),
                        LinhaResumo("Valor demonstrativo:", resumo["valor_demonstrativo"], width=300),
                        ft.Container(height=10),
                        LinhaResumo("Valor Furnapen:", resumo["valor_funarpen"], width=300),
                        ft.Container(height=10),
                        LinhaResumo("Valor ISSQN:", resumo["valor_issqn"], width=300),
                        ft.Container(height=10),
                        ft.Row([
                            ft.Text("Valor líquido total:", color="#004054", size=22, font_family="Gotham", weight=ft.FontWeight.BOLD),
                            ft.Container(
                                ft.Row([
                                    ft.Text(resumo["valor_liquido"], color="#004054", size=20, font_family="Gotham", weight=ft.FontWeight.BOLD),
                                    ft.IconButton(
                                        icon="content_copy", 
                                        icon_color="#004054", 
                                        icon_size=22, 
                                        tooltip="Copiar", 
                                        on_click=lambda e, v=resumo["valor_liquido"]: copiar_para_clipboard(v, e)
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=0),
                                bgcolor="#E8E8E8",
                                border_radius=12,
                                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                                width=300,
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ], spacing=0),
                    bgcolor="#F6F6F6",
                    border_radius=24,
                    padding=32,
                    shadow=ft.BoxShadow(blur_radius=12, color="#00000033", offset=ft.Offset(0, 4)),
                    width=600,
                ),
                ft.Container(height=24),
                ft.Row([
                    BotaoSecundario("VOLTAR AO INÍCIO", on_click=voltar_nova_analise, width=280, height=54),
                    BotaoPrincipal("BAIXAR ARQUIVOS", on_click=ir_para_exportacao, width=280, height=54),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=40),
            ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            margin=ft.margin.only(top=80, left=80, right=80, bottom=20),
            height=820,  # Altura fixa para garantir que caiba em 900px
        ),
        # Logo
        ft.Container(
            ft.Image(src="images/Logotipo-LumaLector.png", width=260, height=60),
            alignment=ft.alignment.top_center,
            margin=ft.margin.only(top=32)
        ),
        # Botões de navegação com z-index mais alto
        ft.Container(
            ft.Row([
                BotaoIconeCircular("arrow_back", on_click=voltar_pagina_anterior, bgcolor="#008EBC", icon_color="#FFFFFF", size=56),
                ft.Container(expand=True),  # Espaçador
                BotaoIconeCircular("home", on_click=ir_para_home, bgcolor="#008EBC", icon_color="#FFFFFF", size=56),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            alignment=ft.alignment.top_center,
            margin=ft.margin.only(top=24, left=24, right=24),
            height=56,
        ),
    ])

def tela_exportacao():
    return ft.Stack([
        # Conteúdo principal da tela
        ft.Container(
            ft.Column([
                ft.Container(height=60),
                ft.Text("Exportar Dados da Análise", color="#004054", size=28, font_family="Gotham", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Container(height=32),
                ft.Column([
                    # Botão TXT
                    BotaoPrincipal("BAIXAR .TXT", on_click=baixar_txt, width=400, height=64),
                    ft.Container(height=6),
                    ft.Text("Arquivo de texto legível com relatório formatado", color="#666666", size=14, font_family="Gotham", text_align=ft.TextAlign.CENTER, style=ft.TextStyle(italic=True)),
                    ft.Container(height=20),
                    
                    # Botão CSV
                    BotaoPrincipal("BAIXAR .CSV", on_click=baixar_csv, width=400, height=64),
                    ft.Container(height=6),
                    ft.Text("Dados estruturados para importar em outras planilhas", color="#666666", size=14, font_family="Gotham", text_align=ft.TextAlign.CENTER, style=ft.TextStyle(italic=True)),
                    ft.Container(height=20),
                    
                    # Botão Voltar
                    BotaoSecundario("VOLTAR AO INÍCIO", on_click=voltar_nova_analise, width=400, height=64),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            margin=ft.margin.only(top=80, left=80, right=80, bottom=20)
        ),
        # Logo
        ft.Container(
            ft.Image(src="images/Logotipo-LumaLector.png", width=260, height=60),
            alignment=ft.alignment.top_center,
            margin=ft.margin.only(top=32)
        ),
        # Botões de navegação com z-index mais alto
        ft.Container(
            ft.Row([
                BotaoIconeCircular("arrow_back", on_click=voltar_pagina_anterior, bgcolor="#008EBC", icon_color="#FFFFFF", size=56),
                ft.Container(expand=True),  # Espaçador
                BotaoIconeCircular("home", on_click=ir_para_home, bgcolor="#008EBC", icon_color="#FFFFFF", size=56),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            alignment=ft.alignment.top_center,
            margin=ft.margin.only(top=24, left=24, right=24),
            height=56,
        ),
    ])

def tela_historico():
    # Estado da ordenação (será mantido durante a sessão)
    if not hasattr(tela_historico, 'ordem_atual'):
        tela_historico.ordem_atual = "mais_recente"
        tela_historico.historico_container = None
        tela_historico.ordenacao_container = None
    
    def atualizar_historico():
        """Atualiza a lista do histórico com a ordenação atual"""
        historico_dados = carregar_historico_ordenado(tela_historico.ordem_atual)
        
        # Limpar e recriar a lista
        if tela_historico.historico_container:
            tela_historico.historico_container.content.controls.clear()
            
            if historico_dados:
                for entrada in historico_dados:
                    linha_historico = criar_linha_historico(entrada)
                    tela_historico.historico_container.content.controls.append(linha_historico)
            else:
                # Mensagem quando não há dados
                tela_historico.historico_container.content.controls.append(
                    ft.Container(
                        ft.Text("Nenhuma análise realizada ainda.", 
                               color="#B0B0B0", 
                               size=16, 
                               font_family="Gotham", 
                               text_align=ft.TextAlign.CENTER),
                        alignment=ft.alignment.center,
                        padding=ft.padding.all(20)
                    )
                )
            
            # Atualizar interface
            from app.logic import flet_page
            if flet_page and hasattr(flet_page, 'update') and callable(flet_page.update):
                flet_page.update()
    
    def mudar_ordenacao(nova_ordem):
        """Muda a ordenação e atualiza a lista"""
        tela_historico.ordem_atual = nova_ordem
        
        # Atualizar estilos dos botões de ordenação
        if tela_historico.ordenacao_container:
            for control in tela_historico.ordenacao_container.controls:
                if hasattr(control, 'content') and hasattr(control.content, 'value'):
                    if control.content.value == "Mais recente":
                        control.bgcolor = "#008EBC" if nova_ordem == "mais_recente" else "#FFFFFF"
                        control.content.color = "#FFFFFF" if nova_ordem == "mais_recente" else "#008EBC"
                    elif control.content.value == "Mais antigo":
                        control.bgcolor = "#008EBC" if nova_ordem == "mais_antigo" else "#FFFFFF"
                        control.content.color = "#FFFFFF" if nova_ordem == "mais_antigo" else "#008EBC"
        
        atualizar_historico()
    
    def criar_linha_historico(entrada):
        """Cria uma linha individual do histórico"""
        def visualizar_analise(e):
            from app.logic import estado, set_etapa
            estado["resumo"] = entrada["resumo"]
            set_etapa(6)
        
        def confirmar_remocao(e):
            """Remove a entrada do histórico"""
            # Remover entrada do histórico
            sucesso = remover_entrada_historico(entrada)
            
            if sucesso:
                # Resetar estados da tela do histórico para recriação completa
                if hasattr(tela_historico, 'ordem_atual'):
                    delattr(tela_historico, 'ordem_atual')
                if hasattr(tela_historico, 'historico_container'):
                    delattr(tela_historico, 'historico_container')
                if hasattr(tela_historico, 'ordenacao_container'):
                    delattr(tela_historico, 'ordenacao_container')
                
                # Recarregar completamente a tela do histórico
                from app.logic import set_etapa
                set_etapa(2)
        
        return ft.Container(
            ft.Row([
                # Data e nome do arquivo
                ft.Container(
                    ft.Text(f"{entrada['data']} | \"{entrada['nome_arquivo']}\"", 
                           color="#004054", 
                           size=16, 
                           font_family="Gotham"),
                    expand=True,
                ),
                # Botões de ação
                ft.Row([
                    ft.IconButton(
                        icon="visibility", 
                        icon_color="#008EBC", 
                        icon_size=20, 
                        tooltip="Visualizar análise",
                        on_click=visualizar_analise
                    ),
                    ft.IconButton(
                        icon="delete", 
                        icon_color="#d32f2f", 
                        icon_size=20, 
                        tooltip="Remover do histórico",
                        on_click=confirmar_remocao
                    ),
                ], spacing=0),
            ], 
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
            vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            border_radius=8,
            bgcolor="#F8F8F8",
            margin=ft.margin.only(bottom=4),
        )
    
    # Criar container de ordenação
    tela_historico.ordenacao_container = ft.Row([
        ft.Text("Ordenar por:", color="#004054", size=14, font_family="Gotham", weight=ft.FontWeight.BOLD),
        ft.Container(width=16),  # Espaçamento
        ft.ElevatedButton(
            "Mais recente",
            bgcolor="#008EBC" if tela_historico.ordem_atual == "mais_recente" else "#FFFFFF",
            color="#FFFFFF" if tela_historico.ordem_atual == "mais_recente" else "#008EBC",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=16),
                text_style=ft.TextStyle(size=12, font_family="Gotham"),
                elevation=2,
            ),
            height=32,
            on_click=lambda e: mudar_ordenacao("mais_recente")
        ),
        ft.ElevatedButton(
            "Mais antigo", 
            bgcolor="#008EBC" if tela_historico.ordem_atual == "mais_antigo" else "#FFFFFF",
            color="#FFFFFF" if tela_historico.ordem_atual == "mais_antigo" else "#008EBC",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=16),
                text_style=ft.TextStyle(size=12, font_family="Gotham"),
                elevation=2,
            ),
            height=32,
            on_click=lambda e: mudar_ordenacao("mais_antigo")
        ),
    ], alignment=ft.MainAxisAlignment.START, spacing=8)
    
    # Criar container do histórico (rolável)
    tela_historico.historico_container = ft.Container(
        ft.ListView(
            controls=[],  # Será preenchido por atualizar_historico()
            spacing=4,
            auto_scroll=False,
            padding=ft.padding.all(16),
        ),
        bgcolor="#FFFFFF",
        border_radius=24,
        height=400,
        shadow=ft.BoxShadow(blur_radius=18, color="#00000022", offset=ft.Offset(0, 6)),
    )
    
    # Carregar dados iniciais
    atualizar_historico()
    
    return ft.Stack([
        # Conteúdo principal da tela
        ft.Container(
            ft.Column([
                ft.Container(height=60),
                ft.Text("Histórico de Análises", color="#004054", size=28, font_family="Gotham", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Container(height=20),
                
                # Controles de ordenação
                ft.Container(
                    tela_historico.ordenacao_container,
                    alignment=ft.alignment.center_left,
                    margin=ft.margin.only(left=24, bottom=16)
                ),
                
                # Lista do histórico
                tela_historico.historico_container,
                
            ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            margin=ft.margin.only(top=80, left=80, right=80, bottom=20)
        ),
        # Logo
        ft.Container(
            ft.Image(src="images/Logotipo-LumaLector.png", width=260, height=60),
            alignment=ft.alignment.top_center,
            margin=ft.margin.only(top=32)
        ),
        # Botões de navegação com z-index mais alto
        ft.Container(
            ft.Row([
                BotaoIconeCircular("arrow_back", on_click=voltar_pagina_anterior, bgcolor="#008EBC", icon_color="#FFFFFF", size=56),
                ft.Container(expand=True),  # Espaçador
                BotaoIconeCircular("home", on_click=ir_para_home, bgcolor="#008EBC", icon_color="#FFFFFF", size=56),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            alignment=ft.alignment.top_center,
            margin=ft.margin.only(top=24, left=24, right=24),
            height=56,
        ),
    ]) 