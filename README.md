# Analisador PDF Financeiro

Ferramenta para análise detalhada de demonstrativos financeiros em PDF, com extração automática de valores, agrupamento diário e geração de relatórios. Interface gráfica simplificada com drag-and-drop.

## Funcionalidades
- Extração automática de valores financeiros de PDFs
- Agrupamento diário dos valores líquidos
- Subtração automática de FUNARPEN e ISSQN por dia
- Relatórios organizados em pasta `results/`
- Interface gráfica moderna (drag-and-drop)
- Pronto para gerar executável único (.exe)

## Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/analisador-pdf-financeiro.git
   cd analisador-pdf-financeiro
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Uso Local (Python)
Execute o launcher:
```bash
python main_launcher.py
```

## Gerar Executável (.exe)
1. Instale o PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Gere o executável:
   ```bash
   pyinstaller --onefile --windowed main_launcher.py
   ```
3. O arquivo estará em `dist/main_launcher.exe`.

## Como Usar
- Abra o programa.
- Arraste e solte o(s) PDF(s) na área indicada.
- Clique em "Analisar".
- O relatório será salvo em `results/`.

## Estrutura do Projeto
```
app/
  sergio.py
  interface_dragdrop.py
main_launcher.py
requirements.txt
results/
```

## Licença
MIT 