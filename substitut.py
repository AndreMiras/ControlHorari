import random
import re
from barcode import EAN13
from barcode.writer import ImageWriter

from dades import connexio
from professors import llista_codis_horari


def codi_barres(dni):
    # Generem codi de 12 xifres
    nif = int(re.findall('\d+', dni)[0])
    random.seed(nif)
    codiBarres = str(random.randint(100000000000, 999999999999))

    # Generem la imatge del codi de barres
    my_code = EAN13(codiBarres, writer=ImageWriter())
    my_code.save(dni)

    return codiBarres


def actualitzacio_BD(nom, cognom, dni, codiHorari, codiBarres):
    horari = str(codiHorari)

    # Canviar estat titular
    ct = connexio()
    update = "UPDATE Professor SET Actiu = 0 WHERE CodiHorari = " + horari + ";"
    with ct.cursor() as cursor:
        cursor.execute(update)
        ct.commit()

    # Afegir substitut
    insert = "INSERT INTO Professor (Dni, Nom, Cognom, CodiHorari, CodiBarres, Actiu) " \
             "VALUES ('" + dni + "', '" + nom + "', '" + cognom + "', " + horari + ", " \
             + codiBarres + ", 1);"
    with ct.cursor() as cursor:
        cursor.execute(insert)
        ct.commit()
    ct.close()


def afegir(nom, cognom, dni, codiHorari):
    codis = llista_codis_horari()
    if codiHorari in codis:
        codiBarres = codi_barres(dni)
        actualitzacio_BD(nom, cognom, dni, codiHorari, codiBarres)
        text = nom + " " + cognom + " afegit correctament"
    else:
        text = "Codi del professor incorrecte"

    return text