#!/usr/bin/env python3
import os
import logging
import threading

from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# ——————————— LOGGING ——————————————————————————————————————————————
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ——————————— TEXTY ———————————————————————————————————————————————
CZ_MENU = """🥐 <b>COFFEE PERK MENU</b> ☕️
U nás nejde jen o kafe. Je to malý rituál. Je to nálada. Je to... láska v šálku. 💘

☕ Výběrová káva  
🍳 Snídaně (lehké i pořádné)  
🍰 Domácí dorty  
🥗 Brunch a saláty

📄 <b>Kompletní menu:</b>
https://www.coffeeperk.cz/jidelni-listek

Ať už si dáte espresso, matchu nebo zázvorovku – tady to chutná líp. 💛
"""

CZ_HOURS = """🕐 <b>KDY MÁME OTEVŘENO?</b>

📅 Pondělí–Pátek: 7:30 – 17:00  
📅 Sobota & Neděle: ZAVŘENO

Chcete nás navštívit? Jsme tu každý všední den od brzkého rána.  
Těšíme se na vás! ☕
"""

CZ_WHERE = """📍 <b>KDE NÁS NAJDETE?</b>

🏠 Vyskočilova 1100/2, Praha 4  
🗺️ https://goo.gl/maps/XU3nYKDcCmC2

Najdete nás snadno – stylová kavárna, příjemná atmosféra a lidé, co kávu berou vážně i s úsměvem.  
Zastavte se. Na chvilku nebo na celý den.
"""

CZ_CONTACT = """📞 <b>KONTAKTUJTE NÁS</b>

📬 info@coffeeperk.cz  
📞 +420 725 422 518

Rádi vám pomůžeme s rezervací, odpovíme na vaše dotazy nebo poradíme s výběrem.  
Neváhejte se nám ozvat – jsme tu pro vás.
"""

CZ_PREORDER = """📦 <b>PŘEDOBJEDNÁVKY</b>

Brzy spustíme možnost objednat si kávu a snídani předem přes Telegram.  
Zatím nás navštivte osobně – těšíme se! ☕️
"""

CZ_REASONS = """😎 <b>DŮVODY, PROČ SI ZAJÍT NA KÁVU</b>

☕ Protože svět se lépe řeší s kofeinem.  
📚 Protože práce počká – espresso ne.  
💬 Protože dobrá konverzace začíná u šálku.  
👀 Protože dnes jste už skoro byli produktivní.  
🧠 Protože mozek startuje až po druhé kávě.  
🌦️ Protože venku prší… nebo svítí slunce… nebo prostě cítíte, že je čas.

A někdy netřeba důvod. Prostě jen přijďte. 💛
"""

EN_MENU = """🥐 <b>COFFEE PERK MENU</b> ☕️
Coffee isn’t just a drink. It’s a ritual. A vibe. Love in a cup. 💘

☕ Specialty coffee to wake you up in the morning—and keep you sharp all day.  
🍳 Breakfast—light bites or hearty feasts.  
🍰 Homemade cakes—for celebrations, breakups, or just because.  
🥗 Brunch & salads—yes, something healthy that actually tastes good!

📄 <b>Full menu:</b>
https://www.coffeeperk.cz/jidelni-listek

Whether it’s an espresso, matcha, or ginger latte—you’ll taste the difference. 💛
"""

EN_HOURS = """🕐 <b>OPENING HOURS</b>

📅 Mon–Fri: 7:30 – 17:00  
📅 Sat & Sun: CLOSED

Need your caffeine fix? We’re open early on weekdays.  
Can’t wait to see you! ☕
"""

EN_WHERE = """📍 <b>FIND US AT</b>

🏠 Vyskočilova 1100/2, Prague 4  
🗺️ https://goo.gl/maps/XU3nYKDcCmC2

Look for the stylish café with great atmosphere and smiling people who take their coffee seriously.  
Drop by—whether for a quick break or a full day’s work.
"""

EN_CONTACT = """📞 <b>CONTACT & RESERVATIONS</b>

📬 info@coffeeperk.cz  
📞 +420 725 422 518

We’re happy to help with reservations, answer questions, or guide you through our offerings.  
Feel free to reach out—we’re here for you.
"""

EN_PREORDER = """📦 <b>PRE-ORDERS (COMING SOON)</b>

Soon you’ll be able to pre-order coffee and breakfast right here on Telegram.  
For now, visit us in person—we can’t wait! ☕️
"""

EN_REASONS = """😎 <b>REASONS TO GRAB A COFFEE</b>

☕ Because the world runs on caffeine.  
📚 Because work can wait; espresso can’t.  
💬 Because good conversations start with coffee.  
👀 Because you were almost productive today.  
🧠 Because your brain boots after the second cup.  
🌦️ Because it’s raining... or sunny... or you just feel like it.

Sometimes, no reason is needed. Just come by. 💛
"""

RESPONSES = {
    "menu_cz": CZ_MENU,     "hours_cz": CZ_HOURS,
    "where_cz": CZ_WHERE,   "contact_cz": CZ_CONTACT,
    "preorder_cz": CZ_PREORDER, "reasons_cz": CZ_REASONS,
    "menu_en": EN_MENU,     "hours_en": EN_HOURS,
    "where_en": EN_WHERE,   "contact_en": EN_CONTACT,
    "preorder_en": EN_PREORDER, "reasons_en": EN_REASONS,
}

# ——————————— INLINE KLÁVESNICE —————————————————————————————————————
lang_kb = InlineKeyboardMarkup([
    [InlineKeyboardButton("🇨🇿 Čeština", callback_data="lang_cz"),
     InlineKeyboardButton("🌍 English", callback_data="lang_en")],
])

menu_kb_cz = InlineKeyboardMarkup([
    [InlineKeyboardButton("🧾 Menu a nabídka", callback_data="menu_cz"),
     InlineKeyboardButton("🕐 Otevírací doba", callback_data="hours_cz")],
    [InlineKeyboardButton("📍 Kde nás najdete", callback_data="where_cz"),
     InlineKeyboardButton("📞 Kontakt / Rezervace", callback_data="contact_cz")],
    [InlineKeyboardButton("📦 Předobjednávka", callback_data="preorder_cz"),
     InlineKeyboardButton("😎 Důvody kávu", callback_data="reasons_cz")],
])

menu_kb_en = InlineKeyboardMarkup([
    [InlineKeyboardButton("🧾 Menu & Offerings", callback_data="menu_en"),
     InlineKeyboardButton("🕐 Opening Hours", callback_data="hours_en")],
    [InlineKeyboardButton("📍 How to find us", callback_data="where_en"),
     InlineKeyboardButton("📞 Contact / Reservation", callback_data="contact_en")],
    [InlineKeyboardButton("📦 Pre-order", callback_data="preorder_en"),
     InlineKeyboardButton("😎 Reasons to grab a coffee", callback_data="reasons_en")],
])

# ——————————— FLASK HEALTHCHECK —————————————————————————————————————
app = Flask(__name__)

@app.route("/", methods=["GET"])
def healthcheck():
    return "OK", 200

def run_flask():
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# ——————————— HANDLERY BOTA ———————————————————————————————————————
def start(update, context: CallbackContext):
    update.message.reply_text(
        "☕️ Vítejte v Coffee Perk!\n"
        "Těší nás, že jste tu. 🌟\n"
        "Prosím, vyberte si jazyk. 🗣️\n\n"
        "☕️ Welcome to Coffee Perk!\n"
        "We’re happy to see you here. 🌟\n"
        "Please choose your language. 🗣️",
        reply_markup=lang_kb,
        parse_mode=ParseMode.HTML,
    )

def button(update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data

    if data.startswith("lang_"):
        lang = data.split("_")[1]
        text = "Na co se mě můžeš zeptat:" if lang == "cz" else "What you can ask me:"
        kb = menu_kb_cz if lang == "cz" else menu_kb_en
        query.edit_message_text(text, reply_markup=kb)
    else:
        resp = RESPONSES.get(data, "Omlouvám se, něco se pokazilo.")
        query.edit_message_text(resp, parse_mode=ParseMode.HTML)

# ——————————— MAIN ——————————————————————————————————————————————
def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("Nenastaven TELEGRAM_TOKEN")
        return

    threading.Thread(target=run_flask, daemon=True).start()

    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    logger.info("Spouštím polling bota...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
