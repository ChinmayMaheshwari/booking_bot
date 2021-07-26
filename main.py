import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
)
from .constants import *

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> int:
    timeslots = []
    for slot_id in TIMESLOT:
        if TIMESLOT[slot_id][1]:
            timeslots.append([InlineKeyboardButton(TIMESLOT[slot_id][0],callback_data= slot_id)]) 

    chat_id = update.message.chat.id
    print(chat_id)
    if chat_id in BOOKINGS and BOOKINGS[chat_id][1]:
        update.message.reply_text(
        'Your slot is already booked.\n\n'
        'use /cancel to cancel a time slot',
        )
        return
    reply_keyboard = InlineKeyboardMarkup(timeslots)
    update.message.reply_text(
        'Hi thanks for contacting i will help you in booking slot\n\n'
        'Please Select a timeslot',
        reply_markup=
            reply_keyboard
    )

    return 0

def slotbook(update: Update, context: CallbackContext):
    update.callback_query.edit_message_reply_markup()
    chat_id = update.callback_query.message.chat.id
    BOOKINGS[chat_id] = [TIMESLOT[int(update.callback_query.data)][0], False, int(update.callback_query.data)]
    TIMESLOT[int(update.callback_query.data)][1] = False
    context.bot.sendMessage(chat_id=chat_id, text="Please wait while we confirm your booking.")
    context.bot.sendMessage(chat_id=CHAT_ID,text='%s want to book slot at %s\n\n please confirm' % (update.callback_query.message.chat.first_name, TIMESLOT[int(update.callback_query.data)][0])
    ,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Yes',callback_data='yes_%s' % chat_id),InlineKeyboardButton('No',callback_data='no_%s' % chat_id)]]))

def validateslot(update: Update, context: CallbackContext):
    update.callback_query.edit_message_reply_markup()
    res = update.callback_query.data.split('_')
    if res[0]=='yes':
        context.bot.sendMessage(chat_id=int(res[1]), text='Your slot for %s is confirmed\n\n Thanks for booking' % (BOOKINGS[int(res[1])][0]))
        context.bot.sendMessage(chat_id=CHAT_ID, text='Booking confirmation send')
        BOOKINGS[int(res[1])][1] = True
    else:
        context.bot.sendMessage(chat_id=int(res[1]), text='Your slot for %s is not available please try again\n\n Thanks for booking' % (BOOKINGS[int(res[1])][0]))

def history(update: Update, context: CallbackContext):
    booking = []
    for book in BOOKINGS:
        booking.append([InlineKeyboardButton(BOOKINGS[book][0],callback_data='history_%s' % (book))])
    history = InlineKeyboardMarkup(booking)
    update.message.reply_text('Your Today Booking are as follows\n\n click on timeslot to cancel booking',reply_markup=history)

def cancelslot(update: Update, context: CallbackContext):
    update.callback_query.edit_message_reply_markup()
    context.bot.sendMessage(chat_id=CHAT_ID, text='Booking canceled')    
    BOOKINGS[int(update.callback_query.data.split('_')[1])][1] = False
    context.bot.sendMessage(chat_id=int(update.callback_query.data.split('_')[1]), 
    text='Your Booking was canceled sorry for inconvience')

def cancel(update: Update, context: CallbackContext):
    context.bot.sendMessage(chat_id=CHAT_ID, text='Booking canceled by user for %s' % (BOOKINGS[update.message.chat.id][0]))
    BOOKINGS[update.message.chat.id][1] = False
    TIMESLOT[BOOKINGS[update.message.chat.id][2]][1] = True
    update.message.reply_text('Your booking was canceled. \n\n Click /book to book again')    
    
    return

def main():

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler('book', start))
    dispatcher.add_handler(CommandHandler('cancel', cancel))
    dispatcher.add_handler(CallbackQueryHandler(slotbook,pattern='^[0-9]+$'))
    dispatcher.add_handler(CallbackQueryHandler(validateslot,pattern='^yes_[0-9]+$|no_[0-9]+$'))
    dispatcher.add_handler(CallbackQueryHandler(cancelslot,pattern='^history_[0-9]+$'))
    dispatcher.add_handler(CommandHandler('history',history))
    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()