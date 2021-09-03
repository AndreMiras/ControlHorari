"""
Genera el fitxer /files/professors_bd.csv necessari per a la importació a la BD

Requereix el fitxer /files/professors.csv amb les columnes:
DNI,Nom,Cognom,Departament,CodiHorari
"""
import pandas as pd
import os
import re

dir_path = os.path.dirname(os.path.realpath(__file__))

# Importació dades
profes = pd.read_csv(dir_path + '/../files/professors.csv', sep=",")

# Neteja de dades
profes = profes.loc[profes.Dni.isna() == False, :]
profes = profes.loc[profes.CodiHorari.isna() == False, :]
profes.fillna('', inplace=True)
profes['CodiHorari'] = profes['CodiHorari'].astype(int)
profes['Dni'] = profes['Dni'].apply(lambda s: re.sub('(^0)', '', s))

# Exportar dades
profes.to_csv(dir_path + '/../files/professors_bd.csv', index=False)
