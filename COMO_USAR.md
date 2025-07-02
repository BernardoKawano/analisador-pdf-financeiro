# 🚀 Como Usar - Interface Gráfica

## Instalação Rápida

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Executar interface:**
   ```bash
   python interface_simples.py
   ```

## 📋 Passo a Passo

### 1. Abrir a Interface
- Execute `python interface_simples.py`
- A janela "Analisador de PDF" aparecerá

### 2. Selecionar Arquivo
- Clique no botão **"📂 Selecionar Arquivo PDF"**
- Navegue até a pasta onde está seu PDF
- Selecione o arquivo e clique em "Abrir"

### 3. Analisar PDF
- O nome do arquivo aparecerá na interface
- Clique no botão **"🔍 Analisar PDF"**
- Aguarde a barra de progresso (pode demorar alguns segundos)

### 4. Ver Resultados
- Os resultados aparecerão na área de texto
- Uma mensagem de sucesso será exibida
- O arquivo .txt será salvo automaticamente na pasta `results/`

### 5. Acessar Arquivo
- Clique em **"📁 Abrir Pasta de Resultados"**
- O explorador abrirá na pasta com o relatório .txt

## 🔧 Botões da Interface

| Botão | Função |
|-------|--------|
| 📂 Selecionar Arquivo PDF | Escolhe o arquivo PDF para análise |
| 🔍 Analisar PDF | Inicia a análise do arquivo selecionado |
| 🗑️ Limpar | Limpa tudo e reinicia a interface |
| 📁 Abrir Pasta de Resultados | Abre a pasta onde estão os relatórios |

## 📊 O que a Análise Faz

1. **Lê todas as páginas** do PDF
2. **Filtra páginas** com o campo bancário específico
3. **Extrai valores** demonstrativos, FUNARPEN e ISSQN
4. **Calcula totais diários** e consolidados
5. **Gera relatório** completo em arquivo .txt

## ❗ Solução de Problemas

### Erro: "Arquivo não encontrado"
- Verifique se o caminho do arquivo está correto
- Certifique-se de que o arquivo existe

### Erro: "Campo bancário não encontrado"
- O PDF deve conter: "Ag./Cod. Cedente: 3162/730791-8"
- Verifique se é o PDF correto

### Interface não abre
- Verifique se Python está instalado
- Execute: `pip install PyPDF2`

### Análise demora muito
- PDFs grandes podem demorar alguns minutos
- Aguarde a barra de progresso terminar

## 📁 Arquivos Gerados

- **Relatório .txt**: `results/{nome_pdf}_relatorio.txt`
- **Conteúdo**: Valores, totais diários, estatísticas completas

## 💡 Dicas

- Use a interface gráfica para facilitar o uso
- Os relatórios são salvos automaticamente
- Você pode analisar múltiplos PDFs sem fechar a interface
- Use o botão "Limpar" para começar uma nova análise 