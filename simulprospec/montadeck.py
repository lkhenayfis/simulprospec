import os
from inspect import _void
import pandas as pd
from inewave.newave.dger import DGer
from inewave.newave.vazoes import Vazoes

def le_cenarios(dir: str, early: bool = False) -> tuple:

    """
    Le um arquivo de cenarios para simulacao num formato especifico pre determinado em conjunto com
    a PRH
    
    Parametros
    ----------
    dir : str
        Diretorio onde se encontra o arquivo de cenarios (nomeado cenarios_vazao.csv)
    early : bool
        Booleano indicando se deve ser retornado uma tupla com o arquivo de cenarios processado,
        numero de meses e numero de cenarios (True) ou apenas numero de meses e de cenarios (False)
    """

    arq_cenarios = dir + "/cenarios_vazao.csv"

    cenarios = pd.read_csv(arq_cenarios)
    colunas = []
    for i in range(cenarios.columns.shape[0]):
        colunas.append(cenarios.columns[i].upper())
    cenarios.columns = colunas
    nmeses = cenarios.shape[1] - 2

    indcen = cenarios["CENARIO"].unique()
    ncens = len(indcen)

    postos = cenarios["POSTO"].unique()

    if early:
        return (nmeses, ncens)

    out = []
    for i in indcen:
        aux = cenarios[cenarios["CENARIO"] == i]
        aux = aux.iloc[:, 2:].T
        aux.columns = postos
        out.append(aux)

    return (out, nmeses, ncens)

def modifica_dger(dir: str, modo: int = 1) -> None:

    """
    Modifica o dger.dat para rodar apenas simulacao final com series historicas

    Parametros
    ----------
    dir : str
        Diretorio onde se encontram os arquivos de entrada do caso
    modo : int
        Modo de execucao: 1 prepara dger para simulacao historica; 2 p consistencia de dados
    """

    dadosgerais = DGer.le_arquivo(dir)

    if modo == 1:
        dadosgerais.tipo_execucao = 0
        dadosgerais.tipo_simulacao_final = 2
    else:
        dadosgerais.tipo_execucao = 1
        dadosgerais.tipo_simulacao_final = 3
        
    dadosgerais.escreve_arquivo(dir)

    pass

def modifica_vazoes(dir: str) -> None:

    """
    Modifica o vazoes.dat com os cenarios externos. 

    Parametros
    ----------
    dir : str
        Diretorio onde se encontram os arquivos de entrada do caso e o arquivo de cenarios chamado
        cenarios_vazao.csv
    """

    dadosgerais = DGer.le_arquivo(dir)
    mesini = dadosgerais.mes_inicio_estudo

    vazoes = Vazoes.le_arquivo(dir)

    cenarios, nmeses, ncens = le_cenarios(dir)

    if not all(cenarios[0].columns == vazoes.vazoes.columns):
        raise Exception("Arquivo de cenarios nao contem todos os postos em vazoes.dat")
    
    meses_muda = [i + (mesini - 1) for i in range(nmeses)]
    reg_muda = [[12 * (i + 1) + meses_muda[j] for j in range(len(meses_muda))] for i in range(ncens)]

    for i in range(len(reg_muda)):
        substitui = cenarios[i]
        substitui.index = reg_muda[i]
        vazoes.vazoes.loc[reg_muda[i], vazoes.vazoes.columns] = cenarios[i]
    
    vazoes.escreve_arquivo(dir)
    vazoes.vazoes.to_csv("vazoes.csv")

    pass
