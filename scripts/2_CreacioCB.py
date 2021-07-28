"""
Genera el codi de barres a partir del número de DNI
"""
import pandas as pd
import random
import os
import re
from barcode import EAN13
from barcode.writer import ImageWriter

dir_path = os.path.dirname(os.path.realpath(__file__))

# Importació dades
profes = pd.read_csv(dir_path + '/../files/professors_dni.csv', sep=",", index_col=0)

# Neteja de dades
profes = profes.drop(columns=['NomHorari'])
profes = profes.loc[profes.Dni.isna() == False, :]
profes['Dni'] = profes['Dni'].apply(lambda s: re.sub('(^0)', '', s))


# Generar codi de barres
def generaCodi(dni):
    nif = int(re.findall('\d+', dni)[0])
    random.seed(nif)
    return random.randint(100000000000, 999999999999)

profes['CodiBarres'] = profes['Dni'].apply(generaCodi)


# Directori codi

if not os.path.exists(dir_path + "/../codis"):
    os.makedirs(dir_path + "/../codis")

# Imprimir codi de barres
for i in profes.index:
    codi = str(profes.loc[i, 'CodiBarres'])
    nom = profes.loc[i, 'Nom'] + profes.loc[i, 'Cognom']
    my_code = EAN13(codi, writer=ImageWriter())
    my_code.save(dir_path + "/../codis/" + nom)

# Exportar dades
profes.to_csv(dir_path + '/../files/professors.csv', index=False)