import pandas as pd
from datetime import datetime

from utils import connexio

HORA_INICI = {1:'8:10:00', 2:'9:05:00', 3:'10:00:00', 4:'10:55:00', 5:'11:25:00', 6:'11:55:00', 7:'12:50:00', 8:'13:45:00'}
HORA_FINAL = {1:'9:05:00', 2:'10:00:00', 3:'10:55:00', 4:'11:25:00', 5:'11:55:00', 6:'12:50:00', 7:'13:45:00', 8:'14:40:00'}


def df_horari():
    # Obtenció horari BD
    ct = connexio()
    query = ("SELECT Dia, Hora, CodiProfessor FROM Horari;")
    with ct.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
    horari = pd.DataFrame(results, columns=['Dia','Hora','CodiHorari'])
    ct.close()

    # Eliminar hores tarda
    horari = horari.loc[horari['Hora'] < 9, :]

    # Càlcul hores d'entrada i sortida
    horari = horari.groupby(['Dia','CodiHorari'], as_index=False).agg({'Hora':['min','max']})
    horari.columns = list(map(''.join, horari.columns.values))

    # Tipus de dades timedelta
    horari['HoraEntrada'] = "0 days " + horari['Horamin'].map(HORA_INICI)
    horari['HoraSortida'] = "0 days " + horari['Horamax'].map(HORA_FINAL)
    horari['HoraEntrada'] = horari['HoraEntrada'].apply(lambda x: pd.to_timedelta(x))
    horari['HoraSortida'] = horari['HoraSortida'].apply(lambda x: pd.to_timedelta(x))

    # Selecció atributs
    horari = horari[['Dia','CodiHorari','HoraEntrada','HoraSortida']]

    return horari


def df_registres(inici, final):
    ct = connexio()
    query = ("SELECT Dni,CodiHorari,Data,HoraEntrada,HoraSortida FROM Registre WHERE Data >= '" + inici + "' AND Data <= '" + final + "';")
    with ct.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
    ct.close()

    registres = pd.DataFrame(results, columns=['Dni','CodiHorari','Data','RegistreEntrada','RegistreSortida'])
    registres['Dia'] = registres['Data'].apply(lambda d: d.weekday()+1)
    return registres


def df_professors():
    """DataFrame amb les dades dels professors actius"""
    ct = connexio()
    query = ("SELECT Dni,Nom,Cognom,CodiHorari FROM Professor;")
    with ct.cursor() as cursor:
        cursor.execute(query)
        profes = pd.DataFrame(cursor.fetchall(), columns=['Dni', 'Nom', 'Cognom', 'CodiHorari'])
    ct.close()

    profes['Nom'] = profes['Nom'] + " " + profes['Cognom']
    profes = profes[['Dni','Nom']]

    return profes


def informe_dates(inici, final):
    horari = df_horari()
    registres = df_registres(inici, final)
    profes = df_professors()

    informe = registres.merge(horari, on=["CodiHorari",'Dia'], how='left')
    informe = informe.merge(profes, on=['Dni'], how='left')

    informe['HoresTreballades'] = informe['RegistreSortida'] - informe['RegistreEntrada']
    informe['HoresFeina'] = informe['HoraSortida'] - informe['HoraEntrada']
    #informe['HoresAbsencia'] = informe['RegistreEntrada'] - informe['HoraEntrada']

    informe = informe[['Dni','Nom','Data','HoraEntrada','HoraSortida','HoresFeina','RegistreEntrada','RegistreSortida','HoresTreballades']]

    informe['HoraEntrada'] = informe['HoraEntrada'].apply(lambda s: ("{:02}:{:02}".format(s.seconds // 3600, s.seconds // 60 % 60)))
    informe['HoraSortida'] = informe['HoraSortida'].apply(lambda s: ("{:02}:{:02}".format(s.seconds // 3600, s.seconds // 60 % 60)))
    informe['RegistreEntrada'] = informe['RegistreEntrada'].apply(lambda s: ("{:02}:{:02}".format(s.seconds // 3600, s.seconds // 60 % 60)))
    informe['RegistreSortida'] = informe['RegistreSortida'].apply(lambda s: ("{:02}:{:02}".format(s.seconds // 3600, s.seconds // 60 % 60)))
    informe['HoresFeina'] = informe['HoresFeina'].apply(lambda s: ("{:02}:{:02}".format(s.seconds // 3600, s.seconds // 60 % 60)))
    informe['HoresTreballades'] = informe['HoresTreballades'].apply(lambda s: ("{:02}:{:02}".format(s.seconds // 3600, s.seconds // 60 % 60)))

    filename = "informe_" + inici + "_" + final +".csv"
    informe.to_csv(filename, index=False)

    return filename



