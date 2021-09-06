from dades import connexio
import os
import pandas as pd
import re
import random
from barcode import EAN13
from barcode.writer import ImageWriter

dir_path = os.path.dirname(os.path.realpath(__file__))

# ----------- 3 Preparació dades professors

# Importació dades
profes = pd.read_csv(dir_path + '/../files/professors.csv', sep=",")

# Neteja de dades
profes = profes.loc[profes.Dni.isna() == False, :]
profes = profes.loc[profes.CodiHorari.isna() == False, :]
profes.fillna('', inplace=True)
profes['CodiHorari'] = profes['CodiHorari'].astype(int)
profes['Dni'] = profes['Dni'].apply(lambda s: re.sub('(^0)', '', s))

# ----------- 4 Preparació dades horaris

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

# ---------- 5 Creació codis de barres

def generaCodi(dni):
    nif = int(re.findall('\d+', dni)[0])
    random.seed(nif)
    return random.randint(100000000000, 999999999999)


# Generar codi de barres
profes['CodiBarres'] = profes['Dni'].apply(generaCodi)

# Imprimir codi de barres
for i in profes.index:
    codi = str(profes.loc[i, 'CodiBarres'])
    nom = profes.loc[i, 'Nom'] + profes.loc[i, 'Cognom']
    nom = nom.replace(" ","")
    my_code = EAN13(codi, writer=ImageWriter())
    my_code.save(dir_path + "/../codis/" + nom)

# ----------- 6 Inserció a la BD

ct = connexio()

# Eliminació taula Professor
with ct.cursor() as cursor:
    cursor.execute("DELETE FROM Professor;")
    ct.commit()

# Eliminació taula Horari
with ct.cursor() as cursor:
    cursor.execute("DELETE FROM Horari;")
    ct.commit()

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


for i in horari.index:
    Dia = str(horari.loc[i,'Dia'])
    Hora = str(horari.loc[i,'Hora'])
    Assignatura = horari.loc[i, 'Assignatura']
    CodiHorari = str(horari.loc[i,'CodiHorari'])
    Aula = horari.loc[i,'Aula']
    Grup = horari.loc[i,'Grup']

    insert = "INSERT INTO Horari (Dia, Hora, Assignatura, CodiHorari, Aula, Grup) " \
             "VALUES (" + Dia + ", " + Hora + ", '" + Assignatura + "', " \
             + CodiHorari + ", '" + Aula + "', '" + Grup + "');"

    with ct.cursor() as cursor:
        cursor.execute(insert)
        ct.commit()

ct.close()
