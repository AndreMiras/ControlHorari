"""
Genera el fitxer /files/professors_bd.csv necessari per a la importació a la BD
i el codi de barres dels professors a la carpeta /codis

Requereix el fitxer /files/professors_cb.csv amb les columnes:
DNI,Nom,Cognom,Departament,CodiHorari
"""
import pandas as pd
import random
import os
import re
from barcode import EAN13
from barcode.writer import ImageWriter

dir_path = os.path.dirname(os.path.realpath(__file__))

# Importació dades
profes = pd.read_csv(dir_path + '/../files/professors_cb.csv', sep=",")


# Generar codi de barres
def generaCodi(dni):
    nif = int(re.findall('\d+', dni)[0])
    random.seed(nif)
    return random.randint(100000000000, 999999999999)


profes['CodiBarres'] = profes['Dni'].apply(generaCodi)


# Imprimir codi de barres
for i in profes.index:
    codi = str(profes.loc[i, 'CodiBarres'])
    nom = profes.loc[i, 'Nom'] + profes.loc[i, 'Cognom']
    nom = nom.replace(" ","")
    my_code = EAN13(codi, writer=ImageWriter())
    my_code.save(dir_path + "/../codis/" + nom)

# Exportar dades
profes.to_csv(dir_path + '/../files/professors_bd.csv', index=False)