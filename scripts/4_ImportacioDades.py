"""
Importació de dades a la base de dades
"""

import pandas as pd
import mysql.connector
import os
from dades import connexio

dir_path = os.path.dirname(os.path.realpath(__file__))
profes = pd.read_csv(dir_path + '/../files/professors.csv', sep=",")
connection = connexio()

# ----------- Professor -------------

for i in profes.index:
    Dni = profes.loc[i,'Dni']
    Nom = profes.loc[i,'Nom']
    Cognom = profes.loc[i, 'Cognom']
    CodiHorari = str(profes.loc[i,'CodiHorari'])
    CodiBarres = str(profes.loc[i,'CodiBarres'])
    Departament = profes.loc[i,'Departament']

    insert = "INSERT INTO Professor (Dni, Nom, Cognom, CodiHorari, CodiBarres, Departament, Actiu) " \
             "VALUES ('" + Dni + "', '" + Nom + "', '" + Cognom + "', " + CodiHorari + ", " \
             + CodiBarres + ", '" + Departament + "', 1);"

    with connection.cursor() as cursor:
        cursor.execute(insert)
        connection.commit()


# ---------- Horari -----------

# Importació de dades dels horaris
horari = pd.read_csv(dir_path + '/../files/horari.csv', sep=";", dtype=str)

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

    with connection.cursor() as cursor:
        cursor.execute(insert)
        connection.commit()

connection.close()

