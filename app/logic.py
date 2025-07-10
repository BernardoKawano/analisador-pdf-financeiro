# app/logic.py
import os
import json
from pathlib import Path
from datetime import datetime
from app.analise_pdf import AnalisadorPDF
import fitz
import flet as ft

# Variáveis globais
estado = {"etapa": None, "file_path": None, "resumo": None}
historico_navegacao = []
flet_page = None
pick_file = None  # Será definida no main_flet.py
save_txt_dialog_func = None  # Será definida no main_flet.py
save_csv_dialog_func = None  # Será definida no main_flet.py  


# Funções de lógica/utilitários
# (Os imports das telas são feitos dentro das funções para evitar dependência circular)



def carregar_historico():
    try:
        if os.path.exists("historico.json"):
            with open("historico.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Erro ao carregar histórico: {e}")
        return []

def carregar_historico_ordenado(ordem="mais_recente"):
    """
    Carrega histórico ordenado por data.
    ordem: 'mais_recente' ou 'mais_antigo'
    """
    historico = carregar_historico()
    if not historico:
        return []
    
    try:
        # Ordenar por timestamp se disponível, senão por data
        if ordem == "mais_recente":
            if 'timestamp' in historico[0]:
                return sorted(historico, key=lambda x: x.get('timestamp', ''), reverse=True)
            else:
                return sorted(historico, key=lambda x: x.get('data', ''), reverse=True)
        else:  # mais_antigo
            if 'timestamp' in historico[0]:
                return sorted(historico, key=lambda x: x.get('timestamp', ''))
            else:
                return sorted(historico, key=lambda x: x.get('data', ''))
    except Exception as e:
        print(f"Erro ao ordenar histórico: {e}")
        return historico

def remover_entrada_historico(entrada_para_remover):
    """
    Remove uma entrada específica do histórico usando múltiplos critérios de identificação
    """
    try:
        historico = carregar_historico()
        
        # Filtrar histórico removendo a entrada específica
        historico_filtrado = []
        entrada_removida = False
        
        for i, entrada in enumerate(historico):
            deve_manter = True
            
            # Critério 1: Timestamp (mais preciso)
            if ('timestamp' in entrada and 'timestamp' in entrada_para_remover and 
                entrada['timestamp'] == entrada_para_remover['timestamp']):
                deve_manter = False
                entrada_removida = True
            
            # Critério 2: Combinação exata de campos críticos
            elif (entrada.get('data') == entrada_para_remover.get('data') and
                  entrada.get('hora') == entrada_para_remover.get('hora') and
                  entrada.get('nome_arquivo') == entrada_para_remover.get('nome_arquivo')):
                
                # Verificação adicional: comparar resumo se disponível
                if ('resumo' in entrada and 'resumo' in entrada_para_remover):
                    resumo_entrada = entrada['resumo']
                    resumo_remover = entrada_para_remover['resumo']
                    
                    # Comparar alguns valores chave do resumo para garantir que é a mesma entrada
                    if (resumo_entrada.get('valor_liquido') == resumo_remover.get('valor_liquido') and
                        resumo_entrada.get('qtd_pgs') == resumo_remover.get('qtd_pgs')):
                        deve_manter = False
                        entrada_removida = True
                else:
                    # Se não tem resumo, remover mesmo assim pela combinação data+hora+nome
                    deve_manter = False
                    entrada_removida = True
            
            if deve_manter:
                historico_filtrado.append(entrada)
        
        if entrada_removida:
            # Salvar histórico atualizado
            salvar_historico(historico_filtrado)
            
            # Mostrar confirmação
            if flet_page and hasattr(flet_page, 'add') and callable(flet_page.add):
                flet_page.add(ft.SnackBar(ft.Text("✓ Entrada removida do histórico"), bgcolor="#4caf50"))
                if hasattr(flet_page, 'update') and callable(flet_page.update):
                    flet_page.update()
            
            return True
        else:
            if flet_page and hasattr(flet_page, 'add') and callable(flet_page.add):
                flet_page.add(ft.SnackBar(ft.Text("⚠️ Entrada não encontrada no histórico"), bgcolor="#ff9800"))
                if hasattr(flet_page, 'update') and callable(flet_page.update):
                    flet_page.update()
            return False
                
    except Exception as e:
        if flet_page and hasattr(flet_page, 'add') and callable(flet_page.add):
            flet_page.add(ft.SnackBar(ft.Text(f"❌ Erro ao remover entrada: {str(e)}"), bgcolor="#d32f2f"))
            if hasattr(flet_page, 'update') and callable(flet_page.update):
                flet_page.update()
        return False

def salvar_historico(historico):
    try:
        with open("historico.json", "w", encoding="utf-8") as f:
            json.dump(historico, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar histórico: {e}")



def adicionar_ao_historico(nome_arquivo, resumo_dados):
    historico = carregar_historico()
    nova_entrada = {
        "data": datetime.now().strftime("%d/%m/%Y"),
        "hora": datetime.now().strftime("%H:%M"),
        "nome_arquivo": nome_arquivo,
        "resumo": resumo_dados,
        "timestamp": datetime.now().isoformat()
    }
    historico.insert(0, nova_entrada)
    if len(historico) > 50:
        historico = historico[:50]
    salvar_historico(historico)
    return historico

def validar_arquivo_pdf(file_path):
    try:
        if not os.path.exists(file_path):
            return False, "Arquivo não encontrado."
        tamanho = os.path.getsize(file_path)
        if tamanho == 0:
            return False, "Arquivo está vazio."
        if tamanho > 100 * 1024 * 1024:
            return False, "Arquivo muito grande (máximo 100MB)."
        if not file_path.lower().endswith('.pdf'):
            return False, "Arquivo deve ter extensão .pdf"
        with open(file_path, 'rb') as f:
            header = f.read(8)
            if not header.startswith(b'%PDF-'):
                return False, "Arquivo não é um PDF válido (cabeçalho inválido)."
        if fitz:
            try:
                doc = fitz.open(file_path)
                if doc.page_count == 0:
                    doc.close()
                    return False, "PDF não contém páginas."
                doc.close()
            except Exception as e:
                return False, f"PDF corrompido ou inválido: {str(e)}"
        return True, "PDF válido."
    except Exception as e:
        return False, f"Erro ao validar arquivo: {str(e)}"

def set_etapa(etapa):
    global estado, historico_navegacao, flet_page
    if estado["etapa"] != etapa:
        if estado["etapa"] is not None:  # Só adiciona ao histórico se não for a primeira inicialização
            historico_navegacao.append(estado["etapa"])
            if len(historico_navegacao) > 10:
                historico_navegacao.pop(0)
    estado["etapa"] = etapa
    if flet_page is not None and hasattr(flet_page, 'controls') and flet_page.controls is not None:
        flet_page.controls.clear()
    from app.screens import tela_boas_vindas, tela_historico, tela_upload, tela_confirmacao, tela_analisando, tela_resumo, tela_exportacao
    if flet_page is not None and hasattr(flet_page, 'add'):
        if etapa == 1:
            flet_page.add(tela_boas_vindas())
        elif etapa == 2:
            flet_page.add(tela_historico())
        elif etapa == 3:
            flet_page.add(tela_upload())
        elif etapa == 4:
            flet_page.add(tela_confirmacao())
        elif etapa == 5:
            flet_page.add(tela_analisando())
        elif etapa == 6:
            flet_page.add(tela_resumo())
        elif etapa == 7:
            flet_page.add(tela_exportacao())
        if hasattr(flet_page, 'update'):
            flet_page.update()

def ir_para_home(e=None):
    global historico_navegacao
    historico_navegacao.clear()
    set_etapa(1)

def voltar_pagina_anterior(e=None):
    global historico_navegacao, estado
    
    # Definir navegação padrão baseada na etapa atual
    etapa_atual = estado.get("etapa")
    
    if historico_navegacao:
        # Se há histórico, usar o último item
        etapa_anterior = historico_navegacao.pop()
    else:
        # Se não há histórico, definir navegação baseada na etapa atual
        if etapa_atual == 2:  # Histórico -> Home
            etapa_anterior = 1
        elif etapa_atual == 3:  # Upload -> Home
            etapa_anterior = 1
        elif etapa_atual == 4:  # Confirmação -> Upload
            etapa_anterior = 3
        elif etapa_atual == 5:  # Analisando -> Confirmação
            etapa_anterior = 4
        elif etapa_atual == 6:  # Resumo -> Analisando
            etapa_anterior = 5
        elif etapa_atual == 7:  # Exportação -> Resumo
            etapa_anterior = 6
        else:
            # Para qualquer outro caso, ir para home
            etapa_anterior = 1
    
    # Navegar para a etapa anterior
    estado["etapa"] = etapa_anterior  # type: ignore
    if flet_page is not None and hasattr(flet_page, 'controls') and flet_page.controls is not None:
        flet_page.controls.clear()
    from app.screens import tela_boas_vindas, tela_historico, tela_upload, tela_confirmacao, tela_analisando, tela_resumo, tela_exportacao
    if flet_page is not None and hasattr(flet_page, 'add') and callable(flet_page.add):
        if etapa_anterior == 1:
            flet_page.add(tela_boas_vindas())
        elif etapa_anterior == 2:
            flet_page.add(tela_historico())
        elif etapa_anterior == 3:
            flet_page.add(tela_upload())
        elif etapa_anterior == 4:
            flet_page.add(tela_confirmacao())
        elif etapa_anterior == 5:
            flet_page.add(tela_analisando())
        elif etapa_anterior == 6:
            flet_page.add(tela_resumo())
        elif etapa_anterior == 7:
            flet_page.add(tela_exportacao())
        if hasattr(flet_page, 'update') and callable(flet_page.update):
            flet_page.update()

def voltar_nova_analise(e=None):
    global estado, historico_navegacao
    estado["file_path"] = None
    estado["resumo"] = None
    historico_navegacao.clear()
    ir_para_home()

def ir_para_exportacao(e=None):
    set_etapa(7)

def baixar_txt(e=None):
    """
    Abre janela para salvar arquivo TXT com o resumo da análise.
    """
    global save_txt_dialog_func
    resumo = estado["resumo"]
    if not resumo:
        if flet_page and hasattr(flet_page, 'add') and callable(flet_page.add):
            flet_page.add(ft.SnackBar(ft.Text("Nenhum dado para exportar"), bgcolor="#d32f2f"))
            if hasattr(flet_page, 'update') and callable(flet_page.update):
                flet_page.update()
        return
    
    if save_txt_dialog_func and callable(save_txt_dialog_func):
        save_txt_dialog_func()
    else:
        if flet_page and hasattr(flet_page, 'add') and callable(flet_page.add):
            flet_page.add(ft.SnackBar(ft.Text("Função de salvar não está disponível"), bgcolor="#d32f2f"))
            if hasattr(flet_page, 'update') and callable(flet_page.update):
                flet_page.update()

def salvar_txt_em_local(caminho_arquivo):
    """
    Gera e salva um arquivo de texto (.txt) com o resumo da análise no local especificado.
    """
    try:
        resumo = estado["resumo"]
        if not resumo:
            return

        # Gerar conteúdo estruturado do relatório
        from datetime import datetime
        data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
        nome_arquivo_original = Path(estado["file_path"]).name if estado["file_path"] else "arquivo_desconhecido.pdf"
        
        conteudo = f"""RELATÓRIO DE ANÁLISE DE PDF
{'='*50}

Arquivo analisado: {nome_arquivo_original}
Data da análise: {data_atual}
Sistema: LumaLector v1.0

{'='*50}
RESUMO DOS DADOS EXTRAÍDOS
{'='*50}

Quantidade de páginas: {resumo['qtd_pgs']}
Intervalo de datas: {resumo['intervalo_datas']}

VALORES IDENTIFICADOS:
• Valor demonstrativo: {resumo['valor_demonstrativo']}
• Valor Furnapen: {resumo['valor_funarpen']}
• Valor ISSQN: {resumo['valor_issqn']}
• Valor líquido total: {resumo['valor_liquido']}

{'='*50}
Relatório gerado automaticamente pelo Luma|Lector
Para dúvidas, consulte a documentação do sistema.
{'='*50}
"""

        # Salvar no local especificado pelo usuário
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write(conteudo)
            
        if flet_page and hasattr(flet_page, 'add') and callable(flet_page.add):
            flet_page.add(ft.SnackBar(ft.Text(f"✓ Arquivo TXT salvo: {Path(caminho_arquivo).name}"), bgcolor="#4caf50"))
            if hasattr(flet_page, 'update') and callable(flet_page.update):
                flet_page.update()
                
    except Exception as e:
        if flet_page and hasattr(flet_page, 'add') and callable(flet_page.add):
            flet_page.add(ft.SnackBar(ft.Text(f"Erro ao salvar TXT: {str(e)}"), bgcolor="#d32f2f"))
            if hasattr(flet_page, 'update') and callable(flet_page.update):
                flet_page.update()

def baixar_csv(e=None):
    """
    Abre janela para salvar arquivo CSV com os dados da análise.
    """
    global save_csv_dialog_func
    resumo = estado["resumo"]
    if not resumo:
        if flet_page and hasattr(flet_page, 'add') and callable(flet_page.add):
            flet_page.add(ft.SnackBar(ft.Text("Nenhum dado para exportar"), bgcolor="#d32f2f"))
            if hasattr(flet_page, 'update') and callable(flet_page.update):
                flet_page.update()
        return
    
    if save_csv_dialog_func and callable(save_csv_dialog_func):
        save_csv_dialog_func()
    else:
        if flet_page and hasattr(flet_page, 'add') and callable(flet_page.add):
            flet_page.add(ft.SnackBar(ft.Text("Função de salvar não está disponível"), bgcolor="#d32f2f"))
            if hasattr(flet_page, 'update') and callable(flet_page.update):
                flet_page.update()

def salvar_csv_em_local(caminho_arquivo):
    """
    Gera e salva um arquivo CSV com os dados da análise no local especificado.
    """
    try:
        resumo = estado["resumo"]
        if not resumo:
            return

        # Gerar CSV estruturado com formatação especificada
        from datetime import datetime
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Função para limpar valores monetários para float
        def limpar_valor_monetario(valor):
            if isinstance(valor, str) and valor.startswith("R$"):
                return float(valor.replace("R$", "").replace(".", "").replace(",", ".").strip())
            return 0.0
        
        # Converter quantidade de páginas para int
        def converter_qtde_paginas(valor):
            if isinstance(valor, str) and valor.isdigit():
                return int(valor)
            return 0
        
        # Criar estrutura CSV conforme especificado
        import csv
        with open(caminho_arquivo, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            
            # Cabeçalhos conforme especificado
            writer.writerow([
                "Data da Análise",
                "Intervalo de Datas", 
                "Qtde Páginas",
                "Valor Demonstrativo",
                "Valor Furnapen",
                "Valor ISSQN", 
                "Valor Líquido Total"
            ])
            
            # Dados formatados
            writer.writerow([
                data_atual,
                resumo['intervalo_datas'],
                converter_qtde_paginas(resumo['qtd_pgs']),
                limpar_valor_monetario(resumo['valor_demonstrativo']),
                limpar_valor_monetario(resumo['valor_funarpen']),
                limpar_valor_monetario(resumo['valor_issqn']),
                limpar_valor_monetario(resumo['valor_liquido'])
            ])
            
        if flet_page and hasattr(flet_page, 'add') and callable(flet_page.add):
            flet_page.add(ft.SnackBar(ft.Text(f"✓ Arquivo CSV salvo: {Path(caminho_arquivo).name}"), bgcolor="#4caf50"))
            if hasattr(flet_page, 'update') and callable(flet_page.update):
                flet_page.update()
                
    except Exception as e:
        if flet_page and hasattr(flet_page, 'add') and callable(flet_page.add):
            flet_page.add(ft.SnackBar(ft.Text(f"Erro ao salvar CSV: {str(e)}"), bgcolor="#d32f2f"))
            if hasattr(flet_page, 'update') and callable(flet_page.update):
                flet_page.update()



def abrir_historico(e=None):
    set_etapa(2)

def abrir_upload(e=None):
    set_etapa(3)

def gerar_miniatura_pdf(pdf_path):
    if not fitz:
        return None
    try:
        doc = fitz.open(pdf_path)
        if doc.page_count == 0:
            doc.close()
            return None
        page = doc[0]
        matriz = fitz.Matrix(0.4, 0.4)
        pixmap = page.get_pixmap(matrix=matriz)  # type: ignore
        img_data = pixmap.tobytes("png")
        doc.close()
        import tempfile
        temp_dir = tempfile.gettempdir()
        nome_arquivo = Path(pdf_path).stem
        temp_path = os.path.join(temp_dir, f"miniatura_{nome_arquivo}.png")
        with open(temp_path, "wb") as f:
            f.write(img_data)
        return temp_path
    except Exception as e:
        return None 