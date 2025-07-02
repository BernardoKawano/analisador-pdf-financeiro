# Analisador de PDF - Valores Financeiros

Script Python para análise detalhada de arquivos PDF com foco em extração e cálculo de valores financeiros específicos.

## Funcionalidades

- **Leitura sequencial completa**: Processa todas as páginas do PDF sem omissões
- **Filtro por campo bancário**: Processa apenas páginas com o campo específico "Ag./Cod. Cedente: 3162/730791-8"
- **Extração de valores demonstrativos**: Captura valores no formato "Valor Demonstrativo: R$ xxx"
- **Processamento FUNARPEN**: Identifica e subtrai valores associados a FUNARPEN
- **Exclusão ISSQN**: Lista valores de ISSQN sem incluí-los nos cálculos
- **Relatório estruturado**: Gera relatório completo com totais e estatísticas

## Instalação

1. **Instalar dependências**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verificar instalação**:
   ```bash
   python -c "import PyPDF2; print('PyPDF2 instalado com sucesso')"
   ```

## Uso

### Linha de Comando

```bash
python sergio.py <caminho_do_pdf>
```

**Exemplo**:
```bash
python sergio.py documento.pdf
```

### Saída

O script gera:

1. **Saída no console**: Progresso da análise e relatório completo
2. **Arquivo de relatório**: `{nome_do_pdf}_relatorio.txt` com análise detalhada

## Estrutura do Relatório

O relatório contém as seguintes seções:

### 1. Valores Demonstrativos Considerados
- Lista todos os valores "Valor Demonstrativo" encontrados
- Inclui número da página, linha completa e valor

### 2. Valores Subtraídos por FUNARPEN
- Lista valores FUNARPEN identificados
- Inclui texto da linha, valor exato e página

### 3. Valores Ignorados por Conter ISSQN
- Lista valores ISSQN encontrados (não incluídos nos cálculos)
- Inclui texto da linha, valor e página

### 4. Resumo Consolidado
- Total de valores demonstrativos
- Total de subtrações FUNARPEN
- Valor líquido final

### 5. Estatísticas
- Páginas processadas
- Contadores de cada tipo de valor

## Critérios de Processamento

### Filtro Bancário
- Apenas páginas contendo exatamente: `Ag./Cod. Cedente: 3162/730791-8`

### Valores Demonstrativos
- Busca por: `Valor Demonstrativo: R$ xxx`
- Formato brasileiro: vírgula como separador decimal

### FUNARPEN
- Busca por linhas contendo "FUNARPEN"
- Verifica valor na mesma linha, linha anterior ou posterior
- Subtrai do total da página

### ISSQN
- Busca por: `ISSQN - Imposto sobre Serviços de Qualquer Natureza`
- Lista mas não inclui nos cálculos

## Formato de Valores

O script reconhece valores no formato brasileiro:
- `R$ 1.234,56` (ponto como separador de milhares, vírgula como decimal)
- `R$ 21,00`
- `R$ 1.000,00`

## Tratamento de Erros

- **Arquivo não encontrado**: Exibe erro e encerra
- **PDF corrompido**: Exibe erro e encerra
- **PyPDF2 não instalado**: Exibe instruções de instalação
- **Valores inválidos**: Ignora valores que não podem ser convertidos

## Exemplo de Saída

```
ANALISADOR DE PDF - VALORES FINANCEIROS
==================================================
Analisando arquivo: documento.pdf

PDF carregado: 5 páginas encontradas
============================================================
Processando página 1...
  Página 1: Campo bancário não encontrado - ignorando
Processando página 2...
  Página 2: Campo bancário encontrado - processando
Processando página 3...
  Página 3: Campo bancário encontrado - processando
============================================================
Análise concluída: 2 páginas processadas

================================================================================
RELATÓRIO DE ANÁLISE DE PDF - VALORES FINANCEIROS
================================================================================

1. VALORES DEMONSTRATIVOS CONSIDERADOS
--------------------------------------------------
Página 2: Valor Demonstrativo: R$ 1.234,56
  Valor: R$ 1,234.56

2. VALORES SUBTRAÍDOS POR FUNARPEN
--------------------------------------------------
Página 3: FUNARPEN | R$ 21,00
  Valor: R$ 21.00

3. VALORES IGNORADOS POR CONTER ISSQN
--------------------------------------------------
Nenhum valor ISSQN encontrado.

4. RESUMO CONSOLIDADO
--------------------------------------------------
Total de valores demonstrativos: R$ 1,234.56
Total de subtrações FUNARPEN: R$ 21.00
Valor líquido final: R$ 1,213.56

5. ESTATÍSTICAS
--------------------------------------------------
Páginas com campo bancário válido: 2
Valores demonstrativos encontrados: 1
Valores FUNARPEN encontrados: 1
Valores ISSQN encontrados: 0

================================================================================

Relatório salvo em: documento_relatorio.txt
```

## Requisitos do Sistema

- Python 3.7 ou superior
- PyPDF2 3.0.0 ou superior
- Sistema operacional: Windows, macOS ou Linux

## Solução de Problemas

### Erro: "PyPDF2 não está instalado"
```bash
pip install PyPDF2
```

### Erro: "Arquivo não encontrado"
Verifique se o caminho do arquivo PDF está correto e se o arquivo existe.

### Erro: "Falha na análise do PDF"
O arquivo PDF pode estar corrompido ou protegido por senha.

## Licença

Este projeto é de uso livre para fins educacionais e comerciais. 