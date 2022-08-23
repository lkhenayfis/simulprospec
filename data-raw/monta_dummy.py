import pandas as pd
import random

def add_noise(series):
    noise = [random.normalvariate(0, 1) for i in range(series.size)]
    noise = noise * (series != 0)
    return series.add(noise)

ncens = 30

dd = pd.read_csv("in/dummy_cenarios_prospec.csv", skipinitialspace = True)
dd.columns = dd.columns.str.rstrip()

cencol = ["MES" + str(i + 1) for i in range(dd.shape[1] - 2)]

variacoes = []

for i in range(ncens):
    aux = dd.copy()
    aux[cencol] = aux[cencol].apply(add_noise)
    aux["CENARIO"] = i
    variacoes.append(aux)

out = pd.concat(variacoes)

out.to_csv("in/dummy_cenarios.csv", index = False)