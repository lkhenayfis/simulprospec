import os
import pandas as pd
from datetime import datetime
from simulprospec.montadeck import le_cenarios
from inewave.newave.dger import DGer

def gera_vetor_datas(infocens: tuple, dataref: tuple):

    """
    Monta vetor de datas para subset dos DataFrames de dados

    Parametros
    ----------
    infocens : tuple
        Tupla contendo comprimento dos cenarios e numero de cenarios simulados,
        respectivamente
    dataref : tuple
        Tupla contendo ano e mes, como inteiros, da data de referencia do PMO
    """

    if dataref[1] + infocens[0] - 1 > 12:
        endmonth = dataref[1] + infocens[0] - 1 - 12
        endyear = dataref[0] + 1
    else:
        endmonth = dataref[1] + infocens[0] - 1
        endyear = dataref[0]

    datas_simul = pd.date_range(
        datetime(year = dataref[0], month = dataref[1], day = 1),
        datetime(year = endyear, month = endmonth, day = 1),
        freq = "MS",
    )

    return datas_simul

def le_arquivo(arq: str, datas: pd.DatetimeIndex, infocens: tuple) -> pd.DataFrame:

    """
    Realiza a leitura de um arquivo de simulacao final do SIN em blocos qualquer
    localizado no diretorio dir

    Parametros
    ----------
    arq : str
        Caminho do arquivo a ser lido
    datas : pd.DatetimeIndex
        Array de Datetimes indicando quais datas extrair do arquivo
    infocens : tuple
        Tupla contendo comprimento dos cenarios e numero de cenarios simulados,
        respectivamente
    """

    dados = pd.read_csv(arq)
    dados["dataInicio"] = pd.to_datetime(dados["dataInicio"])
    cols = dados.columns
    cols = cols[:(cols.tolist().index("dataFim")) + infocens[1] + 1]

    dados = dados.loc[(dados["dataInicio"] >= datas[0]) & (dados["dataInicio"] <= datas[-1]), cols]

    return dados

def le_saidas(dir: str) -> None:

    """
    Leitura dos arquivos simulados de interesse e salvamento de um zip os contendo

    Se assume que a pasta onde estao as saidas do sintetizador esta na raiz do caso, de modo que um
    nivel acima estejam os arquivos do deck como o dger.dat

    Parametros
    ----------
    dir : str
        Diretorio contendo saidas do sintetizador-newave
    """

    infocens = le_cenarios("..", True)
    dataref = (DGer.le_arquivo("..").ano_inicio_estudo, DGer.le_arquivo("..").mes_inicio_estudo)

    datas = gera_vetor_datas(infocens, dataref)

    for (root, dirs, files) in os.walk(dir):
        for file in files:
            file = os.path.join(root, file)
            dado = le_arquivo(file, datas, infocens)
            dado.to_csv(file, index = False)

    pass