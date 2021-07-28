#import pandas as pd
import random
import re
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler
#from datetime import datetime
from barcode import EAN13
from barcode.writer import ImageWriter

from dades import *
from utils import *
from informes import *
import registre

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
dispatcher.add_handler(MessageHandler(Filters.regex('.*[Aa]juda.*'), ajuda))
dispatcher.add_handler(CommandHandler('help', ajuda))
dispatcher.add_handler(CommandHandler('autor', autor))


# ---------- MENU -----------


def menu(update, context):
    text = "/guardia - professors a substituir\n"
    text += "/professors - llistat de professors\n"
    text += "/gestio - informes i substitucions"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def professors(update, context):
    text = "/tots - llistat de tots els professors\n"
    text += "/presents - professors al centre\n"
    text += "/absents - professors fora del centre\n"
    text += "/profes_guardia - professors de guàrdia a l'hora actual\n"
    text += "/horari - horari dels professors"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def gestio(update, context):
    text = "/substitut - afegir o finalitzar una substitució\n"
    text += "/informe - informes d'assistència"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def substitut(update, context):
    text = "/afegir - afegir substitut\n"
    text += "/finalitzar - finalitzar substitució\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


dispatcher.add_handler(CommandHandler('menu', menu))
dispatcher.add_handler(MessageHandler(Filters.regex('[Mm]en[uú]'), menu))
dispatcher.add_handler(CommandHandler('professors', professors))
dispatcher.add_handler(CommandHandler('gestio', gestio))
dispatcher.add_handler(CommandHandler('substitut', substitut))


# ---------- PROFESSORS ----------


def tots(update, context):
    profes = df_profes()
    text = "No hi ha professors"
    if len(profes.index) > 0:
        text="Llistat de tot el professorat:\n\n"
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
    if len(absents.index)>0:
        profes = df_profes()
        profes_absents = absents.merge(profes, on='Dni', how='left')
        text = "Professors fora del centre:\n\n"
        for i in profes_absents.index:
            text += profes_absents.loc[i, 'Nom'] + " " + profes_absents.loc[i, 'Cognom'] + "\n"

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def profes_guardia(update, context):
    dia = dia_lectiu_actual()
    hora_lectiva = hora_lectiva_actual()
    profes = df_profes_guardia(dia, hora_lectiva)

    if hora_lectiva == 0:
        text = "No estem en horari lectiu"
    else:
        text = "Professors de guàrdia a les " + HORA[hora_lectiva - 1] + ":\n"
        for i in profes.index:
            text += profes.loc[i,"Nom"] + " " + profes.loc[i, "Cognom"] + "\n"

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


dispatcher.add_handler(CommandHandler('tots', tots))
dispatcher.add_handler(CommandHandler('presents', presents))
dispatcher.add_handler(CommandHandler('absents', absents))
dispatcher.add_handler(CommandHandler('profes_guardia', profes_guardia))


# ---------- HORARIS ----------


def horari(update, context):
    if len(context.args) == 0:
        tots(update, context)
        update.message.reply_text("Indica /horari i el codi del professor\nPer exemple: /horari 9")

    elif context.args[0].isnumeric():
        CodiHorari = int(context.args[0])
        Dia = dia_lectiu_actual()
        horari = df_horari_profe(CodiHorari, Dia)
        text = ""
        if len(horari.index)>0:
            for i in horari.index:
                text += HORA[horari.loc[i, 'Hora']-1] + " " + horari.loc[i, 'Assignatura'] + " " + horari.loc[i, 'Aula'] + " " + horari.loc[i, 'Grup'] + "\n"
        else:
            text += "No hi ha horari per a aquest codi o dia"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return ConversationHandler.END

    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Codi incorrecte")


dispatcher.add_handler(CommandHandler('horari', horari))


# ---------- GUÀRDIA ----------


def guardia_hora(hora):
    dia_lectiu = dia_lectiu_actual()
    text = "No hi ha classes en aquest moment"
    if dia_lectiu != 0 and hora != 0:
        text = llista_guardia(hora, dia_lectiu)
    return text


def guardia(update, context):
    if len(context.args) == 0:
        hora_lectiva = hora_lectiva_actual()
        text = guardia_hora(hora_lectiva)
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    elif context.args[0].isnumeric():
        hora_lectiva = int(context.args[0])

        if hora_lectiva>0 and hora_lectiva<9:
            text = guardia_hora(hora_lectiva)
        else:
            text = "El nombre ha de ser l'hora lectiva, entre 1 i 8"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="El codi ha de ser un nombre entre 1 i 8")


def text_guardia(update, context):
    hora_lectiva = hora_lectiva_actual()
    text = guardia_hora(hora_lectiva)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


dispatcher.add_handler(CommandHandler('guardia', guardia))
dispatcher.add_handler(MessageHandler(Filters.regex('[Gg]u[aà]rdia'), text_guardia))


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

    autoritzat = update.message.chat.username in GESTIO+ADMIN
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
    update.message.reply_text("Codi de l'horari a substituir?")
    return HORARI


def horari(update, context):
    SUBSTITUT[3] = update.message.text
    text = afegir_substitut(update, context, SUBSTITUT[0], SUBSTITUT[1], SUBSTITUT[2], SUBSTITUT[3])
    update.message.reply_text(text)
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text("Operació cancel·lada")
    return ConversationHandler.END


def incorrecte(update, context):
    update.message.reply_text("Valor incorrecte")
    return ConversationHandler.END


NOM, COGNOM, DNI, HORARI = range(4)

dispatcher.add_handler(ConversationHandler(entry_points=[CommandHandler('afegir', afegir)],
                                           states={
                                                NOM: [MessageHandler(Filters.regex("/cancel"), cancel),
                                                        MessageHandler(Filters.regex("[A-z]*"), nom),],
                                                COGNOM: [MessageHandler(Filters.regex("/cancel"), cancel),
                                                        MessageHandler(Filters.regex("[A-z]*"), cognom)],
                                                DNI: [MessageHandler(Filters.regex("[A-z]?[0-9]{8}[A-z]"), dni),
                                                        MessageHandler(Filters.regex("/cancel"), cancel),
                                                        MessageHandler(Filters.regex(".*"), incorrecte)],
                                                HORARI: [MessageHandler(Filters.regex("[0-9]+"), horari),
                                                        MessageHandler(Filters.regex("/cancel"), cancel),
                                                        MessageHandler(Filters.regex(".*"), incorrecte)],
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
    query = "SELECT * FROM Professor WHERE Dni = '" + Dni + "';"
    with ct.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    if len(result)==0:
        text = "Dni incorrecte"
    else:
        update = "UPDATE Professor SET Actiu = 1 WHERE Dni = '" + Dni + "';"
        with ct.cursor() as cursor:
            cursor.execute(update)
            ct.commit()
        text = "Substitució finalitzada correctament"

    ct.close()
    return text


def finalitzar(update, context):

    autoritzat = update.message.chat.username in GESTIO+ADMIN

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
                                                F_DNI: [MessageHandler(Filters.regex("[A-z]?[0-9]{8}[A-z]"), finalitzar_dni),
                                                            MessageHandler(Filters.regex("/cancel"), cancel),
                                                            MessageHandler(Filters.regex(".*"), incorrecte)],
                                                F_HORARI: [MessageHandler(Filters.regex("[0-9]+"), finalitzar_horari),
                                                            MessageHandler(Filters.regex("/cancel"), cancel),
                                                            MessageHandler(Filters.regex(".*"), incorrecte)],
                                           },
                                           fallbacks=[CommandHandler('cancel', cancel)]
                                           ))


# ---------- INFORMES ----------

DADES_INFORME = ['tipus', 'inici', 'final']


def informe(update, context):
    autoritzat = update.message.chat.username in GESTIO
    if autoritzat:
        text = "Tipus d'informe:\n"
        text += "/informe_assistencia - Temps treballat per dia\n"
        text += "/informe_absencies - Absències per dia\n"
        text += "/cancel per aturar"
        update.message.reply_text(text)
        return TIPUS
    else:
        update.message.reply_text("No autoritzat")
        return ConversationHandler.END


def informe_tipus(update, context):
    DADES_INFORME[0] = update.message.text
    update.message.reply_text("Introdueix la data d'inici: AAAA-MM-DD")
    return INICI


def informe_inici(update, context):
    DADES_INFORME[1] = update.message.text
    update.message.reply_text("Introdueix la data final: AAAA-MM-DD")
    return FINAL


def informe_final(update, context):
    DADES_INFORME[2] = update.message.text

    if DADES_INFORME[0] == "/informe_assistencia":
        filename = informe_ES_dia(DADES_INFORME[1], DADES_INFORME[2])
    elif DADES_INFORME[0] == "/informe_absencies":
        filename = informe_absencies_dia(DADES_INFORME[1], DADES_INFORME[2])
    else:
        update.message.reply_text("Valor incorrecte")
        return ConversationHandler.END

    context.bot.send_document(chat_id=update.effective_chat.id, document=open(filename, 'rb'))
    return ConversationHandler.END


def valor_incorrecte(update, context):
    update.message.reply_text("Valor incorrecte")
    return ConversationHandler.END


TIPUS, INICI, FINAL = range(3)

dispatcher.add_handler(ConversationHandler(entry_points=[CommandHandler('informe', informe)],
                                           states={
                                                TIPUS: [MessageHandler(Filters.regex("/cancel"), cancel),
                                                        MessageHandler(Filters.regex("/.*"), informe_tipus),
                                                        MessageHandler(Filters.regex(".*"), valor_incorrecte)],
                                                INICI: [MessageHandler(Filters.regex("[0-9]{4}-[0-9]{2}-[0-9]{2}"), informe_inici),
                                                        MessageHandler(Filters.regex("/cancel"), cancel),
                                                        MessageHandler(Filters.regex(".*"), valor_incorrecte)],
                                                FINAL: [MessageHandler(Filters.regex("[0-9]{4}-[0-9]{2}-[0-9]{2}"), informe_final),
                                                        MessageHandler(Filters.regex("/cancel"), cancel),
                                                        MessageHandler(Filters.regex(".*"), valor_incorrecte)],
                                           },
                                           fallbacks=[CommandHandler('cancel', cancel)]
                                           ))


# ---------- REGISTRE ----------


def registreDNI(update, context):
    text = "introdueix només les tres últimes xifres i la lletra del DNI o NIE"
    context.bot.send_message(chat_id=update.message.chat_id, text=text)


def registreCodiDNI(update, context):

    # Usuaris autoritzats
    autoritzat = update.message.chat.username in REGISTRE+ADMIN

    text = "No estàs autoritzat a realitzar aquesta acció"

    if autoritzat:
        codiDNI = update.message.text.upper()
        dades_prof = registre.cercaDNI(codiDNI)

        if len(dades_prof) == 0:
            text = "Codi incorrecte"
        else:
            text = registre.registreBD(dades_prof)

    context.bot.send_message(chat_id=update.message.chat_id, text=text)


def registreCB(update, context):

    # Usuaris autoritzats
    autoritzat = update.message.chat.username in REGISTRE+ADMIN

    text = "No estàs autoritzat a realitzar aquesta acció"

    if autoritzat:
        dades_prof = registre.cercaCB(update.message.text)

        if len(dades_prof)==0:
            text = "Aquest codi de barres no està associat a cap professor"
        else:
            text = registre.registreBD(dades_prof)

    context.bot.send_message(chat_id=update.message.chat_id, text=text)


dispatcher.add_handler(MessageHandler(Filters.regex('[A-z]?[0-9]{7,8}[A-z]'), registreDNI))
dispatcher.add_handler(MessageHandler(Filters.regex('[0-9]{3}[A-z]'), registreCodiDNI))
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