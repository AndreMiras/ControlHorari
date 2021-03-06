import pandas as pd
from datetime import datetime

from dades import connexio
from dades import HORA_INICI, HORA_FINAL, FESTIUS
from professors import df_professors


def df_dates(inici, final):
    """
    Genera un DataFrame amb els dies laborables entre la data inicial i final
    Columnes: Data, DiaSetmana
    """
    v_inici = [int(i) for i in inici.split("-")]
    v_final = [int(i) for i in final.split("-")]

    data_inici = datetime(v_inici[0], v_inici[1], v_inici[2])
    data_final = datetime(v_final[0], v_final[1], v_final[2])

    dies = pd.date_range(data_inici, data_final).tolist()
    dates = pd.DataFrame({'Data': dies})

    # Calcular dia de la setmana
    dates['DiaSetmana'] = dates['Data'].apply(lambda d: d.weekday() + 1)

    # Eliminar caps de setmana
    dates = dates.loc[dates['DiaSetmana'] < 6, :]
    # Eliminar festius
    for f in FESTIUS:
        dates.drop(dates.index[dates['Data'] == f], inplace=True)

    dates['Data'] = dates['Data'].apply(lambda d: d.strftime("%Y-%m-%d"))
    return dates


def df_horari():
    """
    Genera un DataFrame amb l'hora d'entrada i sortida de cada professor
    Columnes: DiaSetmana, CodiHorari, HoraEntrada, HoraSortida
    """
    # Obtenció horari BD
    ct = connexio()
    query = ("SELECT Dia, Hora, CodiHorari FROM Horari;")
    with ct.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
    horari = pd.DataFrame(results, columns=['DiaSetmana','Hora','CodiHorari'])
    ct.close()

    # Eliminar hores tarda
    horari = horari.loc[horari['Hora'] < 9, :]

    # Càlcul hores d'entrada i sortida
    horari = horari.groupby(['DiaSetmana','CodiHorari'], as_index=False).agg({'Hora':['min','max']})
    horari.columns = list(map(''.join, horari.columns.values))

    # Tipus de dades timedelta
    horari['HoraEntrada'] = "0 days " + horari['Horamin'].map(HORA_INICI)
    horari['HoraSortida'] = "0 days " + horari['Horamax'].map(HORA_FINAL)
    horari['HoraEntrada'] = horari['HoraEntrada'].apply(lambda x: pd.to_timedelta(x))
    horari['HoraSortida'] = horari['HoraSortida'].apply(lambda x: pd.to_timedelta(x))

    # Selecció atributs
    horari = horari[['DiaSetmana','CodiHorari','HoraEntrada','HoraSortida']]

    return horari


def df_registres(inici, final):
    """
    Genera una DataFrame amb els registres d'entrada i sortida de cada professor per dia
    Columnes: Dni, CodiHorari, Data, RegistreEntrada, RegistreSortida
    """
    ct = connexio()
    query = ("SELECT Dni,CodiHorari,Data,HoraEntrada,HoraSortida FROM Registre WHERE Data >= '" + inici + "' AND Data <= '" + final + "';")
    with ct.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
    ct.close()

    registres = pd.DataFrame(results, columns=['Dni','CodiHorari','Data','RegistreEntrada','RegistreSortida'])
    registres['Data'] = registres['Data'].apply(lambda d: d.strftime("%Y-%m-%d"))

    # Si un professor fitxa més d'una vegada per dia s'agafa l'entrada més antiga i la sortida més recent
    registres = registres.groupby(['Dni','CodiHorari','Data'], as_index=False).agg({'RegistreEntrada':'min', 'RegistreSortida':'max'})

    return registres


def format_hora(hms):
    string_hora = "{:02}:{:02}".format(hms.seconds // 3600, hms.seconds // 60 % 60)
    if string_hora=="nan:nan":
        string_hora="No"
    return string_hora


def calcul_temps_absencia(row):
    if pd.isna(row['RegistreEntrada']):
        temps_absencia = row['HoraSortida'] - row['HoraEntrada']
    else:
        entrada = max(row['HoraEntrada'], row['RegistreEntrada'])
        sortida = min(row['HoraSortida'], row['RegistreSortida'])
        temps_feina = row['HoraSortida'] - row['HoraEntrada']
        temps_treballat = sortida - entrada
        temps_absencia = temps_feina - temps_treballat

    return temps_absencia


def absencies(inici, final):
    """
    Informe del temps d'absència d'un professor segons el seu horari
    Data, Nom, Temps absència, Hora entrada, Hora sortida
    """

    dates = df_dates(inici, final)
    horari = df_horari()
    informe = dates.merge(horari, on=['DiaSetmana'], how='left')

    registres = df_registres(inici, final)
    informe = informe.merge(registres, on=["CodiHorari", 'Data'], how='left')

    profes = df_professors()
    informe = informe.merge(profes[['Nom', 'CodiHorari']], on=['CodiHorari'], how='left')

    informe['TempsAbsencia'] = informe.apply(calcul_temps_absencia, axis=1)
    informe = informe.loc[informe['TempsAbsencia'] > pd.Timedelta("0 days 00:00:59"),:]
    informe['TempsAbsencia'] = informe['TempsAbsencia'].apply(format_hora)
    informe['RegistreEntrada'] = informe['RegistreEntrada'].apply(format_hora)
    informe['RegistreSortida'] = informe['RegistreSortida'].apply(format_hora)
    informe = informe[['Data', 'Nom', 'TempsAbsencia', 'RegistreEntrada', 'RegistreSortida']]

    # Generar fitxer
    filename = "./informes/informe_absencies_" + inici + "_" + final + ".csv"
    informe.to_csv(filename, index=False)

    return filename


def assistencia(inici, final):
    """
    Informe d'assistència del professorat:
    Data, Nom, RegistreEntrada, RegistreSortida, TempsTreballat
    """

    dates = df_dates(inici, final)
    registres = df_registres(inici, final)
    informe = dates.merge(registres, on=['Data'], how='inner')

    informe['TempsTreballat'] = informe['RegistreSortida'] - informe['RegistreEntrada']

    informe['RegistreEntrada'] = informe['RegistreEntrada'].apply(format_hora)
    informe['RegistreSortida'] = informe['RegistreSortida'].apply(format_hora)
    informe['TempsTreballat'] = informe['TempsTreballat'].apply(format_hora)

    # Dades professors
    profes = df_professors()
    informe = informe.merge(profes[['Nom','Dni']], on=['Dni'], how='left')

    # Format informe
    informe = informe[['Data','Nom','RegistreEntrada','RegistreSortida','TempsTreballat']]

    # Generar fitxer
    filename = "./informes/informe_assistencia_" + inici + "_" + final +".csv"
    informe.to_csv(filename, index=False)

    return filename



