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

## TODO List

* Adicionar Animação de Loading:
 Implementar uma animação de carregamento durante a execução do comando de resumo para melhorar a experiência do usuário enquanto as informações são coletadas da API.

* Adicionar Opção --cached no Comando Mostrar Resumo:
  Incluir uma opção --cached no comando de mostrar resumo para recuperar os dados armazenados em cache pela aplicação, reduzindo a necessidade de acessar a API repetidamente. Esses dados serão utilizados para geração de relatórios e gráficos.
  
* Automatizar Subscrições na Área do Investidor da B3:
  Desenvolver uma solução para lidar com as subscrições na Área do Investidor da B3, já que atualmente não é fornecido o valor unitário da operação. Considerar a automação ou implementar uma alternativa eficiente para a entrada manual, especialmente para usuários que realizam múltiplas subscrições.
Esta lista pode servir como um guia para as próximas etapas do projeto, abordando áreas que precisam de atenção e melhorias.

* Melhorar README.md
  Melhorar estrutura, incluir exemplos, tutoriais, setup e documentar os comandos. 

