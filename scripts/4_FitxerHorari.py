"""
Genera el fitxer horaris_bd.csv necessari per importar els horaris a la base de dades
Requereix el fitxer amb els horaris de GPUntis GPU001.TXT
"""

import pandas as pd
import os

dir_path = os.path.dirname(os.path.realpath(__file__))


# Importació de dades dels horaris
horari = pd.read_csv(dir_path + '/../files/GPU001.TXT', sep=",", dtype=str, header=None,
                     names=['Index','Grup','CodiHorari','Assignatura','Aula','Dia','Hora','1','2'])


# Neteja columnes i valors nuls
horari.drop(columns=['Index','1','2'], inplace=True)
horari = horari.loc[horari.CodiHorari.isna() == False, :]

# Codi horari com a enter
horari['CodiHorari'] = horari['CodiHorari'].str.slice(start=1)
horari['CodiHorari'] = horari['CodiHorari'].astype(int)
horari = horari.fillna('')

# Agrupació optatives
horari['Grup'] = horari.groupby(['Dia','Hora','CodiHorari'])['Grup'].transform(lambda s: "-".join(s))

horari.drop_duplicates(inplace=True)


# Exportació dades
horari.to_csv(dir_path + '/../files/horari_bd.csv', index=False)

