import pandas as pd
import random
import re
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler
from datetime import datetime
from barcode import EAN13
from barcode.writer import ImageWriter

from dades import *
from utils import *
from informes import *

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


# ---------- INICI ----------


def start(update, context):
    text = "Hola %s!\nBenvingut al sistema de control horari de l'Institut " \
           "de Corbera de Llobregat.\n"%(update.message.chat.first_name)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    ajuda(update, context)
    autor(update, context)
    print(update.message.chat.username)


def ajuda(update, context):
    text = "Per registrar l'entrada o sortida al centre utilitza el lector de codi de barres o introdueix el teu DNI\n"
    text += "Per obtenir el llistat de professors a substituir escriu /guardia\n"
    text += "Per a altres opcions escriu /menu"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def autor(update, context):
    text = "Aquest bot ha sigut creat per Víctor Boix (@vboix2)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('ajuda', ajuda))
dispatcher.add_handler(MessageHandler(Filters.regex('[Aa]juda'), ajuda))
dispatcher.add_handler(CommandHandler('help', ajuda))
dispatcher.add_handler(CommandHandler('autor', autor))


# ---------- MENU -----------


def menu(update, context):
    text = "/professors - llistat de professors\n"
    text += "/guardia - professors a substituir\n"
    text += "/substitut - afegir o finalitzar una substitució\n"
    text += "/informe - informes d'assistència"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def professors(update, context):
    text = "/tots - llistat de tots els professors\n"
    text += "/presents - professors al centre\n"
    text += "/absents - professors fora del centre"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def substitut(update, context):
    text = "/afegir - afegir substitut\n"
    text += "/finalitzar - finalitzar substitució\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def informe(update, context):
    text = "/setmana - informe setmanal\n"
    text += "/mes - informe mensual"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


dispatcher.add_handler(CommandHandler('menu', menu))
dispatcher.add_handler(MessageHandler(Filters.regex('[Mm]en[uú]'), menu))
dispatcher.add_handler(CommandHandler('professors', professors))
dispatcher.add_handler(CommandHandler('substitut', substitut))
dispatcher.add_handler(CommandHandler('informe', informe))


# ---------- PROFESSORS ----------


def tots(update, context):
    profes = df_profes()
    text = ""
    for i in profes.index:
        text += profes.loc[i,'Nom'] + " " + profes.loc[i,'Cognom'] + " (" + str(profes.loc[i,'CodiHorari']) + ")\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def presents(update, context):
    dni = llista_dni_presents()
    text = "No hi ha ningú"
    if len(dni) > 0 :
        presents = pd.DataFrame({'Dni':dni})
        profes = df_profes()
        profes_presents = presents.merge(profes, on='Dni', how='left')
        text = "Professors al centre:\n\n"
        for i in profes_presents.index:
            text += profes_presents.loc[i, 'Nom'] + " " + profes_presents.loc[i, 'Cognom'] + "\n"

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def absents(update, context):
    absents = pd.DataFrame({'Dni':llista_dni_absents()})
    text = "No falta ningú"
    if len(absents)>0:
        profes = df_profes()
        profes_absents = absents.merge(profes, on='Dni', how='left')
        text = "Professors fora del centre:\n\n"
        for i in profes_absents.index:
            text += profes_absents.loc[i, 'Nom'] + " " + profes_absents.loc[i, 'Cognom'] + "\n"

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


dispatcher.add_handler(CommandHandler('tots', tots))
dispatcher.add_handler(CommandHandler('presents', presents))
dispatcher.add_handler(CommandHandler('absents', absents))


# ---------- GUÀRDIA ----------


def llista_guardia(hora, dia):
    # Dades professors absents
    absents = pd.DataFrame({'Dni': llista_dni_absents()})
    profes = df_profes()
    profes_absents = absents.merge(profes, on='Dni', how='left')

    # Classes hora actual
    query = "SELECT Assignatura, CodiProfessor, Aula, Grup FROM Horari WHERE Dia=" \
            + str(dia) + " AND Hora=" + str(hora) + ";"
    ct = connexio()
    with ct.cursor() as cursor:
        cursor.execute(query)
        classes = pd.DataFrame(cursor.fetchall())
    ct.close()
    classes.columns = ['Assignatura', 'CodiHorari', 'Aula', 'Grup']

    # Classes a substituir
    guardia = profes_absents.merge(classes, on="CodiHorari", how='inner')

    text = "Tot correcte!"
    if len(guardia) > 0 :
        text = "Professors a substituir:\n\n"
        for i in guardia.index:
            text += guardia.loc[i, 'Nom'] + " " + guardia.loc[i, 'Cognom'] + ": " \
                    + guardia.loc[i, 'Assignatura'] + " " + guardia.loc[i, 'Aula'] \
                    + " " + guardia.loc[i, 'Grup'] + "\n"

    return text


def guardia_hora(hora):
    dia_lectiu = dia_lectiu_actual()
    text = "No hi ha classes en aquest moment"
    if dia_lectiu != 0 and hora != 0:
        text = llista_guardia(hora, dia_lectiu)
    return text


def guardia(update, context):
    hora_lectiva = hora_lectiva_actual()
    text = guardia_hora(hora_lectiva)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


dispatcher.add_handler(CommandHandler('guardia', guardia))
dispatcher.add_handler(MessageHandler(Filters.regex('[Gg]u[aà]rdia'), guardia))


# ---------- AFEGIR SUBSTITUT ----------


SUBSTITUT = ['Nom', 'Cognom', 'Dni', 'Horari']


def afegir_substitut(update, context, Nom, Cognom, Dni, CodiHorari):
    # Codi barres
    nif = int(re.findall('\d+', Dni)[0])
    random.seed(nif)
    CodiBarres = str(random.randint(100000000000, 999999999999))
    my_code = EAN13(CodiBarres, writer=ImageWriter())
    my_code.save(Nom+Cognom)
    pic = Nom + Cognom + ".png"
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(pic, 'rb'))

    # Canviar estat titular
    ct = connexio()
    update = "UPDATE Professor SET Actiu = 0 WHERE CodiHorari = " + CodiHorari + ";"
    with ct.cursor() as cursor:
        cursor.execute(update)
        ct.commit()

    # Afegir substitut BD
    insert = "INSERT INTO Professor (Dni, Nom, Cognom, CodiHorari, CodiBarres, Actiu) " \
             "VALUES ('" + Dni + "', '" + Nom + "', '" + Cognom + "', " + CodiHorari + ", " \
             + CodiBarres + ", 1);"
    with ct.cursor() as cursor:
        cursor.execute(insert)
        ct.commit()
    ct.close()

    return Nom + " " + Cognom + " afegit correctament"


def afegir(update, context):

    autoritzat = update.message.chat.username in GESTIO
    if not autoritzat:
        update.message.reply_text("No estàs autoritzat a realitzar aquesta acció")
        return ConversationHandler.END
    else:
        update.message.reply_text("Nom del substitut?\n/cancel per cancel·lar l'operació")
        return NOM


def nom(update, context):
    SUBSTITUT[0] = update.message.text
    update.message.reply_text("Cognom del substitut?")
    return COGNOM


def cognom(update, context):
    SUBSTITUT[1] = update.message.text
    update.message.reply_text("DNI del substitut?")
    return DNI


def dni(update, context):
    SUBSTITUT[2] = update.message.text
    tots(update, context)
    update.message.reply_text("Codi de l'horari del substitut?")
    return HORARI


def horari(update, context):
    SUBSTITUT[3] = update.message.text
    text = afegir_substitut(update, context, SUBSTITUT[0], SUBSTITUT[1], SUBSTITUT[2], SUBSTITUT[3])
    update.message.reply_text(text)
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text("Operació cancel·lada")
    return ConversationHandler.END


NOM, COGNOM, DNI, HORARI = range(4)

dispatcher.add_handler(ConversationHandler(entry_points=[CommandHandler('afegir', afegir)],
                                           states={
                                                NOM: [MessageHandler(Filters.regex("[A-z]*"), nom)],
                                                COGNOM: [MessageHandler(Filters.regex("[A-z]*"), cognom)],
                                                DNI: [MessageHandler(Filters.regex("[A-z]?[0-9]{8}[A-z]"), dni)],
                                                HORARI: [MessageHandler(Filters.regex("[0-9]+"), horari)],
                                           },
                                           fallbacks=[CommandHandler('cancel', cancel)]
                                           ))


# ---------- FINALITZAR SUBSTITUCIÓ -------------


FINALITZAR = ['DNI','Horari']


def finalitzar_substitucio(update, context, Dni, CodiHorari):

    # Eliminar substitut BD
    ct = connexio()
    delete = "DELETE FROM Professor WHERE Actiu = 1 AND CodiHorari = " + CodiHorari + ";"
    with ct.cursor() as cursor:
        cursor.execute(delete)
        ct.commit()

    # Canviar estat titular
    update = "UPDATE Professor SET Actiu = 1 WHERE Dni = '" + Dni + "';"
    with ct.cursor() as cursor:
        cursor.execute(update)
        ct.commit()
    ct.close()

    return "Substitució finalitzada correctament"


def finalitzar(update, context):

    autoritzat = update.message.chat.username in GESTIO

    if not autoritzat:
        update.message.reply_text("No estàs autoritzat a realitzar aquesta acció")
        return ConversationHandler.END
    else:
        update.message.reply_text("DNI del professor que es reincorpora?\n/cancel per cancel·lar l'operació")
        return F_DNI


def finalitzar_dni(update, context):
    FINALITZAR[0] = update.message.text
    tots(update, context)
    update.message.reply_text("Codi de l'horari del substitut?")
    return F_HORARI


def finalitzar_horari(update, context):
    FINALITZAR[1] = update.message.text
    text = finalitzar_substitucio(update, context, FINALITZAR[0], FINALITZAR[1])
    update.message.reply_text(text)
    ConversationHandler.END


F_DNI, F_HORARI = range(2)

dispatcher.add_handler(ConversationHandler(entry_points=[CommandHandler('finalitzar', finalitzar)],
                                           states={
                                                F_DNI: [MessageHandler(Filters.regex("[A-z]?[0-9]{8}[A-z]"), finalitzar_dni)],
                                                F_HORARI: [MessageHandler(Filters.regex("[0-9]+"), finalitzar_horari)],
                                           },
                                           fallbacks=[CommandHandler('cancel', cancel)]
                                           ))


# ---------- INFORMES ----------


def informe_dates(update, context):
    context.bot.send_document(chat_id=update.effective_chat.id, document=open('horari.csv', 'rb'))


def setmana(update, context):
    if len(context.args) == 0:
        setmana = datetime.now().isocalendar()[1]
        text = "Informe realitzat"
    elif context.args[0]!=int:
        text = "Valor incorrecte"
    else:
        text = "Informe realitzat"

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def mes(update, context):
    if len(context.args) == 0:
        mes = datetime.now().month
        text = "Informe realitzat"
    elif context.args[0] != int:
        text = "Valor incorrecte"
    else:
        text = "Informe realitzat"

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


dispatcher.add_handler(CommandHandler('informe_dates', informe_dates))
dispatcher.add_handler(CommandHandler('mes', mes))


# ---------- REGISTRE ----------


def registreDNI(update, context):

    # Cercar dades professor
    ct = connexio()
    Dni = update.message.text
    Dni = Dni.upper()
    query = ("SELECT Nom,CodiHorari FROM Professor WHERE Dni = '" + Dni + "';")
    with ct.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()

    # Usuaris autoritzats
    autoritzat = update.message.chat.username in REGISTRE

    if not autoritzat:
        text = "No estàs autoritzat a realitzar aquesta acció"
    elif len(results) == 0:
        text = "DNI incorrecte"
    else:
        for row in results:
            Nom = row[0]
            CodiHorari = str(row[1])

        # Registrar entrada/sortida
        current_time = datetime.now().strftime("%H:%M:%S")
        current_day = datetime.today().strftime("%Y-%m-%d")

        query = ("SELECT idRegistre FROM Registre WHERE Data='" + current_day + "' AND Dni='" + Dni + "' AND HoraSortida IS NULL;")
        with ct.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()

        if len(results)==0:
            insert = "INSERT INTO Registre (Dni, CodiHorari, Data, HoraEntrada)" \
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
        text = missatge_entrada(Nom, current_time) if es_entrada else missatge_sortida(Nom, current_time)

    ct.close()
    context.bot.send_message(chat_id=update.message.chat_id, text=text)


def registreCB(update, context):

    # Cercar dades professor
    ct = connexio()
    codi = update.message.text
    query = ("SELECT Nom,Dni,CodiHorari FROM Professor WHERE CodiBarres = '" + codi[:12] + "';")
    with ct.cursor() as cursor:
        cursor.execute(query,(codi))
        results = cursor.fetchall()

    # Usuaris autoritzats
    autoritzat = update.message.chat.username in REGISTRE

    if not autoritzat:
        text = "No estàs autoritzat a realitzar aquesta acció"
    elif len(results)==0:
        text = "Aquest codi de barres no està associat a cap professor"
    else:
        # Codi de barres correcte
        for row in results:
            Nom = row[0]
            Dni = row[1]
            CodiHorari = str(row[2])

        # Obtenir data i hora
        current_time = datetime.now().strftime("%H:%M:%S")
        current_day = datetime.today().strftime("%Y-%m-%d")

        # Registrar entrada/sortida
        query = ("SELECT idRegistre FROM Registre WHERE Data='" + current_day + "' AND Dni='" + Dni + "' AND HoraSortida IS NULL;")

        with ct.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
        for row in results:
            idRegistre = str(row[0])

        if len(results) == 0:
            insert = "INSERT INTO Registre (Dni, CodiHorari, Data, HoraEntrada)" \
                     " VALUES ('" + Dni + "', '" + CodiHorari + "', '" + current_day + "', '" + current_time + "');"
            es_entrada = True
        else:
            insert = "UPDATE Registre SET HoraSortida = '" + current_time + "' WHERE idRegistre = " + idRegistre + ";"
            es_entrada = False

        with ct.cursor() as cursor:
            cursor.execute(insert)
            ct.commit()

        text = missatge_entrada(Nom, current_time) if es_entrada else missatge_sortida(Nom, current_time)

    ct.close()
    context.bot.send_message(chat_id=update.message.chat_id, text=text)


dispatcher.add_handler(MessageHandler(Filters.regex('[0-9]{8}[A-z]'), registreDNI))
dispatcher.add_handler(MessageHandler(Filters.regex('[0-9]{13}'), registreCB))


# ---------- ALTRES ----------


def eco(update, context):
    text = update.message.text
    context.bot.send_message(chat_id=update.message.chat_id, text=text)


def resposta(update, context):
    missatges = ["Què?", "No t'entenc", "Missatge incorrecte", "Què vols dir?", "Repeteix-ho", "Torna-ho a dir"]
    text = random.choice(missatges)
    context.bot.send_message(chat_id=update.message.chat_id, text=text)


dispatcher.add_handler(MessageHandler(Filters.regex('[Hh]ola[!]*|[Aa]d[ée]u[!]*'), eco))
dispatcher.add_handler(MessageHandler(Filters.regex('.*'), resposta))

updater.start_polling()