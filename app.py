from datetime import datetime
import click
import csv
import os
import os.path
from sqlalchemy import create_engine
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Date, Float, desc, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import yfinance as yf




arquivo_banco_de_dados = 'banco_fiis_controle.db'
Base = declarative_base()
engine = engine = create_engine('sqlite:///banco_fiis_controle.db')  # echo=True mostra as instruções SQL geradas

class Movimentacao(Base):
    __tablename__ = 'movimentacao'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_IO = Column(String)
    data = Column(Date)
    tipo_movimentacao = Column(String)
    produto = Column(String)
    instituicao = Column(String)
    quantidade = Column(Integer)
    preco_unitario = Column(Float)
    valor_operacao = Column(Float)
    
class Categoria(Base):
    __tablename__ = 'categoria'
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_negociacao = Column(String)
    categoria = Column(String)

class Dados_FII(Base):
    __tablename__ = 'dados_fii'
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_negociacao = Column(String)
    valor_patrimonial = Column(Float)
    cotacao = Column(Float)
    patrimonio_liquido = Column(String)
    dy = Column(String)

Base.metadata.create_all(engine)

def criar_tabela_resumo():
    engine = retorna_engine()  # Substitua isso pela função que retorna sua engine

    metadata = MetaData()

    # Defina uma tabela com as colunas correspondentes à estrutura da sua query
    nova_tabela = Table(
        'nova_tabela', metadata,
        Column('ticker', String),
        Column('categoria', String),
        Column('total_dividendos', Float),
        Column('total_operado', Float),
        Column('quantidade', Float),
        Column('preco_medio', Float),
        Column('dy_dados_fii', Float),
        Column('valor_patrimonial', Float),
        Column('patrimonio_liquido', Float)
    )

    # Crie a tabela no banco de dados
    metadata.create_all(bind=engine)
    engine.execute("CREATE TABLE IF NOT EXISTS nova_tabela ();")  # Cria a tabela vazia

    # Execute a query e insira os resultados na nova tabela
    with engine.connect() as conn:
        query = """SELECT 
                            SUBSTR(m.produto, 1, 4) AS ticker,
                            c.categoria,
                            SUM(CASE WHEN m.tipo_movimentacao = 'Rendimento' THEN m.valor_operacao ELSE 0 END) AS total_dividendos,
                            SUM(CASE WHEN m.tipo_movimentacao = 'Transferência - Liquidação' THEN
                                        CASE WHEN m.tipo_IO = 'Credito' THEN m.valor_operacao
                                            WHEN m.tipo_IO = 'Debito' THEN -m.valor_operacao ELSE 0 END
                                    ELSE 0 END) AS total_operado,
                            SUM(CASE WHEN m.tipo_movimentacao IN ('Transferência - Liquidação', 'Desdobro', 'Subscrição') THEN 
                                            CASE 
                                                WHEN m.tipo_IO = 'Credito' THEN m.quantidade
                                                WHEN m.tipo_IO = 'Debito' THEN -m.quantidade 
                                                ELSE 0 
                                            END 
                                        ELSE 0 
                                    END) AS quantidade,
                            CASE WHEN SUM(CASE WHEN m.tipo_movimentacao = 'Transferência - Liquidação' THEN
                                                    CASE WHEN m.tipo_IO = 'Credito' THEN m.quantidade
                                                        WHEN m.tipo_IO = 'Debito' THEN -m.quantidade ELSE 0 END
                                                    ELSE 0 END) != 0
                                    THEN SUM(CASE WHEN m.tipo_movimentacao IN ('Transferência - Liquidação', 'Subscrição') THEN
                                                        CASE WHEN m.tipo_IO = 'Credito' THEN m.valor_operacao
                                                            WHEN m.tipo_IO = 'Debito' THEN -m.valor_operacao ELSE 0 END
                                                        ELSE 0 END) /
                                        SUM(CASE WHEN m.tipo_movimentacao IN ('Transferência - Liquidação', 'Desdobro', 'Subscrição') THEN
                                                        CASE WHEN m.tipo_IO = 'Credito' THEN m.quantidade
                                                            WHEN m.tipo_IO = 'Debito' THEN -m.quantidade ELSE 0 END
                                                        ELSE 0 END)
                                    ELSE 0 END AS preco_medio,
                            fii.dy AS dy_dados_fii,
                            fii.valor_patrimonial,
                            fii.patrimonio_liquido
                        FROM movimentacao m
                        LEFT JOIN categoria c ON SUBSTR(m.produto, 1, 4) = SUBSTR(c.codigo_negociacao, 1, 4)
                        LEFT JOIN dados_fii fii ON SUBSTR(m.produto, 1, 4) = SUBSTR(fii.codigo_negociacao, 1, 4)
                        GROUP BY ticker, categoria
                        ORDER BY ticker;"""
        result_proxy = conn.execute(query)
        result = result_proxy.fetchall()

        # Mapeie os resultados da query para um dicionário para inserção na tabela
        insert_values = [{col.name: value for col, value in zip(result_proxy._metadata.keys, row)} for row in result]
        conn.execute(nova_tabela.insert().values(insert_values))


def retorna_engine():
    return engine

def cria_sessao_banco():
    Session = sessionmaker(bind=retorna_engine())
    session = Session()
    return session

def converter_data(string_data):
    return datetime.strptime(string_data, '%d/%m/%Y').date()    

def converter_valor(string_valor):
    click.echo(string_valor)
    if string_valor.strip() == '-':
        return 0.0

    valor_limpo = string_valor.replace('R$', '').strip().replace(',', '')  # Remove 'R$', spaces, and replace comma with dot
    if valor_limpo == '':
        return 0.0  # If the string becomes empty after removing characters, return 0.0

    return float(valor_limpo)


def deleta_banco_de_dados():
    if (os.path.isfile(arquivo_banco_de_dados)):
        os.remove(arquivo_banco_de_dados)

def ler_csv(nome_arquivo):
    with open(nome_arquivo, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            click.echo(row)

def valida_dado_fii(linha):
    for dado in linha:
        if (dado == 0 or dado == '' or dado == '-'):
            return False
    return True
    
def salvar_csv_no_banco(arquivo_entrada, tipo):
    session = cria_sessao_banco()

    if not verificar_csv(arquivo_entrada, tipo):
        return 

    if (tipo == 'movimentacao'):
        # Lógica para salvar o arquivo
        with open(arquivo_entrada, newline='', encoding='utf-8') as arquivo_entrada:
            leitor = csv.reader(arquivo_entrada)
            next(leitor)
            for linha in leitor:
                nova_movimentacao = Movimentacao(tipo_IO=linha[0], data=converter_data(linha[1]), tipo_movimentacao=linha[2], produto=linha[3].strip(), instituicao = linha[4], quantidade = linha[5], preco_unitario = converter_valor(linha[6]), valor_operacao = converter_valor(linha[7]) )  # Adicione mais colunas conforme necessário
                session.add(nova_movimentacao)
        session.commit()
    
    if (tipo == 'categoria'):
        with open(arquivo_entrada, newline='', encoding='utf-8') as arquivo_entrada:
            leitor = csv.reader(arquivo_entrada)
            next(leitor)
            for linha in leitor:
                nova_categoria = Categoria(codigo_negociacao=linha[0], categoria=linha[1] )  # Adicione mais colunas conforme necessário
                session.add(nova_categoria)
        session.commit()
    
    if (tipo == 'dados_fii'):
        with open(arquivo_entrada, newline='', encoding='utf-8') as arquivo_entrada:
            leitor = csv.reader(arquivo_entrada)
            next(leitor)
            for linha in leitor:
                if valida_dado_fii(linha):
                    novo_dados_fii = Dados_FII(codigo_negociacao = linha[0], valor_patrimonial = linha[1], cotacao = linha[2], patrimonio_liquido = linha[3], dy = linha[4])
                    session.add(novo_dados_fii) 
        session.commit()




    click.echo(f"Salvando arquivo no banco de dados.")

def verificar_csv(arquivo, tipo):
    with open(arquivo, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        linhas = list(reader)

        if len(linhas) == 0:
            click.echo("Arquivo vazio.")
            return False

        header = linhas[0]  # Primeira linha é o cabeçalho

        if len(header) == 0:
            print("Arquivo sem cabeçalho.")
            return False

        match tipo:
            case 'movimentacao': numero_de_colunas_esperado = 8 # O padrão tem 8, tem que voltar depois o valor pra 8
            case 'categoria': numero_de_colunas_esperado = 2
            case 'dados_fii': numero_de_colunas_esperado = 5
            
        if len(header) != numero_de_colunas_esperado:
            print(f"Arquivo com número incorreto de colunas. Esperado: {numero_de_colunas_esperado}, Encontrado: {len(header)}")
            return False

        # Caso tudo esteja correto
        print("Arquivo aparentemente válido.")
        return True

@click.group()
def main():
    pass

@main.group()
def inicializar():
    """Comandos para inicializar dados"""
    pass

@main.group()
def ler():
    """Comandos para ler dados"""
    pass

@main.group()
def mostrar():
    """Comandos para ler dados"""
    pass

@inicializar.command()
@click.option("--deletar-existente", default=False, help='Forçar que os arquivos do banco de dados sejam deletados')
def arquivos(deletar_existente):
    """Comandos para inicializar arquivos dados"""

    if(deletar_existente):
        click.echo("Deletando todos os arquivos e recriando a base")
        deleta_banco_de_dados()
    
    criar_tabela_resumo()
    
@ler.command()
@click.argument('arquivo', type=click.Path(exists=True))
def movimentacao(arquivo):
    """Ler e exibir movimentacao de um arquivo CSV"""
    click.echo(f"Carregando '{arquivo}' na base de dados:")
    ler_csv(arquivo)
    salvar_csv_no_banco(arquivo, 'movimentacao')
    
@ler.command()
@click.argument('arquivo', type=click.Path(exists=True))
def categoria(arquivo):
    """Ler e exibir movimentacao de um arquivo CSV"""
    click.echo(f"Carregando '{arquivo}' na base de dados:")
    ler_csv(arquivo)
    salvar_csv_no_banco(arquivo, "categoria")   
    
@ler.command()
@click.argument('arquivo', type=click.Path(exists=True))
def dados_fii(arquivo):
    """Ler e exibir movimentacao de um arquivo CSV"""
    click.echo(f"Carregando '{arquivo}' na base de dados:")
    ler_csv(arquivo)
    salvar_csv_no_banco(arquivo, "dados_fii")    
  
@mostrar.command()
@click.option('--pagina', default=1, help='Número da página')
@click.option('--itens_por_pagina', default=10, help='Quantidade de itens por página')
def tudo(pagina, itens_por_pagina):
    deslocamento = (pagina - 1) * itens_por_pagina
    session = cria_sessao_banco()
    dados = session.query(Movimentacao).order_by(desc(Movimentacao.data)).limit(itens_por_pagina).offset(deslocamento).all()
    
    df = pd.DataFrame([{key: value for key, value in vars(dado).items() if not key.startswith('_sa_instance_state')} for dado in dados])


    click.echo(df)

@mostrar.command()
def resumo():
    session = cria_sessao_banco()
    consulta_sql = text("""SELECT 
                            SUBSTR(m.produto, 1, 4) AS ticker,
                            c.categoria,
                            SUM(CASE WHEN m.tipo_movimentacao = 'Rendimento' THEN m.valor_operacao ELSE 0 END) AS total_dividendos,
                            SUM(CASE WHEN m.tipo_movimentacao IN ('Transferência - Liquidação', 'Subscrição') THEN
                                        CASE WHEN m.tipo_IO = 'Credito' THEN m.valor_operacao
                                            WHEN m.tipo_IO = 'Debito' THEN -m.valor_operacao ELSE 0 END
                                    ELSE 0 END) AS total_operado,
                            SUM(CASE WHEN m.tipo_movimentacao IN ('Transferência - Liquidação', 'Desdobro', 'Subscrição') THEN 
                                            CASE 
                                                WHEN m.tipo_IO = 'Credito' THEN m.quantidade
                                                WHEN m.tipo_IO = 'Debito' THEN -m.quantidade 
                                                ELSE 0 
                                            END 
                                        ELSE 0 
                                    END) AS quantidade,
                            CASE WHEN SUM(CASE WHEN m.tipo_movimentacao = 'Transferência - Liquidação' THEN
                                                    CASE WHEN m.tipo_IO = 'Credito' THEN m.quantidade
                                                        WHEN m.tipo_IO = 'Debito' THEN -m.quantidade ELSE 0 END
                                                    ELSE 0 END) != 0
                                    THEN SUM(CASE WHEN m.tipo_movimentacao IN ('Transferência - Liquidação', 'Subscrição') THEN
                                                        CASE WHEN m.tipo_IO = 'Credito' THEN m.valor_operacao
                                                            WHEN m.tipo_IO = 'Debito' THEN -m.valor_operacao ELSE 0 END
                                                        ELSE 0 END) /
                                        SUM(CASE WHEN m.tipo_movimentacao IN ('Transferência - Liquidação', 'Desdobro', 'Subscrição') THEN
                                                        CASE WHEN m.tipo_IO = 'Credito' THEN m.quantidade
                                                            WHEN m.tipo_IO = 'Debito' THEN -m.quantidade ELSE 0 END
                                                        ELSE 0 END)
                                    ELSE 0 END AS preco_medio,
                            fii.dy AS dy_dados_fii,
                            fii.valor_patrimonial,
                            fii.patrimonio_liquido
                        FROM movimentacao m
                        LEFT JOIN categoria c ON SUBSTR(m.produto, 1, 4) = SUBSTR(c.codigo_negociacao, 1, 4)
                        LEFT JOIN dados_fii fii ON SUBSTR(m.produto, 1, 4) = SUBSTR(fii.codigo_negociacao, 1, 4)
                        GROUP BY ticker, categoria
                        ORDER BY ticker;
                        """)
    resultados = session.execute(consulta_sql)
    colunas = resultados.keys()
    
    cotacao_atual = 'cotacao_atual'
    valor_total_atual = 'valor_total_atual'

    colunas_lista = list(colunas)
    colunas_lista.extend([cotacao_atual, valor_total_atual])
    # Convertendo de volta para uma tupla, se necessário
    colunas_atualizadas = tuple(colunas_lista)   
    
    dados = resultados.fetchall()
    novos_dados = []

    for dado in dados:
        
        novo_dado = list(dado)  # Converte a tupla para uma lista mutável
        if (novo_dado[0].startswith('Teso')):
            novo_dado.pop()
            continue
        
        ticker = novo_dado[0] + '11.SA'
        
        cotacao_atual = 0
        
        try:
            ativo = yf.Ticker(ticker)
            cotacao_atual = ativo.info['currentPrice']
            valor_total_atual = novo_dado[4] * cotacao_atual
            
            novo_dado.append(cotacao_atual) 
            novo_dado.append(valor_total_atual)
            novos_dados.append(novo_dado)  # Adiciona a lista atualizada à nova lista
            
        except:
            click.echo(f'Ativo {ticker}, não foi encontrado valor atual')
        
        
        

    
    df = pd.DataFrame(novos_dados, columns=colunas_atualizadas)

    click.echo(df)


def inserir_entrada_manual(objeto, tipo):
    session = cria_sessao_banco()

    if (tipo == 'subscricao'):  
        nova_subscricao = Movimentacao(tipo_IO='Credito', data=objeto['data'], tipo_movimentacao='Subscrição', produto=objeto['ticker'], instituicao = 'Manual', quantidade = objeto['quantidade'], preco_unitario = objeto['preco_unitario'], valor_operacao = (objeto['quantidade'] * objeto['preco_unitario']) )  # Adicione mais colunas conforme necessário
        session.add(nova_subscricao)
        
    session.commit()

    
        
@ler.command()
def entrada_manual_subscricao():
    ticker = click.prompt('Ticker', type=str)    
    quantidade = click.prompt('Quantidade', type=int)   
    preco_unitario = click.prompt('Preço Unitário', type=float)
    data = click.prompt('Data Efetivação', type=str)
    
    
    objeto = {
        'ticker': ticker,
        'quantidade': quantidade,
        'preco_unitario': (preco_unitario),
        'data': converter_data(data),
        'valor_operacao': quantidade * preco_unitario
    }
    
    click.echo(f'Inserindo no banco {ticker}, {quantidade} unidade por R${preco_unitario} cada. Valor total da operacao: {preco_unitario * quantidade}. Válido a partir de {converter_data(data)}')
    inserir_entrada_manual(objeto, 'subscricao')
    
if __name__ == '__main__':
    main()