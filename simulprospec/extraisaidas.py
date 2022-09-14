import os
import tempfile
import pandas as pd
from datetime import datetime
from simulprospec.montadeck import le_cenarios
from zipfile import ZipFile
from inewave.config import MESES_DF
from inewave.newave.ree import REE
from inewave.newave.sistema import Sistema
from inewave.newave.dger import DGer
from inewave.newave.vazoes import Vazoes
from inewave.nwlistop.earmfp import Earmfp
from inewave.nwlistop.eafb import Eafb
from inewave.nwlistop.ghtot import Ghtot
from inewave.nwlistop.gttot import Gttot
from inewave.nwlistop.earmfpsin import EarmfpSIN
from inewave.nwlistop.eafbsin import EafbSIN
from inewave.nwlistop.ghtotsin import GhtotSIN
from inewave.nwlistop.gttotsin import GttotSIN

def arruma_blockfile(data: pd.DataFrame) -> pd.DataFrame:

    """
    Organiza um DataFrame na estrutura de blocos em um formato orientado por series
    nas colunas com a data correspondente nos labels

    Parametros
    ----------
    data : pandas.DataFrame
        um DataFrame com o arquivo em blocos lido pelas classes em inewave.nwlistop
    """

    anos = data["Ano"].unique().tolist()
    labels = pd.date_range(
        datetime(year = anos[0], month = 1, day = 1),
        datetime(year = anos[-1], month = 12, day = 1),
        freq = "MS",
    )

    out = pd.DataFrame()
    for a in anos:
        aux = data.loc[data["Ano"] == a, MESES_DF].T
        aux.columns = list(range(1, aux.shape[1] + 1))
        out = pd.concat([out, aux], ignore_index=True)
    out.index = labels

    return out

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

def le_aquivoREE(dir: str, cls: type, infocens: tuple, dataref: tuple) -> pd.DataFrame:

    """
    Realiza a leitura de um arquivo de simulacao final por REE em blocos qualquer
    localizado no diretorio dir

    Parametros
    ----------
    dir : str
        Diretorio contendo saidas do NWLISTOP
    cls : type
        Uma classe herdando de ArquivoREE para leitura do arquivo
    infocens : tuple
        Tupla contendo comprimento dos cenarios e numero de cenarios simulados,
        respectivamente
    dataref : tuple
        Tupla contendo ano e mes, como inteiros, da data de referencia do PMO
    """

    datas_simul = gera_vetor_datas(infocens, dataref)

    rees = REE.le_arquivo(dir)
    dados = pd.DataFrame()
    for i in range(rees.rees.shape[0]):
        dado_i = cls.le_arquivo(dir, cls.__name__.lower() + "%03d" %(i + 1) + ".out")
        vals = arruma_blockfile(dado_i.valores)
        vals = vals.loc[datas_simul, 1:infocens[1]]
        vals["REE"] = dado_i.ree
        dados = pd.concat([dados, vals])

    return dados

def le_aquivoMERC(dir: str, cls: type, infocens: tuple, dataref: tuple) -> pd.DataFrame:

    """
    Realiza a leitura de um arquivo de simulacao final por REE em blocos qualquer
    localizado no diretorio dir

    Parametros
    ----------
    dir : str
        Diretorio contendo saidas do NWLISTOP
    cls : type
        Uma classe herdando de ArquivoREE para leitura do arquivo
    infocens : tuple
        Tupla contendo comprimento dos cenarios e numero de cenarios simulados,
        respectivamente
    dataref : tuple
        Tupla contendo ano e mes, como inteiros, da data de referencia do PMO
    """

    datas_simul = gera_vetor_datas(infocens, dataref)

    submercs = Sistema.le_arquivo(dir).mercado_energia["Subsistema"].unique()
    dados = pd.DataFrame()
    for i in submercs:
        dado_i = cls.le_arquivo(dir, cls.__name__.lower() + "%03d" %(i) + ".out")
        vals = arruma_blockfile(dado_i.valores)
        vals = vals.loc[datas_simul, 1:infocens[1]]
        vals["SUBMERCADO"] = i
        dados = pd.concat([dados, vals])

    return dados

def le_aquivoSIN(dir: str, cls: type, infocens: tuple, dataref: tuple) -> pd.DataFrame:

    """
    Realiza a leitura de um arquivo de simulacao final do SIN em blocos qualquer
    localizado no diretorio dir

    Parametros
    ----------
    dir : str
        Diretorio contendo saidas do NWLISTOP
    cls : type
        Uma classe herdando de ArquivoSIN para leitura do arquivo
    infocens : tuple
        Tupla contendo comprimento dos cenarios e numero de cenarios simulados,
        respectivamente
    dataref : tuple
        Tupla contendo ano e mes, como inteiros, da data de referencia do PMO
    """

    datas_simul = gera_vetor_datas(infocens, dataref)

    earm_sin = cls.le_arquivo(dir, cls.__name__.lower() + ".out")
    dados = arruma_blockfile(earm_sin.valores)
    dados = dados.loc[datas_simul, 1:infocens[1]]

    return dados

def le_saidas(dir: str) -> None:

    """
    Leitura dos arquivos simulados de interesse e salvamento de um zip os contendo

    Parametros
    ----------
    dir : str
        Diretorio contendo saidas do NWLISTOP
    """

    infocens = le_cenarios(dir, True)
    dataref = (DGer.le_arquivo(dir).ano_inicio_estudo, DGer.le_arquivo(dir).mes_inicio_estudo)

    tempdir = tempfile.mkdtemp()
    outzip = os.path.join(dir, "simul_prospec.zip")

    vazoes = Vazoes.le_arquivo(dir)
    vazoes.vazoes.to_csv(os.path.join(tempdir, "vazoes.csv"))

    earm_ree = le_aquivoREE(dir, Earmfp, infocens, dataref)
    earm_ree.to_csv(os.path.join(tempdir, "earmfp_ree.csv"))

    eafb_ree = le_aquivoREE(dir, Eafb, infocens, dataref)
    eafb_ree.to_csv(os.path.join(tempdir, "eafb_ree.csv"))

    ghtot_ree = le_aquivoREE(dir, Ghtot, infocens, dataref)
    ghtot_ree.to_csv(os.path.join(tempdir, "ghtot_ree.csv"))

    gttot_merc = le_aquivoMERC(dir, Gttot, infocens, dataref)
    gttot_merc.to_csv(os.path.join(tempdir, "gttot_merc.csv"))

    earm_sin = le_aquivoSIN(dir, EarmfpSIN, infocens, dataref)
    earm_sin.to_csv(os.path.join(tempdir, "earmfp_sin.csv"))

    eafb_sin = le_aquivoSIN(dir, EafbSIN, infocens, dataref)
    eafb_sin.to_csv(os.path.join(tempdir, "eafb_sin.csv"))

    ghtot_sin = le_aquivoSIN(dir, GhtotSIN, infocens, dataref)
    ghtot_sin.to_csv(os.path.join(tempdir, "ghtot_sin.csv"))

    gttot_sin = le_aquivoSIN(dir, GttotSIN, infocens, dataref)
    gttot_sin.to_csv(os.path.join(tempdir, "gttot_sin.csv"))

    with ZipFile(outzip, "w") as zip:
        for path, subdir, files in os.walk(tempdir):
            for file in files:
                file_name = os.path.join(path, file)
                zip.write(file_name, arcname = file)

    pass