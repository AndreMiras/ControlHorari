from random import choice
from os import path
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler
from re import match

import registre, professors, guardia, substitucions, informes
from dades import *
from utils import *

import logging
dir_path = path.dirname(path.realpath(__file__))
logging.basicConfig( filename=dir_path + "/logs/main.log",
                     filemode='a',
                     level=logging.INFO,
                     format= '%(asctime)s - %(levelname)s - %(lineno)s - %(message)s')


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
    text = "Aquest bot ha sigut creat per Víctor Boix (@" + ADMIN[0] + ")"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('ajuda', ajuda))
dispatcher.add_handler(MessageHandler(Filters.regex('.*[Aa]juda.*'), ajuda))
dispatcher.add_handler(CommandHandler('help', ajuda))
dispatcher.add_handler(CommandHandler('autor', autor))


# ---------- MENU -----------


def menu(update, context):
    text = "/guardia - professors a substituir a l'hora actual\n"
    text += "/professors - llistats de professorat\n"
    text += "/gestio - informes i substitucions"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def menu_professors(update, context):
    text = "/tots - llistat de tots els professors\n"
    text += "/presents - professors al centre\n"
    text += "/absents - professors fora del centre\n"
    text += "/profes_guardia - professors de guàrdia a l'hora actual\n"
    text += "/horari - horari de tots els professors"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def menu_gestio(update, context):
    permisos = update.message.chat.username in GESTIO+ADMIN

    if permisos:
        text = "/substitucio - afegir o finalitzar una substitució\n"
        text += "/informe - informes d'assistència del professorat"
    else:
        text = "No tens permisos per accedir a aquest menú"

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def menu_substitut(update, context):
    text = "/afegir - afegir una substitució\n"
    text += "/finalitzar - finalitzar una substitució\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


dispatcher.add_handler(CommandHandler('menu', menu))
dispatcher.add_handler(MessageHandler(Filters.regex('[Mm]en[uú]'), menu))
dispatcher.add_handler(CommandHandler('professors', menu_professors))
dispatcher.add_handler(CommandHandler('gestio', menu_gestio))
dispatcher.add_handler(CommandHandler('substitucio', menu_substitut))


# ---------- GUÀRDIA ----------


def guardia_command(update, context):
    if len(context.args) == 0:
        hora = hora_lectiva_actual()
        dia = dia_actual()
        text = guardia.llista(dia, hora)

    elif match("^[1-8]$", context.args[0]):
        hora = int(context.args[0])
        dia = dia_actual()
        text = guardia.llista(dia, hora)

    else:
        text="L'hora ha de ser un nombre entre 1 i 8"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def guardia_message(update, context):
    hora = hora_lectiva_actual()
    dia = dia_actual()
    text = guardia.llista(dia, hora)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


dispatcher.add_handler(CommandHandler('guardia', guardia_command))


# ---------- PROFESSORS ----------


def tots(update, context):
    text = professors.tots()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def substituts(update, context):
    text = professors.substituts()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def presents(update, context):
    text = professors.presents()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def absents(update, context):
    text = professors.absents()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def profes_guardia(update, context):
    text = professors.guardia()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def horari(update, context):
    if len(context.args) == 0:
        tots(update, context)
        text = "Indica /horari i el codi del professor\nPer exemple: /horari 9"

    elif match("^[0-9]{1,2}$", context.args[0]):
        codi_horari = int(context.args[0])
        text = professors.horari(codi_horari)

    else:
        text="Codi incorrecte"

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


dispatcher.add_handler(CommandHandler('tots', tots))
dispatcher.add_handler(CommandHandler('presents', presents))
dispatcher.add_handler(CommandHandler('absents', absents))
dispatcher.add_handler(CommandHandler('profes_guardia', profes_guardia))
dispatcher.add_handler(CommandHandler('horari', horari))


# ---------- AFEGIR SUBSTITUT ----------


SUBSTITUT = ['Nom', 'Cognom', 'Dni', 'Horari']


def afegir(update, context):
    permisos = update.message.chat.username in GESTIO + ADMIN

    if permisos:
        update.message.reply_text("Nom del substitut?\n/cancel per cancel·lar l'operació")
        return NOM
    else:
        update.message.reply_text("No tens permisos")
        return ConversationHandler.END


def afegir_nom(update, context):
    SUBSTITUT[0] = update.message.text
    update.message.reply_text("Cognom del substitut?\n/cancel per cancel·lar l'operació")
    return COGNOM


def afegir_cognom(update, context):
    SUBSTITUT[1] = update.message.text
    update.message.reply_text("DNI del substitut?\n/cancel per cancel·lar l'operació")
    return DNI


def afegir_dni(update, context):
    SUBSTITUT[2] = update.message.text
    tots(update, context)
    update.message.reply_text("Codi de l'horari a substituir?\n/cancel per cancel·lar l'operació")
    return HORARI


def afegir_horari(update, context):
    try:
        # Missatge confirmació
        SUBSTITUT[3] = int(update.message.text)
        text = substitucions.afegir(SUBSTITUT[0], SUBSTITUT[1], SUBSTITUT[2], SUBSTITUT[3])
        update.message.reply_text(text)

        # Imatge codi de barres
        nom_fitxer = "./codis/" + SUBSTITUT[2] + ".png"
        if path.isfile(nom_fitxer):
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(nom_fitxer, 'rb'))

    except Exception as e:
        logging.error(e)
        update.message.reply_text("Problema afegint la substitució")

    finally:
        return ConversationHandler.END


def afegir_cancel(update, context):
    update.message.reply_text("Operació cancel·lada")
    return ConversationHandler.END


def afegir_incorrecte(update, context):
    update.message.reply_text("Valor incorrecte\nOperació cancel·lada")
    return ConversationHandler.END


NOM, COGNOM, DNI, HORARI = range(4)

dispatcher.add_handler(ConversationHandler(entry_points=[CommandHandler('afegir', afegir)],
                                           states={
                                                NOM: [MessageHandler(Filters.regex("/cancel"), afegir_cancel),
                                                      MessageHandler(Filters.regex("[A-z]*"), afegir_nom),
                                                      MessageHandler(Filters.regex(".*"), afegir_incorrecte)],
                                                COGNOM: [MessageHandler(Filters.regex("/cancel"), afegir_cancel),
                                                         MessageHandler(Filters.regex("[A-z]*"), afegir_cognom),
                                                         MessageHandler(Filters.regex(".*"), afegir_incorrecte)],
                                                DNI: [MessageHandler(Filters.regex("[A-z]?[0-9]{8}[A-z]"), afegir_dni),
                                                      MessageHandler(Filters.regex("/cancel"), afegir_cancel),
                                                      MessageHandler(Filters.regex(".*"), afegir_incorrecte)],
                                                HORARI: [MessageHandler(Filters.regex("^[0-9]{1,2}$"), afegir_horari),
                                                         MessageHandler(Filters.regex("/cancel"), afegir_cancel),
                                                         MessageHandler(Filters.regex(".*"), afegir_incorrecte)],
                                           },
                                           fallbacks=[CommandHandler('cancel', afegir_cancel)]
                                           ))


# ---------- FINALITZAR SUBSTITUCIÓ -------------


def finalitzar(update, context):

    permisos = update.message.chat.username in GESTIO+ADMIN

    if permisos:
        if professors.substituts() != "No hi ha substituts":
            substituts(update, context)
            update.message.reply_text("Codi de la substitució a finalitzar?\n/cancel per cancel·lar l'operació")
            return F_HORARI

        else:
            update.message.reply_text("No hi ha substituts")
            return ConversationHandler.END

    else:
        update.message.reply_text("No tens permisos")
        return ConversationHandler.END


def finalitzar_horari(update, context):
    try:
        horari = int(update.message.text)
        text = substitucions.finalitzar(horari)

    except Exception as e:
        logging.error(e)
        text = "Problema finalitzant la substitució"

    finally:
        update.message.reply_text(text)
        return ConversationHandler.END


def finalitzar_cancel(update, context):
    update.message.reply_text("Operació cancel·lada")
    return ConversationHandler.END


def finalitzar_incorrecte(update, context):
    update.message.reply_text("Valor incorrecte\nOperació cancel·lada")
    return ConversationHandler.END


F_HORARI = 0

dispatcher.add_handler(ConversationHandler(entry_points=[CommandHandler('finalitzar', finalitzar)],
                                           states={
                                                F_HORARI: [MessageHandler(Filters.regex('^[0-9]{1,2}$'), finalitzar_horari),
                                                           MessageHandler(Filters.regex('/cancel'), finalitzar_cancel),
                                                           MessageHandler(Filters.regex('.*'), finalitzar_incorrecte)],
                                           },
                                           fallbacks=[CommandHandler('cancel', finalitzar_cancel)]
                                           ))


# ---------- INFORMES ----------

DADES_INFORME = [0, 'inici', 'final']


def informe(update, context):
    permisos = update.message.chat.username in GESTIO+ADMIN

    if permisos:
        text = "Tipus d'informe:\n"
        text += "1. Assistència: temps treballat segons el registre d'entrades i sortides\n"
        text += "2. Absències: temps d'absència segons l'horari de cada professor\n"
        text += "/cancel per aturar"
        update.message.reply_text(text)
        return TIPUS
    else:
        update.message.reply_text("No tens permisos")
        return ConversationHandler.END


def informe_tipus(update, context):
    DADES_INFORME[0] = int(update.message.text)
    text = "Informe d'assistència" if DADES_INFORME[0] == 1 else "Informe d'absències"
    context.bot.send_message(chat_id=update.message.chat_id, text=text)

    text = "Introdueix la data d'inici: AAAA-MM-DD\n"
    text += "/cancel per aturar"
    update.message.reply_text(text)
    return INICI


def informe_inici(update, context):
    DADES_INFORME[1] = update.message.text
    text = "Introdueix la data final: AAAA-MM-DD\n"
    text += "/cancel per aturar"
    update.message.reply_text(text)
    return FINAL


def informe_final(update, context):
    DADES_INFORME[2] = update.message.text

    try:
        if DADES_INFORME[0] == 1:
            filename = informes.assistencia(DADES_INFORME[1], DADES_INFORME[2])
        else:
            filename = informes.absencies(DADES_INFORME[1], DADES_INFORME[2])

        context.bot.send_document(chat_id=update.effective_chat.id, document=open(filename, 'rb'))

    except Exception as e:
        logging.error(e)
        update.message.reply_text("Problema generant l'informe")

    finally:
        return ConversationHandler.END


def informe_cancel(update, context):
    update.message.reply_text("Operació cancel·lada")
    return ConversationHandler.END


def informe_incorrecte(update, context):
    update.message.reply_text("Valor incorrecte\nOperació cancel·lada")
    return ConversationHandler.END


TIPUS, INICI, FINAL = range(3)

dispatcher.add_handler(ConversationHandler(entry_points=[CommandHandler('informe', informe)],
                                           states={
                                                TIPUS: [MessageHandler(Filters.regex("[1|2]"), informe_tipus),
                                                        MessageHandler(Filters.regex("/cancel"), informe_cancel),
                                                        MessageHandler(Filters.regex(".*"), informe_incorrecte)],
                                                INICI: [MessageHandler(Filters.regex("[0-9]{4}-[0-9]{2}-[0-9]{2}"), informe_inici),
                                                        MessageHandler(Filters.regex("/cancel"), informe_cancel),
                                                        MessageHandler(Filters.regex(".*"), informe_incorrecte)],
                                                FINAL: [MessageHandler(Filters.regex("[0-9]{4}-[0-9]{2}-[0-9]{2}"), informe_final),
                                                        MessageHandler(Filters.regex("/cancel"), informe_cancel),
                                                        MessageHandler(Filters.regex(".*"), informe_incorrecte)],
                                           },
                                           fallbacks=[CommandHandler('cancel', afegir_cancel)]
                                           ))


# ---------- REGISTRE ----------


def registre_dni(update, context):
    text = "introdueix només les tres últimes xifres i la lletra del DNI o NIE"
    context.bot.send_message(chat_id=update.message.chat_id, text=text)


def registre_final_dni(update, context):

    permisos = update.message.chat.username in REGISTRE+ADMIN

    if permisos:
        final_dni = update.message.text.upper()
        try:
            dades_prof = registre.professor_per_dni(final_dni)

            if len(dades_prof) > 0:
                text = registre.registre_BD(dades_prof)
            else:
                text = "Codi incorrecte"

        except Exception as e:
            logging.error(e)
            text = "Problema accedint a la base de dades"

        finally:
            context.bot.send_message(chat_id=update.message.chat_id, text=text)

    else:
        text = "No tens permisos per realitzar aquesta acció"
        context.bot.send_message(chat_id=update.message.chat_id, text=text)


def registre_codi_barres(update, context):

    permisos = update.message.chat.username in REGISTRE+ADMIN

    if permisos:
        try:
            dades_prof = registre.professor_per_codi_barres(update.message.text)

            if len(dades_prof)>0:
                text = registre.registre_BD(dades_prof)
            else:
                text = "Aquest codi de barres no està associat a cap professor"

        except Exception as e:
            logging.error(e)
            text = "Problema accedint a la base de dades"

        finally:
            context.bot.send_message(chat_id=update.message.chat_id, text=text)

    else:
        text = "No tens permisos per realitzar aquesta acció"
        context.bot.send_message(chat_id=update.message.chat_id, text=text)


dispatcher.add_handler(MessageHandler(Filters.regex('[A-z]?[0-9]{7,8}[A-z]'), registre_dni))
dispatcher.add_handler(MessageHandler(Filters.regex('[0-9]{3}[A-z]'), registre_final_dni))
dispatcher.add_handler(MessageHandler(Filters.regex('[0-9]{13}'), registre_codi_barres))


# ---------- ALTRES ----------


def eco(update, context):
    text = update.message.text
    context.bot.send_message(chat_id=update.message.chat_id, text=text)


def resposta(update, context):
    missatges = ["Què?", "No t'entenc", "Missatge incorrecte", "Què vols dir?", "Repeteix-ho", "Torna-ho a dir"]
    text = choice(missatges)
    context.bot.send_message(chat_id=update.message.chat_id, text=text)


dispatcher.add_handler(MessageHandler(Filters.regex('[Hh]ola[!]*|[Aa]d[ée]u[!]*'), eco))
dispatcher.add_handler(MessageHandler(Filters.regex('.*'), resposta))
dispatcher.add_handler(MessageHandler(Filters.regex('[Gg]u[aà]rdia'), guardia_message))

updater.start_polling()