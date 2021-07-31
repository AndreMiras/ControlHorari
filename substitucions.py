import random
import re
from barcode import EAN13
from barcode.writer import ImageWriter

from dades import connexio
from professors import es_codi_horari_actiu


def generar_codi_barres(dni):
    # Generem codi de 12 xifres
    nif = int(re.findall('\d+', dni)[0])
    random.seed(nif)
    codiBarres = str(random.randint(100000000000, 999999999999))

    # Generem la imatge del codi de barres
    my_code = EAN13(codiBarres, writer=ImageWriter())
    my_code.save(dni)

    return codiBarres


def es_dni_baixa(dni):
    # Comprova que el dni correspon a un professor de baixa
    ct = connexio()
    query = "SELECT * FROM Professor WHERE Dni = '" + dni + "' AND ACTIU=0;"
    with ct.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    ct.close()

    if len(result) == 0:
        return False
    else:
        return True


def BD_afegir_substitut(nom, cognom, dni, codiHorari, codiBarres):
    horari = str(codiHorari)
    ct = connexio()

    # Canviar estat titular
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


def BD_finalitzar_substitucio(dni, codiHorari):
    horari = str(codiHorari)
    ct = connexio()

    # Eliminar substitut
    delete = "DELETE FROM Professor WHERE Actiu = 1 AND CodiHorari = " + horari + ";"
    with ct.cursor() as cursor:
        cursor.execute(delete)
        ct.commit()

    # Canviar estat titular
    update = "UPDATE Professor SET Actiu = 1 WHERE Dni = '" + dni + "';"
    with ct.cursor() as cursor:
        cursor.execute(update)
        ct.commit()

    ct.close()


def afegir(nom, cognom, dni, codiHorari):
    if es_codi_horari_actiu(codiHorari):
        codiBarres = generar_codi_barres(dni)
        BD_afegir_substitut(nom, cognom, dni, codiHorari, codiBarres)
        text = nom + " " + cognom + " afegit correctament"
    else:
        text = "Codi del professor incorrecte"

    return text


def finalitzar(dni, codiHorari):
    # Comprovar dades
    if es_dni_baixa(dni) and es_codi_horari_actiu(codiHorari):
        BD_finalitzar_substitucio(dni, codiHorari)
        text = "Substitució finalitzada correctament"
    else:
        text = "Hi ha un error a les dades"

    return text