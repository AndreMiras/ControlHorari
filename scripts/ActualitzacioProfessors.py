"""
Actualitza les dades dels professors a la BD
Requereix el fitxer professors.csv
"""

import pandas as pd
import os
import re
import random
from dades import connexio

dir_path = os.path.dirname(os.path.realpath(__file__))

ct = connexio()

# Eliminació taula
with ct.cursor() as cursor:
    cursor.execute("DELETE FROM Professor;")
    ct.commit()

# Importació del fitxer
profes = pd.read_csv(dir_path + '/../files/professors.csv', sep=",")

# Neteja de dades
profes = profes.loc[profes.Dni.isna() == False, :]
profes = profes.loc[profes.CodiHorari.isna() == False, :]
profes.fillna('', inplace=True)
profes['CodiHorari'] = profes['CodiHorari'].astype(int)
profes['Dni'] = profes['Dni'].apply(lambda s: re.sub('(^0)', '', s))


# Generar codi de barres
def generaCodi(dni):
    nif = int(re.findall('\d+', dni)[0])
    random.seed(nif)
    return random.randint(100000000000, 999999999999)


profes['CodiBarres'] = profes['Dni'].apply(generaCodi)

# Importació BD
for i in profes.index:
    Dni = profes.loc[i,'Dni']
    Nom = profes.loc[i,'Nom']
    Cognom = profes.loc[i, 'Cognom']
    CodiHorari = str(profes.loc[i,'CodiHorari'])
    CodiBarres = str(profes.loc[i,'CodiBarres'])
    Departament = profes.loc[i,'Departament']

    insert = "INSERT INTO Professor (Dni, Nom, Cognom, CodiHorari, CodiBarres, Departament, Actiu, Substitut) " \
             "VALUES ('" + Dni + "', '" + Nom + "', '" + Cognom + "', " + CodiHorari + ", " \
             + CodiBarres + ", '" + Departament + "', 1, 'no');"

    with ct.cursor() as cursor:
        cursor.execute(insert)
        ct.commit()

ct.close()