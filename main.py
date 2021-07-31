import random
from os import path
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler

import registre
import professors
import guardia
import substitucions
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
dispatcher.add_handler(MessageHandler(Filters.regex('.*[Aa]juda.*'), ajuda))
dispatcher.add_handler(CommandHandler('help', ajuda))
dispatcher.add_handler(CommandHandler('autor', autor))


# ---------- MENU -----------


def menu(update, context):
    text = "/guardia - professors a substituir\n"
    text += "/professors - llistats de professorat\n"
    text += "/gestio - informes i substitucions"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def menu_professors(update, context):
    text = "/tots - llistat de tots els professors\n"
    text += "/presents - professors al centre\n"
    text += "/absents - professors fora del centre\n"
    text += "/profes_guardia - professors de guàrdia a l'hora actual\n"
    text += "/horari - horari dels professors"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def menu_gestio(update, context):
    text = "/substitucio - afegir o finalitzar una substitució\n"
    text += "/informe - informes d'assistència del professorat"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def menu_substitut(update, context):
    text = "/afegir - afegir una substitució\n"
    text += "/finalitzar - finalitzar substitució\n"
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
        dia = dia_lectiu_actual()
        text = guardia.llista(dia, hora)

    elif context.args[0].isnumeric():
        hora = int(context.args[0])
        dia = dia_lectiu_actual()
        text = guardia.llista(dia, hora)

    else:
        text="L'hora ha de ser un nombre entre 1 i 8"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def guardia_message(update, context):
    hora = hora_lectiva_actual()
    dia = dia_lectiu_actual()
    text = guardia.llista(dia, hora)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


dispatcher.add_handler(CommandHandler('guardia', guardia_command))
dispatcher.add_handler(MessageHandler(Filters.regex('[Gg]u[aà]rdia'), guardia_message))


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

    elif context.args[0].isnumeric():
        codiHorari = int(context.args[0])
        text = professors.horari(codiHorari)

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

    autoritzat = update.message.chat.username in GESTIO+ADMIN
    if not autoritzat:
        update.message.reply_text("No estàs autoritzat a realitzar aquesta acció")
        return ConversationHandler.END
    else:
        update.message.reply_text("Nom del substitut?\n/cancel per cancel·lar l'operació")
        return NOM


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
    SUBSTITUT[3] = int(update.message.text)

    # Missatge confirmació
    text = substitucions.afegir(SUBSTITUT[0], SUBSTITUT[1], SUBSTITUT[2], SUBSTITUT[3])
    update.message.reply_text(text)

    # Imatge codi de barres
    nom_fitxer = "./codes/" + SUBSTITUT[2] + ".png"
    if path.isfile(nom_fitxer):
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(nom_fitxer, 'rb'))
    return ConversationHandler.END


def afegir_cancel(update, context):
    update.message.reply_text("Operació cancel·lada")
    return ConversationHandler.END


def afegir_incorrecte(update, context):
    update.message.reply_text("Valor incorrecte")
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
                                                HORARI: [MessageHandler(Filters.regex("[0-9]+"), afegir_horari),
                                                         MessageHandler(Filters.regex("/cancel"), afegir_cancel),
                                                         MessageHandler(Filters.regex(".*"), afegir_incorrecte)],
                                           },
                                           fallbacks=[CommandHandler('cancel', afegir_cancel)]
                                           ))


# ---------- FINALITZAR SUBSTITUCIÓ -------------


def finalitzar(update, context):

    autoritzat = update.message.chat.username in GESTIO+ADMIN

    if not autoritzat:
        update.message.reply_text("No estàs autoritzat a realitzar aquesta acció")
        return ConversationHandler.END
    else:
        substituts(update, context)
        update.message.reply_text("Codi de l'horari del substitut?\n/cancel per cancel·lar l'operació")
        return F_HORARI


def finalitzar_horari(update, context):
    horari = int(update.message.text)
    text = substitucions.finalitzar(horari)
    update.message.reply_text(text)
    return ConversationHandler.END


def finalitzar_cancel(update, context):
    update.message.reply_text("Operació cancel·lada")
    return ConversationHandler.END


def finalitzar_incorrecte(update, context):
    update.message.reply_text("Codi horari incorrecte")
    return ConversationHandler.END


F_HORARI = 0

dispatcher.add_handler(ConversationHandler(entry_points=[CommandHandler('finalitzar', finalitzar)],
                                           states={
                                                F_HORARI: [MessageHandler(Filters.regex("[0-9]+"), finalitzar_horari),
                                                           MessageHandler(Filters.regex("/cancel"), finalitzar_cancel),
                                                           MessageHandler(Filters.regex(".*"), finalitzar_incorrecte)],
                                           },
                                           fallbacks=[CommandHandler('cancel', finalitzar_cancel)]
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
                                                TIPUS: [MessageHandler(Filters.regex("/cancel"), afegir_cancel),
                                                        MessageHandler(Filters.regex("/.*"), informe_tipus),
                                                        MessageHandler(Filters.regex(".*"), valor_incorrecte)],
                                                INICI: [MessageHandler(Filters.regex("[0-9]{4}-[0-9]{2}-[0-9]{2}"), informe_inici),
                                                        MessageHandler(Filters.regex("/cancel"), afegir_cancel),
                                                        MessageHandler(Filters.regex(".*"), valor_incorrecte)],
                                                FINAL: [MessageHandler(Filters.regex("[0-9]{4}-[0-9]{2}-[0-9]{2}"), informe_final),
                                                        MessageHandler(Filters.regex("/cancel"), afegir_cancel),
                                                        MessageHandler(Filters.regex(".*"), valor_incorrecte)],
                                           },
                                           fallbacks=[CommandHandler('cancel', afegir_cancel)]
                                           ))


# ---------- REGISTRE ----------


def registre_dni(update, context):
    text = "introdueix només les tres últimes xifres i la lletra del DNI o NIE"
    context.bot.send_message(chat_id=update.message.chat_id, text=text)


def registre_final_dni(update, context):

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


def registre_codi_barres(update, context):

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


dispatcher.add_handler(MessageHandler(Filters.regex('[A-z]?[0-9]{7,8}[A-z]'), registre_dni))
dispatcher.add_handler(MessageHandler(Filters.regex('[0-9]{3}[A-z]'), registre_final_dni))
dispatcher.add_handler(MessageHandler(Filters.regex('[0-9]{13}'), registre_codi_barres))


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