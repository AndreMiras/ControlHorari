import pandas as pd
import professors
from dades import connexio
from utils import *


def df_classes(dia, hora):
    # DataFrame amb les classes a l'hora indicada
    # Assignatura, CodiHorari, Aula i Grup

    query = "SELECT Assignatura, CodiHorari, Aula, Grup FROM Horari WHERE Dia=" \
            + str(dia) + " AND Hora=" + str(hora) + ";"
    ct = connexio()
    with ct.cursor() as cursor:
        cursor.execute(query)
        classes = pd.DataFrame(cursor.fetchall())
    ct.close()
    classes.columns = ['Assignatura', 'CodiHorari', 'Aula', 'Grup']

    return classes


def llista(dia, hora):

    if (dia in range(1,6)) and (hora in range(1,9)):
        profes_absents = professors.df_profes_absents()
        classes = df_classes(dia, hora)
        guardia = profes_absents.merge(classes, on="CodiHorari", how='inner')

        if len(guardia) > 0:
            text = "Professors a substituir a les " + HORA[hora - 1] + ":\n\n"
            for i in guardia.index:
                text += guardia.loc[i, 'Nom'] + " " + guardia.loc[i, 'Cognom'] + ": " \
                        + guardia.loc[i, 'Assignatura'] + " " + guardia.loc[i, 'Aula'] \
                        + " " + guardia.loc[i, 'Grup'] + "\n"
        else:
            text = "Tot correcte!"

    else:
        text = "No hi ha classes en aquesta hora"

    return text

