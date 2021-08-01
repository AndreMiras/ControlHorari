"""
Neteja fitxer horari
"""

import pandas as pd
import os

dir_path = os.path.dirname(os.path.realpath(__file__))


# ---------- Horari classes -----------

# Importació de dades dels horaris
horari = pd.read_csv(dir_path + '/../files/horari_tot.csv', sep=";", dtype=str)

# Neteja de dades
COLS = ['DIA,C,1','HORA,C,2','ABRE_ASIG,C,5',
        'NUM_PROF,C,4', 'ABRE_AULA,C,5','ABRE_GRUP,C,5']
horari = horari[COLS]
horari.columns = ['Dia','Hora','Assignatura',
                  'CodiHorari', 'Aula', 'Grup']

horari = horari.fillna('')

horari['Grup'] = horari.groupby(['Dia','Hora','CodiHorari'])['Grup'].transform(lambda s: "-".join(s))
horari.drop_duplicates(inplace=True)

horari.to_csv(dir_path + '/../files/horari.csv')

