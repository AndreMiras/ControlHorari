import pandas as pd
from datetime import datetime
from utils import *
from dades import connexio


def df_profes():
    """DataFrame amb les dades dels professors actius"""
    ct = connexio()
    query = ("SELECT Dni,Nom,Cognom,CodiHorari FROM Professor WHERE Actiu=1 ORDER BY 4;")
    with ct.cursor() as cursor:
        cursor.execute(query)
        profes = pd.DataFrame(cursor.fetchall(), columns=['Dni', 'Nom', 'Cognom', 'CodiHorari'])
    ct.close()
    profes.fillna('?', inplace=True)
    return profes


def df_horari_profe(codi, dia):
    """DataFrame amb l'horari d'un professor per codi i dia"""
    ct = connexio()
    query = ("SELECT Hora,Assignatura,Aula,Grup FROM Horari WHERE CodiHorari=" + str(codi) +" AND Dia=" + str(dia) + " ORDER BY 1;")
    with ct.cursor() as cursor:
        cursor.execute(query)
        horari = pd.DataFrame(cursor.fetchall(), columns=['Hora', 'Assignatura', 'Aula', 'Grup'])
    ct.close()
    horari.fillna('?', inplace=True)
    return horari


def df_profes_guardia(dia, hora):
    """DataFrame amb el nom i el cognom dels professors amb G o Gp al dia i hora indicats"""
    ct = connexio()
    query = ("SELECT CodiHorari FROM Horari WHERE Dia= " + str(dia) + " AND Hora = " + str(hora) + " AND (Assignatura = 'G' OR Assignatura = 'Gp')")
    with ct.cursor() as cursor:
        cursor.execute(query)
        profes_g = pd.DataFrame(cursor.fetchall(), columns=['CodiHorari'])
    ct.close()
    profes = df_profes()
    profes_g = profes_g.merge(profes, how='left', on='CodiHorari')
    profes_g.fillna('?', inplace=True)

    return profes_g[['Nom', 'Cognom']]


def llista_dni_actius():
    """Llista de tot els DNI de professors actius"""
    ct = connexio()
    query = ("SELECT Dni FROM Professor WHERE Actiu=1;")
    with ct.cursor() as cursor:
        cursor.execute(query)
        llista_dni = []
        for row in cursor.fetchall():
            llista_dni.append(row[0])
    ct.close()
    return llista_dni


def llista_dni_presents():
    """Llista de DNIs dels professors presents al centre"""
    llista_presents = []
    current_day = datetime.today().strftime("%Y-%m-%d")

    ct = connexio()
    query = ("SELECT Dni FROM Registre WHERE Data='" + current_day + "' AND HoraSortida IS NULL;")
    with ct.cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            llista_presents.append(row[0])
    ct.close()

    # Eliminem els professors presents però no actius a la BD
    actius = llista_dni_actius()
    llista_presents_actius = [value for value in llista_presents if value in actius]

    return llista_presents_actius


def llista_dni_absents():
    """Llista de DNIs dels professors fora del centre"""
    dni = llista_dni_actius()
    presents = llista_dni_presents()
    for i in presents:
        dni.remove(i)
    return dni


def tots():
    profes = df_profes()
    text = "No hi ha professors"
    if len(profes.index) > 0:
        text = "Llistat de tot el professorat:\n\n"
        for i in profes.index:
            text += profes.loc[i, 'Nom'] + " " + profes.loc[i, 'Cognom'] + " (" + str(
                profes.loc[i, 'CodiHorari']) + ")\n"
    return text


def presents():
    dni = llista_dni_presents()
    text = "No hi ha ningú"
    if len(dni) > 0:
        presents = pd.DataFrame({'Dni': dni})
        profes = df_profes()
        profes_presents = presents.merge(profes, on='Dni', how='left')
        text = "Professors al centre:\n\n"
        for i in profes_presents.index:
            text += profes_presents.loc[i, 'Nom'] + " " + profes_presents.loc[i, 'Cognom'] + "\n"
    return text


def absents():
    absents = pd.DataFrame({'Dni': llista_dni_absents()})
    text = "No falta ningú"
    if len(absents.index) > 0:
        profes = df_profes()
        profes_absents = absents.merge(profes, on='Dni', how='left')
        text = "Professors fora del centre:\n\n"
        for i in profes_absents.index:
            text += profes_absents.loc[i, 'Nom'] + " " + profes_absents.loc[i, 'Cognom'] + "\n"
    return text


def guardia():
    dia = dia_lectiu_actual()
    hora_lectiva = hora_lectiva_actual()

    if (hora_lectiva == 0) or (dia in [6,7]):
        text = "No estem en horari lectiu"
    else:
        profes = df_profes_guardia(dia, hora_lectiva)
        text = "Professors de guàrdia a les " + HORA[hora_lectiva - 1] + ":\n"
        for i in profes.index:
            text += profes.loc[i, "Nom"] + " " + profes.loc[i, "Cognom"] + "\n"
    return text


def horari(codiHorari):
    dia = dia_lectiu_actual()
    if dia in [6,7]:
        text = "No estem en horari lectiu"
    else:
        horari = df_horari_profe(codiHorari, dia)
        if len(horari.index) > 0:
            text = ""
            for i in horari.index:
                text += HORA[horari.loc[i, 'Hora'] - 1] + " " + horari.loc[i, 'Assignatura'] + " " + horari.loc[
                    i, 'Aula'] + " " + horari.loc[i, 'Grup'] + "\n"
        else:
            text = "No hi ha horari per a aquest codi"
    return text

