import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from collections import defaultdict
from datetime import datetime

try:
    import PyPDF2  # type: ignore
except ImportError:
    print("Erro: PyPDF2 não está instalado. Execute: pip install PyPDF2")
    sys.exit(1)

@dataclass
class ValorDemonstrativo:
    pagina: int
    linha_completa: str
    valor: Decimal
    data_pagamento: str

@dataclass
class ValorFunarpen:
    pagina: int
    linha_completa: str
    valor: Decimal
    data_pagamento: str

@dataclass
class ValorIssqn:
    pagina: int
    linha_completa: str
    valor: Optional[Decimal]
    data_pagamento: str

@dataclass
class TotalDiario:
    data: str
    demonstrativos: Decimal
    funarpen: Decimal
    issqn: Decimal
    valor_liquido: Decimal

class AnalisadorPDF:
    def __init__(self, caminho_pdf: str):
        self.caminho_pdf = caminho_pdf
        self.valores_demonstrativos: List[ValorDemonstrativo] = []
        self.valores_funarpen: List[ValorFunarpen] = []
        self.valores_issqn: List[ValorIssqn] = []
        self.campo_bancario_esperado = "Ag./Cod. Cedente: 3162/730791-8"
        
    def extrair_data_pagamento(self, texto: str) -> str:
        """Extrai data de pagamento no formato DD/MM/YYYY"""
        padrao = r'Dt\.\s*Pgto:\s*(\d{2}/\d{2}/\d{4})'
        match = re.search(padrao, texto)
        if match:
            return match.group(1)
        return ""
    
    def extrair_valor_monetario(self, texto: str) -> Optional[Decimal]:
        """Extrai valor monetário no formato brasileiro (R$ 1.234,56)"""
        padrao = r'R\$\s*([0-9.,]+)'
        match = re.search(padrao, texto)
        if match:
            valor_str = match.group(1).replace('.', '').replace(',', '.')
            try:
                return Decimal(valor_str)
            except InvalidOperation:
                return None
        return None
    
    def pagina_contem_campo_bancario(self, texto: str) -> bool:
        """Verifica se a página contém o campo bancário específico"""
        return self.campo_bancario_esperado in texto
    
    def processar_valor_demonstrativo(self, linhas: List[str], num_pagina: int):
        """Processa valores demonstrativos na página"""
        for i, linha in enumerate(linhas):
            if "Valor Demonstrativo:" in linha:
                valor = self.extrair_valor_monetario(linha)
                data_pagamento = self.extrair_data_pagamento(linha)
                if valor:
                    self.valores_demonstrativos.append(
                        ValorDemonstrativo(num_pagina, linha.strip(), valor, data_pagamento)
                    )
    
    def processar_funarpen(self, linhas: List[str], num_pagina: int):
        """Processa valores FUNARPEN na página"""
        # Primeiro, encontra a data de pagamento na página
        data_pagamento = ""
        for linha in linhas:
            data_temp = self.extrair_data_pagamento(linha)
            if data_temp:
                data_pagamento = data_temp
                break
        
        for i, linha in enumerate(linhas):
            if "FUNARPEN" in linha:
                # Verifica a linha atual
                valor = self.extrair_valor_monetario(linha)
                if valor:
                    self.valores_funarpen.append(
                        ValorFunarpen(num_pagina, linha.strip(), valor, data_pagamento)
                    )
                else:
                    # Verifica linha anterior
                    if i > 0:
                        valor_anterior = self.extrair_valor_monetario(linhas[i-1])
                        if valor_anterior:
                            self.valores_funarpen.append(
                                ValorFunarpen(num_pagina, f"{linhas[i-1].strip()} | {linha.strip()}", valor_anterior, data_pagamento)
                            )
                    
                    # Verifica linha posterior
                    if i < len(linhas) - 1:
                        valor_posterior = self.extrair_valor_monetario(linhas[i+1])
                        if valor_posterior:
                            self.valores_funarpen.append(
                                ValorFunarpen(num_pagina, f"{linha.strip()} | {linhas[i+1].strip()}", valor_posterior, data_pagamento)
                            )
    
    def processar_issqn(self, linhas: List[str], num_pagina: int):
        """Processa valores ISSQN na página"""
        # Primeiro, encontra a data de pagamento na página
        data_pagamento = ""
        for linha in linhas:
            data_temp = self.extrair_data_pagamento(linha)
            if data_temp:
                data_pagamento = data_temp
                break
        
        for linha in linhas:
            if "ISSQN - Imposto sobre Serviços de Qualquer Natureza" in linha:
                valor = self.extrair_valor_monetario(linha)
                self.valores_issqn.append(
                    ValorIssqn(num_pagina, linha.strip(), valor, data_pagamento)
                )
    
    def processar_pagina(self, texto: str, num_pagina: int):
        """Processa uma página completa"""
        print(f"Processando página {num_pagina}...")
        
        # Verifica se contém o campo bancário específico
        if not self.pagina_contem_campo_bancario(texto):
            print(f"  Página {num_pagina}: Campo bancário não encontrado - ignorando")
            return False
        
        print(f"  Página {num_pagina}: Campo bancário encontrado - processando")
        
        # Divide em linhas para processamento
        linhas = texto.split('\n')
        
        # Processa cada tipo de valor
        self.processar_valor_demonstrativo(linhas, num_pagina)
        self.processar_funarpen(linhas, num_pagina)
        self.processar_issqn(linhas, num_pagina)
        
        return True
    
    def analisar_pdf(self) -> bool:
        """Analisa o PDF completo, página por página"""
        try:
            with open(self.caminho_pdf, 'rb') as arquivo:
                leitor = PyPDF2.PdfReader(arquivo)
                total_paginas = len(leitor.pages)
                
                print(f"PDF carregado: {total_paginas} páginas encontradas")
                print("=" * 60)
                
                paginas_processadas = 0
                
                for num_pagina in range(total_paginas):
                    pagina = leitor.pages[num_pagina]
                    texto = pagina.extract_text()
                    
                    if self.processar_pagina(texto, num_pagina + 1):
                        paginas_processadas += 1
                
                print("=" * 60)
                print(f"Análise concluída: {paginas_processadas} páginas processadas")
                return True
                
        except FileNotFoundError:
            print(f"Erro: Arquivo '{self.caminho_pdf}' não encontrado.")
            return False
        except Exception as e:
            print(f"Erro ao processar PDF: {e}")
            return False
    
    def calcular_totais_diarios(self) -> List[TotalDiario]:
        """Calcula totais diários agrupados por data de pagamento"""
        totais_por_data = defaultdict(lambda: {
            'demonstrativos': Decimal('0'),
            'funarpen': Decimal('0'),
            'issqn': Decimal('0')
        })
        
        # Agrupa valores demonstrativos por data
        for valor in self.valores_demonstrativos:
            data = valor.data_pagamento if valor.data_pagamento else "Data não identificada"
            totais_por_data[data]['demonstrativos'] += valor.valor
        
        # Agrupa valores FUNARPEN por data
        for valor in self.valores_funarpen:
            data = valor.data_pagamento if valor.data_pagamento else "Data não identificada"
            totais_por_data[data]['funarpen'] += valor.valor
        
        # Agrupa valores ISSQN por data
        for valor in self.valores_issqn:
            if valor.valor:
                data = valor.data_pagamento if valor.data_pagamento else "Data não identificada"
                totais_por_data[data]['issqn'] += valor.valor
        
        # Converte para lista de TotalDiario
        totais_diarios = []
        for data, totais in sorted(totais_por_data.items()):
            valor_liquido = totais['demonstrativos'] - totais['funarpen'] - totais['issqn']
            totais_diarios.append(TotalDiario(
                data=data,
                demonstrativos=totais['demonstrativos'],
                funarpen=totais['funarpen'],
                issqn=totais['issqn'],
                valor_liquido=valor_liquido
            ))
        
        return totais_diarios

    def calcular_totais(self) -> Dict[str, Union[Decimal, int]]:
        """Calcula totais consolidados"""
        total_demonstrativos = sum(v.valor for v in self.valores_demonstrativos)
        total_funarpen = sum(v.valor for v in self.valores_funarpen)
        total_issqn = sum(v.valor for v in self.valores_issqn if v.valor is not None)
        valor_liquido = total_demonstrativos - total_funarpen - total_issqn
        
        return {
            'total_demonstrativos': total_demonstrativos,
            'total_funarpen': total_funarpen,
            'total_issqn': total_issqn,
            'valor_liquido': valor_liquido
        }
    
    def gerar_relatorio(self) -> str:
        """Gera relatório estruturado completo"""
        totais = self.calcular_totais()
        totais_diarios = self.calcular_totais_diarios()
        
        relatorio = []
        relatorio.append("=" * 80)
        relatorio.append("RELATÓRIO DE ANÁLISE DE PDF - VALORES FINANCEIROS")
        relatorio.append("=" * 80)
        relatorio.append("")
        
        # Seção 1: Valores Demonstrativos
        relatorio.append("1. VALORES DEMONSTRATIVOS CONSIDERADOS")
        relatorio.append("-" * 50)
        if self.valores_demonstrativos:
            for valor in self.valores_demonstrativos:
                relatorio.append(f"Página {valor.pagina}: {valor.linha_completa}")
                relatorio.append(f"  Valor: R$ {valor.valor:,.2f}")
                relatorio.append(f"  Data de pagamento: {valor.data_pagamento}")
                relatorio.append("")
        else:
            relatorio.append("Nenhum valor demonstrativo encontrado.")
        relatorio.append("")
        
        # Seção 2: Valores FUNARPEN
        relatorio.append("2. VALORES SUBTRAÍDOS POR FUNARPEN")
        relatorio.append("-" * 50)
        if self.valores_funarpen:
            for valor in self.valores_funarpen:
                relatorio.append(f"Página {valor.pagina}: {valor.linha_completa}")
                relatorio.append(f"  Valor: R$ {valor.valor:,.2f}")
                relatorio.append(f"  Data de pagamento: {valor.data_pagamento}")
                relatorio.append("")
        else:
            relatorio.append("Nenhum valor FUNARPEN encontrado.")
        relatorio.append("")
        
        # Seção 3: Valores ISSQN
        relatorio.append("3. VALORES SUBTRAÍDOS POR CONTER ISSQN")
        relatorio.append("-" * 50)
        if self.valores_issqn:
            for valor in self.valores_issqn:
                relatorio.append(f"Página {valor.pagina}: {valor.linha_completa}")
                if valor.valor:
                    relatorio.append(f"  Valor: R$ {valor.valor:,.2f}")
                    relatorio.append(f"  Data de pagamento: {valor.data_pagamento}")
                else:
                    relatorio.append("  Valor: Não identificado")
                relatorio.append("")
        else:
            relatorio.append("Nenhum valor ISSQN encontrado.")
        relatorio.append("")
        
        # Seção 4: Totais Diários
        relatorio.append("4. TOTAIS DIÁRIOS")
        relatorio.append("-" * 50)
        if totais_diarios:
            for total in totais_diarios:
                relatorio.append(f"Data: {total.data}")
                relatorio.append(f"  Demonstrativos: R$ {total.demonstrativos:,.2f}")
                relatorio.append(f"  Subtrações FUNARPEN: R$ {total.funarpen:,.2f}")
                relatorio.append(f"  Subtrações ISSQN: R$ {total.issqn:,.2f}")
                relatorio.append(f"  Valor líquido diário: R$ {total.valor_liquido:,.2f}")
                relatorio.append("")
        else:
            relatorio.append("Nenhum total diário calculado.")
        relatorio.append("")
        
        # Seção 5: Resumo Consolidado
        relatorio.append("5. RESUMO CONSOLIDADO")
        relatorio.append("-" * 50)
        relatorio.append(f"Total de valores demonstrativos: R$ {totais['total_demonstrativos']:,.2f}")
        relatorio.append(f"Total de subtrações FUNARPEN: R$ {totais['total_funarpen']:,.2f}")
        relatorio.append(f"Total de valores ISSQN: R$ {totais['total_issqn']:,.2f}")
        relatorio.append(f"Valor líquido final: R$ {totais['valor_liquido']:,.2f}")
        relatorio.append("")
        
        # Estatísticas
        relatorio.append("6. ESTATÍSTICAS")
        relatorio.append("-" * 50)
        relatorio.append(f"Páginas com campo bancário válido: {len(set(v.pagina for v in self.valores_demonstrativos))}")
        relatorio.append(f"Valores demonstrativos encontrados: {len(self.valores_demonstrativos)}")
        relatorio.append(f"Valores FUNARPEN encontrados: {len(self.valores_funarpen)}")
        relatorio.append(f"Valores ISSQN encontrados: {len(self.valores_issqn)}")
        relatorio.append(f"Dias com movimentação: {len(totais_diarios)}")
        relatorio.append("")
        relatorio.append("=" * 80)
        
        return "\n".join(relatorio)

def main():
    """Função principal do programa"""
    print("ANALISADOR DE PDF - VALORES FINANCEIROS")
    print("=" * 50)
    
    # Verifica argumentos da linha de comando
    if len(sys.argv) != 2:
        print("Uso: python sergio.py <caminho_do_pdf>")
        print("Exemplo: python sergio.py documento.pdf")
        sys.exit(1)
    
    caminho_pdf = sys.argv[1]
    
    # Verifica se o arquivo existe
    if not Path(caminho_pdf).exists():
        print(f"Erro: Arquivo '{caminho_pdf}' não encontrado.")
        sys.exit(1)
    
    # Cria analisador e executa análise
    analisador = AnalisadorPDF(caminho_pdf)
    
    print(f"Analisando arquivo: {caminho_pdf}")
    print()
    
    if analisador.analisar_pdf():
        # Gera e exibe relatório
        relatorio = analisador.gerar_relatorio()
        print(relatorio)
        
        # Salva relatório em arquivo
        nome_arquivo_relatorio = Path(caminho_pdf).stem + "_relatorio.txt"
        caminho_relatorio = Path("results") / nome_arquivo_relatorio
        
        # Cria a pasta results se não existir
        Path("results").mkdir(exist_ok=True)
        
        with open(caminho_relatorio, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        
        print(f"\nRelatório salvo em: {caminho_relatorio}")
    else:
        print("Falha na análise do PDF.")
        sys.exit(1)

if __name__ == "__main__":
    main()
