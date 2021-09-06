"""
Importació de dades a la base de dades
"""

import pandas as pd
import os
from dades import connexio

dir_path = os.path.dirname(os.path.realpath(__file__))
ct = connexio()


# ----------- Buidar taules --------------

# Eliminació taula Professor
with ct.cursor() as cursor:
    cursor.execute("DELETE FROM Professor;")
    ct.commit()

# Eliminació taula Horari
with ct.cursor() as cursor:
    cursor.execute("DELETE FROM Horari;")
    ct.commit()


# ----------- Taula Professor -------------

profes = pd.read_csv(dir_path + '/../files/professors_bd.csv', sep=",")
profes.fillna('', inplace=True)

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


# ---------- Taula Horari -----------

horari = pd.read_csv(dir_path + '/../files/horari_bd.csv', sep=",", dtype=str)
horari = horari.fillna('')

for i in horari.index:
    Dia = horari.loc[i,'Dia']
    Hora = horari.loc[i,'Hora']
    Assignatura = horari.loc[i, 'Assignatura']
    CodiHorari = horari.loc[i,'CodiHorari']
    Aula = horari.loc[i,'Aula']
    Grup = horari.loc[i,'Grup']

    insert = "INSERT INTO Horari (Dia, Hora, Assignatura, CodiHorari, Aula, Grup) " \
             "VALUES (" + Dia + ", " + Hora + ", '" + Assignatura + "', " \
             + CodiHorari + ", '" + Aula + "', '" + Grup + "');"

    with ct.cursor() as cursor:
        cursor.execute(insert)
        ct.commit()

ct.close()

