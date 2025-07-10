# app/components.py
import flet as ft

# Componentes visuais reutilizáveis

def BotaoIdentidadeVisual(texto, on_click=None, bgcolor="#008EBC", color="#FFFFFF", hover_bg="#00BEE9", width=220, height=54):
    return ft.ElevatedButton(
        texto,
        on_click=on_click,
        bgcolor=bgcolor,
        color=color,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=20),
            text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=16, font_family="Gotham"),
            overlay_color=hover_bg,
            elevation=8,
        ),
        height=height,
        width=width,
    )

def BotaoIconeCircular(icon_name, on_click=None, bgcolor="#FFFFFF", icon_color="#008EBC", size=48):
    return ft.ElevatedButton(
        content=ft.Icon(icon_name, color=icon_color, size=28),
        on_click=on_click,
        bgcolor=bgcolor,
        style=ft.ButtonStyle(
            shape=ft.CircleBorder(),
            padding=ft.padding.all(0),
            elevation=4,
        ),
        width=size,
        height=size,
        tooltip=icon_name,
    )

def BotaoCardMenu(texto_linha1, texto_linha2, icon_path, on_click=None):
    return ft.ElevatedButton(
        content=ft.Column([
            ft.Image(src=icon_path, width=64, height=64),
            ft.Text(
                texto_linha1,
                color="#004054",
                size=18,
                font_family="Gotham",
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Text(
                texto_linha2,
                color="#004054",
                size=18,
                font_family="Gotham",
                text_align=ft.TextAlign.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4),
        on_click=on_click,
        bgcolor="#F6F6F6",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=24),
            overlay_color="#e0e0e0",
            elevation=10,
            padding=0,
        ),
        width=180,
        height=180,
    )

def BotaoPrincipal(texto, on_click=None, width=320, height=64):
    return ft.ElevatedButton(
        texto,
        on_click=on_click,
        bgcolor="#008EBC",
        color="#FFFFFF",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=32),
            text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=18, font_family="Gotham"),
            overlay_color="#00BEE9",
            elevation=8,
        ),
        height=height,
        width=width,
    )

def BotaoSecundario(texto, on_click=None, width=320, height=64):
    return ft.ElevatedButton(
        texto,
        on_click=on_click,
        bgcolor="#FFFFFF",
        color="#008EBC",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=32),
            text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=18, font_family="Gotham"),
            side=ft.BorderSide(2, "#008EBC"),
            overlay_color="#00BEE9",
            elevation=8,
        ),
        height=height,
        width=width,
    )

def CardMiniatura(texto):
    return ft.Container(
        ft.Column([
            ft.Text(texto, color="#004054", size=20, font_family="Gotham", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        width=220,
        height=180,
        bgcolor="#FFFFFF",
        border_radius=24,
        shadow=ft.BoxShadow(blur_radius=18, color="#00000022", offset=ft.Offset(0, 6)),
        alignment=ft.alignment.center,
    )

def BalaoValor(valor):
    return ft.Container(
        ft.Row([
            ft.Text(valor, color="#004054", size=16, font_family="Gotham"),
            ft.IconButton(icon="content_copy", icon_color="#008EBC", icon_size=20, tooltip="Copiar", on_click=None),
        ], alignment=ft.MainAxisAlignment.START, spacing=8),
        bgcolor="#F3F3F3",
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
        shadow=ft.BoxShadow(blur_radius=6, color="#00000011", offset=ft.Offset(0, 2)),
    )

def LinhaHistorico(data, nome, on_click=None):
    return ft.Row([
        ft.Text(f"{data} | \"{nome}\"", color="#004054", size=16, font_family="Gotham"),
        ft.IconButton(icon="visibility", icon_color="#008EBC", icon_size=24, on_click=on_click),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER) 