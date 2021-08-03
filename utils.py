from datetime import datetime

HORA = ['8:10','9:05','10:00','10:55','11:25','11:55','12:50','13:45','16:00']


def hora_lectiva_actual():
    """Torna un enter amb l'hora lectiva actual segons l'horari del centre"""
    current_time = datetime.now()
    hora = current_time.hour
    minuts= current_time.minute
    hora_lectiva = 0
    if hora == 8 and minuts>10:
        hora_lectiva=1
    elif hora == 9:
        if minuts<5: hora_lectiva=1
        else: hora_lectiva=2
    elif hora==10:
        if minuts<55: hora_lectiva=3
        else: hora_lectiva=4
    elif hora==11:
        if minuts<25: hora_lectiva=4
        elif minuts<55: hora_lectiva=5
        else: hora_lectiva=6
    elif hora==12:
        if minuts<50: hora_lectiva=6
        else: hora_lectiva=7
    elif hora==13:
        if minuts<45: hora_lectiva=7
        else: hora_lectiva=8
    elif hora==14 and minuts<40:
        hora_lectiva=8
    return hora_lectiva


def dia_actual():
    """Torna un enter amb el dia de la setmana"""
    current_time = datetime.now()
    dia = current_time.weekday()
    return dia + 1
