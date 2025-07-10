# Como Usar o Analisador de PDF - LumaLector

## Instalação

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Executar a aplicação
```bash
python main_flet.py
```

## Funcionalidades Implementadas

### ✅ Interface Gráfica Completa (Flet)
- 7 telas navegáveis com identidade visual personalizada
- Navegação com botões "Home" e "Voltar"
- Design responsivo com paleta de cores oficial

### ✅ Análise de PDF
- Validação robusta de arquivos PDF
- Extração de valores financeiros (líquido, demonstrativo, Funarpen, ISSQN)
- Identificação de datas e número de páginas
- Processamento com feedback visual

### ✅ Navegação e Fluxo
- **Tela 1**: Boas-vindas com opções principais
- **Tela 2**: Upload de arquivo PDF
- **Tela 3**: Confirmação do documento com miniatura
- **Tela 4**: Processamento com animação Lottie
- **Tela 5**: Resumo da análise com valores extraídos
- **Tela 6**: Opções de exportação
- **Tela 7**: Histórico de análises realizadas

### ✅ Exportação de Dados
- **TXT**: Relatório formatado em texto
- **CSV**: Dados estruturados para importação
- **Excel**: Planilha com formatação profissional

### ✅ Histórico Persistente
- Salva análises realizadas em `historico.json`
- Visualização cronológica das análises
- Acesso rápido a resultados anteriores

### ✅ Funcionalidades Adicionais
- Cópia de valores individuais para área de transferência
- Validação de integridade de arquivos PDF
- Geração de miniaturas (quando PyMuPDF disponível)
- Feedback visual com SnackBars informativos

## Personalização

### Cliente
Para personalizar o nome do cliente, edite a linha 19 em `main_flet.py`:
```python
NOME_CLIENTE = "Seu Nome Aqui"
```

### Logo
Substitua o arquivo `images/Logotipo-LumaLector.png` pelo logo desejado.

### Cores
As cores da identidade visual podem ser ajustadas nas linhas 8-15 de `main_flet.py`.

## Arquivos Gerados

- `results/`: Diretório com relatórios TXT e CSV
- `historico.json`: Histórico de análises
- Arquivos temporários de miniatura (pasta temp do sistema)

## Dependências Opcionais

### PyMuPDF (Recomendado)
Para geração de miniaturas reais dos PDFs:
```bash
pip install PyMuPDF
```

### Pandas + OpenPyXL (Recomendado)  
Para exportação em Excel:
```bash
pip install pandas openpyxl
```

## Solução de Problemas

### Erro ao carregar PDF
- Verifique se o arquivo não está corrompido
- Tamanho máximo: 100MB
- Formato suportado: PDF válido

### Funcionalidades indisponíveis
- Miniaturas: Instale PyMuPDF
- Exportação Excel: Instale pandas e openpyxl

### Navegação
- **Home**: Sempre retorna à tela inicial
- **Voltar**: Retorna à tela anterior no fluxo
- **Voltar ao Início**: Limpa dados e volta ao menu principal 