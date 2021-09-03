"""
Actualitza els horaris de la base de dades
Requereix el fitxer amb els horaris de GPUntis GPU001.TXT
"""

import pandas as pd
import os
from dades import connexio

dir_path = os.path.dirname(os.path.realpath(__file__))

ct = connexio()

# Eliminació taula
with ct.cursor() as cursor:
    cursor.execute("DELETE FROM Horari;")
    ct.commit()

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

# Importació a la BD
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


