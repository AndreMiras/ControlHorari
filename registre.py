import random
import datetime
from utils import connexio


def cercaCB(codi):
    # Cercar dades professor per codi de barres
    ct = connexio()
    query = ("SELECT Nom,CodiHorari,DNI FROM Professor WHERE CodiBarres = '" + codi[:12] + "';")
    with ct.cursor() as cursor:
        cursor.execute(query)
        dades_prof = cursor.fetchall()
    ct.close()
    return dades_prof


def cercaDNI(dni):
    # Cercar dades professor per codi DNI
    ct = connexio()
    query = ("SELECT Nom,CodiHorari,DNI FROM Professor WHERE SUBSTRING(DNI, LENGTH(DNI)-3, 4) = '" + dni + "';")
    with ct.cursor() as cursor:
        cursor.execute(query)
        dades_prof = cursor.fetchall()
    ct.close()
    return dades_prof


def missatge_entrada(nom, hora):
    missatges = ["Bon dia", "Hola", "Salutacions", "Benvingut/da"]
    text = random.choice(missatges)
    text += " " + nom + "!\n"
    text += "Entrada registrada a les " + hora + " "
    text +=  u"\U000027A1"
    return text


def missatge_sortida(nom, hora):
    missatges = ["Adéu", "Que vagi bé", "Fins aviat", "Fins la propera"]
    text = random.choice(missatges)
    text += " " + nom + "!\n"
    text += "Sortida registrada a les " + hora + " "
    text += u"\U00002705"
    return text


def registreBD(dades_prof):

    for row in dades_prof:
        Nom = row[0]
        CodiHorari = str(row[1])
        Dni = row[2]

    # Registrar entrada/sortida
    current_time = datetime.now().strftime("%H:%M:%S")
    current_day = datetime.today().strftime("%Y-%m-%d")

    query = ("SELECT idRegistre FROM Registre WHERE Data='" + current_day + "' AND DNI='" + Dni + "' AND HoraSortida IS NULL;")
    ct = connexio()

    with ct.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()

    if len(results) == 0:
        insert = "INSERT INTO Registre (DNI, CodiHorari, Data, HoraEntrada)" \
                 " VALUES ('" + Dni + "', '" + CodiHorari + "', '" + current_day + "', '" + current_time + "');"
        es_entrada = True
    else:
        for row in results:
            idRegistre = str(row[0])
        insert = "UPDATE Registre SET HoraSortida = '" + current_time + "' WHERE idRegistre = " + idRegistre + ";"
        es_entrada = False

    with ct.cursor() as cursor:
        cursor.execute(insert)
        ct.commit()

    ct.close()

    return missatge_entrada(Nom, current_time) if es_entrada else missatge_sortida(Nom, current_time)