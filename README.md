WIP

# FIIs Controle

Este é um projeto para gerenciar movimentações financeiras de FIIs com CSV importado direto da Área do Investidor

## Descrição

O projeto utiliza Python e bibliotecas como SQLAlchemy, Pandas, e Selenium para realizar várias operações:

- Carregar dados de movimentações financeiras de arquivos CSV para um banco de dados SQLite.
- Exibir e resumir informações sobre movimentações de FIIs.
- Permitir a inserção manual de dados de Subscrição.


## Como Usar

### Pré-requisitos

- Python 3.x
- Bibliotecas especificadas em `requirements.txt`

### Instalação

1. Clone o repositório: `git clone https://github.com/seu-usuario/nome-do-repositorio.git`
2. Instale as dependências: `pip install -r requirements.txt`

### Comandos

- `python app.py inicializar arquivos`: Inicializa os arquivos do banco de dados.
- `python app.py ler movimentacao arquivo.csv`: Lê e carrega movimentações de um arquivo CSV para o banco.
- `python app.py mostrar tudo`: Mostra todas as movimentações.
- `python app.py mostrar resumo`: Mostra um resumo das movimentações.
- `python app.py ler entrada_manual_subscricao`: Permite a inserção manual de uma subscrição.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir um pull request ou reportar problemas.

## Disclaimer

O projeto está no projeto bem inicial :-) Conhecimento de Python do autor é bem ínfimo.

