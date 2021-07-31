import random
import re
from barcode import EAN13
from barcode.writer import ImageWriter

from dades import connexio
from professors import dni_per_horari, dni_titular_per_substitut


def generar_codi_barres(dni):
    # Generem codi de 12 xifres
    nif = int(re.findall('\d+', dni)[0])
    random.seed(nif)
    codiBarres = str(random.randint(100000000000, 999999999999))

    # Generem la imatge del codi de barres
    my_code = EAN13(codiBarres, writer=ImageWriter())
    my_code.save("./codis/" + dni)

    return codiBarres


def BD_afegir_substitut(nom, cognom, dni, horari, codiBarres, dni_titular):
    ct = connexio()

    # Canviar estat titular
    update = "UPDATE Professor SET Actiu = 0 WHERE Dni = '" + dni_titular + "';"
    with ct.cursor() as cursor:
        cursor.execute(update)
        ct.commit()

    # Afegir substitut
    insert = "INSERT INTO Professor (Dni, Nom, Cognom, CodiHorari, CodiBarres, Actiu, Substitut) " \
             "VALUES ('" + dni + "', '" + nom + "', '" + cognom + "', " + str(horari) + ", " \
             + codiBarres + ", 1, '" + dni_titular + "');"
    with ct.cursor() as cursor:
        cursor.execute(insert)
        ct.commit()

    ct.close()


def BD_finalitzar_substitucio(dni_titular, horari):
    ct = connexio()

    # Eliminar substitut
    delete = "DELETE FROM Professor WHERE Actiu = 1 AND CodiHorari = " + str(horari) + ";"
    with ct.cursor() as cursor:
        cursor.execute(delete)
        ct.commit()

    # Canviar estat titular
    update = "UPDATE Professor SET Actiu = 1 WHERE Dni = '" + dni_titular + "';"
    with ct.cursor() as cursor:
        cursor.execute(update)
        ct.commit()

    ct.close()


def afegir(nom, cognom, dni, horari):

    dni_titular = dni_per_horari(horari)

    if dni_titular !='no':
        codiBarres = generar_codi_barres(dni)
        BD_afegir_substitut(nom, cognom, dni, horari, codiBarres, dni_titular)
        text = nom + " " + cognom + " afegit correctament"
    else:
        text = "Codi del professor incorrecte"

    return text


def finalitzar(horari):

    dni_titular = dni_titular_per_substitut(horari)

    if dni_titular != 'no':
        BD_finalitzar_substitucio(dni_titular, horari)
        text = "Substitució finalitzada correctament"
    else:
        text = "Codi del professor incorrecte"

    return text