import json
import os
import logging
from datetime import datetime, timedelta, date, time as dt_time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8779477894:AAGQo4bkEv1s0Cknh4a5IVzHCVncQhRBwAM")
OWNER_ID = 7365000441
BOOKINGS_DIR = os.getenv("BOOKINGS_DIR", os.path.dirname(os.path.abspath(__file__)))
BOOKINGS_FILE = os.path.join(BOOKINGS_DIR, "bookings.json")
LANGUAGES_FILE = os.path.join(BOOKINGS_DIR, "languages.json")
WORK_START = 9
WORK_END = 20

SERVICES = {
    "men": {"name": "Мужская стрижка", "price": "600 \u20bd", "emoji": "\U0001f487", "desc": "\u041a\u043b\u0430\u0441\u0441\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u0438\u043b\u0438 \u043c\u043e\u0434\u0435\u043b\u044c\u043d\u0430\u044f \u0441\u0442\u0440\u0438\u0436\u043a\u0430\n\u043c\u044b\u0442\u044c\u0451 \u0433\u043e\u043b\u043e\u0432\u044b + \u0443\u043a\u043b\u0430\u0434\u043a\u0430"},
    "beard": {"name": "\u041e\u0444\u043e\u0440\u043c\u043b\u0435\u043d\u0438\u0435 \u0431\u043e\u0440\u043e\u0434\u044b", "price": "400 \u20bd", "emoji": "\U0001f9d4", "desc": "\u041a\u043e\u0440\u0440\u0435\u043a\u0446\u0438\u044f \u0444\u043e\u0440\u043c\u044b \u0431\u043e\u0440\u043e\u0434\u044b \u0438 \u0443\u0441\u043e\u0432\n\u0433\u043e\u0440\u044f\u0447\u0435\u0435 \u043f\u043e\u043b\u043e\u0442\u0435\u043d\u0446\u0435 + \u0431\u0430\u043b\u044c\u0437\u0430\u043c"},
    "toning_hair": {"name": "\u0422\u043e\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435 \u0432\u043e\u043b\u043e\u0441", "price": "800 \u20bd", "emoji": "\U0001f3a8", "desc": "\u041e\u0442\u0442\u0435\u043d\u043e\u0447\u043d\u043e\u0435 \u0442\u043e\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435\n\u043e\u0441\u0432\u0435\u0436\u0435\u043d\u0438\u0435 \u0446\u0432\u0435\u0442\u0430 + \u0443\u0445\u043e\u0434"},
    "toning_beard": {"name": "\u0422\u043e\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435 \u0431\u043e\u0440\u043e\u0434\u044b", "price": "700 \u20bd", "emoji": "\U0001f3ad", "desc": "\u0417\u0430\u043a\u0440\u0430\u0448\u0438\u0432\u0430\u043d\u0438\u0435 \u0441\u0435\u0434\u0438\u043d\u044b \u0432 \u0431\u043e\u0440\u043e\u0434\u0435\n\u0441\u0442\u043e\u0439\u043a\u0438\u0439 \u043e\u0442\u0442\u0435\u043d\u043e\u043a + \u0443\u0445\u043e\u0434"},
    "kids": {"name": "\u0414\u0435\u0442\u0441\u043a\u0430\u044f \u0441\u0442\u0440\u0438\u0436\u043a\u0430", "price": "600 \u20bd", "emoji": "\U0001f476", "desc": "\u0421\u0442\u0440\u0438\u0436\u043a\u0430 \u0434\u043b\u044f \u043c\u0430\u043b\u044c\u0447\u0438\u043a\u043e\u0432 \u0434\u043e 12 \u043b\u0435\u0442\n\u0430\u043a\u043a\u0443\u0440\u0430\u0442\u043d\u043e + \u0442\u0435\u0440\u043f\u0435\u043b\u0438\u0432\u043e"},
    "dad_son": {"name": "\u041f\u0430\u043f\u0430 + \u0441\u044b\u043d", "price": "1100 \u20bd", "emoji": "\U0001f468\u200d\U0001f466", "desc": "\u0421\u043e\u0432\u043c\u0435\u0441\u0442\u043d\u0430\u044f \u0441\u0442\u0440\u0438\u0436\u043a\u0430\n\u0432\u044b\u0433\u043e\u0434\u0430 100 \u20bd!"},
    "pensioner": {"name": "\u0421\u0442\u0440\u0438\u0436\u043a\u0430 \u043f\u0435\u043d\u0441\u0438\u043e\u043d\u0435\u0440\u0430\u043c", "price": "500 \u20bd", "emoji": "\U0001f474", "desc": "\u041a\u043b\u0430\u0441\u0441\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u0441\u0442\u0440\u0438\u0436\u043a\u0430\n\u0441\u043e \u0441\u043a\u0438\u0434\u043a\u043e\u0439 \u0434\u043b\u044f \u043f\u0435\u043d\u0441\u0438\u043e\u043d\u0435\u0440\u043e\u0432"},
}

MONTHS = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}

GREETINGS = {
    "morning": "Доброе утро! ☀️",
    "afternoon": "Добрый день! 🌤",
    "evening": "Добрый вечер! 🌆",
    "night": "Доброй ночи! 🌙",
}

PHONE = "+7 (917) 109-47-02"
ADDRESS = "ул. Маршала Устинова, 40А, Самара"
MAP_URL = "https://yandex.ru/maps/org/kharizma/146356869906/"
SITE_URL = "https://HarizmaBarber.github.io/"
INSTAGRAM_URL = "https://www.instagram.com/harizma_barber_/"

TR = {
    "ru": {
        "lang_name": "Русский",
        "greeting": "Я — бот для записи в барбершоп «Харизма».\nЗдесь вы можете узнать цены, записаться на\nстрижку или отменить визит.",
        "addr_line": "📍 {addr}",
        "hours_line": "⏰ Ежедневно 9:00 – 21:00",
        "phone_line": "📞 {phone}",
        "master_line": "💈 Мастер: Баха",
        "btn_about": "📖 О нас",
        "btn_services": "💇 Услуги и цены",
        "btn_book": "📅 Записаться",
        "btn_map": "📍 Как проехать",
        "btn_cancel": "❌ Отменить запись",
        "btn_help": "❓ Как работает бот",
        "btn_site": "🌐 Наш сайт",
        "btn_instagram": "📸 Instagram",
        "btn_back": "← Назад",
        "btn_back_menu": "← В меню",
        "btn_back_service": "← К выбору услуги",
        "btn_back_day": "← К выбору дня",
        "btn_confirm": "✅ Подтвердить",
        "btn_cancel_booking": "❌ Отменить",
        "btn_lang": "🌐 Язык",
        "btn_book_now": "📅 Записаться",
        "about_title": "📖 О нас",
        "about_text1": "Барбершоп «Харизма» — это место, где ценят мужской стиль и качественный сервис.",
        "about_text2": "💈 Мастер: Баха — опыт работы более 5 лет.\nЗнает всё о мужских стрижках, бороде и стиле.",
        "about_why": "Почему выбирают нас:",
        "about_w1": "✦ Индивидуальный подход к каждому клиенту",
        "about_w2": "✦ Качественные материалы и инструменты",
        "about_w3": "✦ Уютная атмосфера ✨",
        "about_w4": "✦ Удобное расположение в городе",
        "about_w5": "✦ Работаем без выходных 9:00 – 21:00",
        "about_what": "Что мы предлагаем:",
        "about_offer1": "✦ Аккуратные стрижки любой сложности",
        "about_offer2": "✦ Оформление и коррекция бороды",
        "about_offer3": "✦ Тонирование волос и бороды",
        "about_offer4": "✦ Стрижки для детей и пенсионеров",
        "about_offer5": "✦ Акция «Папа + сын» с выгодой 100 ₽",
        "about_outro": "У нас вы можете отдохнуть и выйти с новой уверенностью. ✂",
        "services_title": "💇 Наши услуги и цены",
        "help_title": "❓ Как работает бот",
        "help_cap": "🤖 Возможности:",
        "help_cap1": "• 💇 Просмотр услуг и цен",
        "help_cap2": "• 📅 Запись на стрижку онлайн",
        "help_cap3": "• ❌ Отмена записи по номеру телефона",
        "help_how": "📱 Как записаться:",
        "help_s1": "1. Нажмите «Записаться»",
        "help_s2": "2. Выберите услугу",
        "help_s3": "3. Выберите дату и время",
        "help_s4": "4. Введите имя и телефон",
        "help_s5": "5. Подтвердите запись",
        "help_addr": "📍 Адрес: {addr}",
        "help_hours": "⏰ Часы: Ежедневно 9:00 – 21:00",
        "help_hosting": "🆓 Бот работает 24/7 на JustRunMy.app",
        "map_title": "📍 Как нас найти",
        "map_addr": "🏠 Адрес:\n{addr}",
        "map_how": "🚗 Как добраться:",
        "map_stop1": "• Остановка «Улица Советской Армии» — 5 мин",
        "map_stop2": "• Остановка «Металлург» — 10 мин",
        "map_hours": "⏰ Часы работы:\nЕжедневно 9:00 – 21:00",
        "map_phone": "📞 Телефон:\n{phone}",
        "map_btn": "🗺 Открыть Яндекс Карты",
        "cancel_title": "❌ Отмена записи",
        "cancel_text": "Чтобы отменить запись, введите номер телефона, на который вы записаны:\n\n<i>Например: {phone}</i>",
        "cancel_done": "✅ Запись отменена\n\nДата: {date}\nВремя: {time}\n\nЖдём вас в другой раз! ✂",
        "cancel_notfound": "❌ Запись не найдена\n\nВозможно, она уже была отменена.",
        "cancel_search_notfound": "❌ Записей не найдено\n\nНомер <b>{phone}</b> не найден в записях.\n\nПроверьте номер или вернитесь в меню:",
        "cancel_found_title": "🔍 Найденные записи",
        "cancel_found_action": "Выберите запись для отмены:",
        "cancel_btn": "❌ Отменить {date} {time}",
        "select_service_title": "💇 Выберите услугу",
        "select_service_hint": "Нажмите на нужную услугу:",
        "select_day_title": "📅 Выберите день",
        "select_day_hint": "Доступна запись на 14 дней вперёд:",
        "today": "📌 Сегодня",
        "tomorrow": "📌 Завтра",
        "select_time_title": "📅 {date} — выбор времени",
        "select_time_free": "Свободно: {free} из {total}",
        "select_time_hint": "Выберите свободное время:",
        "slot_booked": "❌ {time} — {name}",
        "slot_free": "✅ {time}",
        "service_selected": "{emoji} {name}\n{desc}\n\n💰 Цена: {price}\n\n📅 Выберите дату для записи:",
        "enter_name": "📝 Запись на стрижку\n\n💇 Услуга: {service}\n📅 Дата: {date}\n⏰ Время: {time}\n\nВведите ваше <b>имя</b>:",
        "enter_phone": "📞 Введите номер телефона\n\n<i>Например: {phone}</i>",
        "name_error": "Пожалуйста, введите настоящее имя (от 2 символов):",
        "confirm_title": "📋 Проверьте данные\n\n💇 Услуга: {service}\n📅 Дата: {date}\n⏰ Время: {time}\n👤 Имя: {name}\n📞 Телефон: {phone}\n\nВсё верно?",
        "confirm_ask": "Нажмите ✅ Подтвердить или ❌ Отменить выше.",
        "booking_done": "✅ Вы записаны!\n\n💇 Услуга: {service}\n📅 Дата: {date}\n⏰ Время: {time}\n👤 Имя: {name}\n📞 Телефон: {phone}\n\nЖдём вас в «Харизма»! ✂\n\n📍 {addr}",
        "booking_cancelled": "❌ Запись отменена\n\nЕсли передумаете — запишитесь снова!",
        "owner_new_booking": "✂ Новая запись!\n\n💇 {service}\n📅 {date}\n⏰ {time}\n👤 {name}\n📞 {phone}\n🗺 {map_url}",
        "owner_cancelled": "❌ Запись отменена клиентом\n\n📅 {date} в {time}",
        "owner_reminder": "⏰ Напоминание: через 30 мин запись\n\n💇 {service}\n📅 {date}\n⏰ {time}\n👤 {name}\n📞 {phone}\n\n<b>Клиент пришёл?</b>",
        "owner_confirm_yes": "✅ Пришёл",
        "owner_confirm_no": "❌ Не пришёл",
        "owner_marked": "Отмечено мастером.",
        "unknown_cmd": "Я вас не понял. Используйте команды:\n\n<b>/start</b> — главное меню\n<b>/services</b> — услуги и цены\n<b>/booking</b> — записаться\n<b>/help</b> — как работает бот",
        "choose_lang": "🌐 Выберите язык / Tilni tanlang / Тілді таңдаңыз / Тилди тандоо / Забонро интихоб кунед:",
        "lang_changed": "Язык изменён на Русский 🇷🇺",
        "instagram_text": "📸 Наш Instagram\n\nПодписывайтесь!",
        "instagram_btn": "📸 Открыть Instagram",
    },
    "uz": {
        "lang_name": "O'zbek",
        "greeting": "Men — «Harizma» sartaroshxonasiga yozilish uchun botman.\nBu yerda siz narxlarni bilib olishingiz,\nsoch oldirishga yozilishingiz yoki\nbuyurtmani bekor qilishingiz mumkin.",
        "addr_line": "📍 {addr}",
        "hours_line": "⏰ Har kuni 9:00 – 21:00",
        "phone_line": "📞 {phone}",
        "master_line": "💈 Usta: Baxa",
        "btn_about": "📖 Biz haqimizda",
        "btn_services": "💇 Xizmatlar va narxlar",
        "btn_book": "📅 Yozilish",
        "btn_map": "📍 Qanday borish",
        "btn_cancel": "❌ Buyurtmani bekor qilish",
        "btn_help": "❓ Bot qanday ishlaydi",
        "btn_site": "🌐 Saytimiz",
        "btn_instagram": "📸 Instagram",
        "btn_back": "← Orqaga",
        "btn_back_menu": "← Menyuga",
        "btn_back_service": "← Xizmat tanlashga",
        "btn_back_day": "← Kun tanlashga",
        "btn_confirm": "✅ Tasdiqlash",
        "btn_cancel_booking": "❌ Bekor qilish",
        "btn_lang": "🌐 Til",
        "btn_book_now": "📅 Yozilish",
        "about_title": "📖 Biz haqimizda",
        "about_text1": "«Harizma» sartaroshxonasi — bu erkaklar uslubi va sifatli xizmat qadrlanadigan joy.",
        "about_text2": "💈 Usta: Baxa — 5 yildan ortiq tajriba.\nErkaklarga soch oldirish, soqol va uslub haqida hamma narsani biladi.",
        "about_why": "Nega bizni tanlashadi:",
        "about_w1": "✦ Har bir mijozga individual yondashish",
        "about_w2": "✦ Sifatli materiallar va asboblar",
        "about_w3": "✦ Qulay atmosfera ✨",
        "about_w4": "✦ Shaharda qulay joylashuv",
        "about_w5": "✦ Dam olishsiz ishlaymiz 9:00 – 21:00",
        "about_what": "Biz nimani taklif qilamiz:",
        "about_offer1": "✦ Har qanday murakkablikdagi soch oldirish",
        "about_offer2": "✦ Soqolni shakllantirish va tuzatish",
        "about_offer3": "✦ Soch va soqolni bo'yash",
        "about_offer4": "✦ Bolalar va nafaqaxo'rlarga soch oldirish",
        "about_offer5": "✦ «Ota + o'g'il» aksiyasi — 100 so'm tejash",
        "about_outro": "Bizda dam olishingiz va yangi ishonch bilan chiqishingiz mumkin. ✂",
        "services_title": "💇 Xizmatlar va narxlar",
        "help_title": "❓ Bot qanday ishlaydi",
        "help_cap": "🤖 Imkoniyatlar:",
        "help_cap1": "• 💇 Xizmatlar va narxlarni ko'rish",
        "help_cap2": "• 📅 Onlayn soch oldirishga yozilish",
        "help_cap3": "• ❌ Telefon raqami bo'yicha bekor qilish",
        "help_how": "📱 Qanday yozilish:",
        "help_s1": "1. «Yozilish» tugmasini bosing",
        "help_s2": "2. Xizmatni tanlang",
        "help_s3": "3. Kun va vaqtni tanlang",
        "help_s4": "4. Ism va telefon kiriting",
        "help_s5": "5. Yozilishni tasdiqlang",
        "help_addr": "📍 Manzil: {addr}",
        "help_hours": "⏰ Vaqt: Har kuni 9:00 – 21:00",
        "help_hosting": "🆓 Bot 24/7 JustRunMy.app da ishlaydi",
        "map_title": "📍 Bizni qanday topish",
        "map_addr": "🏠 Manzil:\n{addr}",
        "map_how": "🚗 Qanday borish:",
        "map_stop1": "• «Sovetskoy Armii» bekati — 5 min",
        "map_stop2": "• «Metallurg» bekati — 10 min",
        "map_hours": "⏰ Ish vaqti:\nHar kuni 9:00 – 21:00",
        "map_phone": "📞 Telefon:\n{phone}",
        "map_btn": "🗺 Yandex Xaritalarni ochish",
        "cancel_title": "❌ Buyurtmani bekor qilish",
        "cancel_text": "Buyurtmani bekor qilish uchun qaysi telefonga yozilgan bo'lsangiz, shu raqamni kiriting:\n\n<i>Masalan: {phone}</i>",
        "cancel_done": "✅ Buyurtma bekor qilindi\n\nSana: {date}\nVaqt: {time}\n\nSizni boshqa safar kutamiz! ✂",
        "cancel_notfound": "❌ Buyurtma topilmadi\n\nEhtimol, u allaqachon bekor qilingan.",
        "cancel_search_notfound": "❌ Buyurtmalar topilmadi\n\n<b>{phone}</b> raqami buyurtmalarda yo'q.\n\nRaqamni tekshiring yoki menyuga qayting:",
        "cancel_found_title": "🔍 Topilgan buyurtmalar",
        "cancel_found_action": "Bekor qilish uchun buyurtmani tanlang:",
        "cancel_btn": "❌ Bekor qilish {date} {time}",
        "select_service_title": "💇 Xizmatni tanlang",
        "select_service_hint": "Kerakli xizmatni bosing:",
        "select_day_title": "📅 Kunni tanlang",
        "select_day_hint": "14 kun oldin yozilish mumkin:",
        "today": "📌 Bugun",
        "tomorrow": "📌 Ertaga",
        "select_time_title": "📅 {date} — vaqt tanlash",
        "select_time_free": "Bo'sh: {free} ta / {total} ta",
        "select_time_hint": "Bo'sh vaqtni tanlang:",
        "slot_booked": "❌ {time} — {name}",
        "slot_free": "✅ {time}",
        "service_selected": "{emoji} {name}\n{desc}\n\n💰 Narx: {price}\n\n📅 Yozilish uchun kunni tanlang:",
        "enter_name": "📝 Soch oldirishga yozilish\n\n💇 Xizmat: {service}\n📅 Sana: {date}\n⏰ Vaqt: {time}\n\nIsmingizni kiriting:",
        "enter_phone": "📞 Telefon raqamingizni kiriting\n\n<i>Masalan: {phone}</i>",
        "name_error": "Iltimos, haqiqiy ismingizni kiriting (kamida 2 harf):",
        "confirm_title": "📋 Ma'lumotlarni tekshiring\n\n💇 Xizmat: {service}\n📅 Sana: {date}\n⏰ Vaqt: {time}\n👤 Ism: {name}\n📞 Telefon: {phone}\n\nHammasi to'g'rimi?",
        "confirm_ask": "✅ Tasdiqlash yoki ❌ Bekor qilish tugmasini bosing.",
        "booking_done": "✅ Siz yozildingiz!\n\n💇 Xizmat: {service}\n📅 Sana: {date}\n⏰ Vaqt: {time}\n👤 Ism: {name}\n📞 Telefon: {phone}\n\n«Harizma»da kutamiz! ✂\n\n📍 {addr}",
        "booking_cancelled": "❌ Buyurtma bekor qilindi\n\nAgar qayta yozilmoqchi bo'lsangiz — yoziling!",
        "owner_new_booking": "✂ Yangi yozilish!\n\n💇 {service}\n📅 {date}\n⏰ {time}\n👤 {name}\n📞 {phone}\n🗺 {map_url}",
        "owner_cancelled": "❌ Mijoz buyurtmani bekor qildi\n\n📅 {date} {time} da",
        "owner_reminder": "⏰ Eslatma: 30 daqiqadan keyin yozilish\n\n💇 {service}\n📅 {date}\n⏰ {time}\n👤 {name}\n📞 {phone}\n\n<b>Mijoz keldimi?</b>",
        "owner_confirm_yes": "✅ Keldi",
        "owner_confirm_no": "❌ Kelmadi",
        "owner_marked": "Usta tomonidan belgilandi.",
        "unknown_cmd": "Men sizni tushunmadim. Buyruqlardan foydalaning:\n\n<b>/start</b> — asosiy menyu\n<b>/services</b> — xizmatlar va narxlar\n<b>/booking</b> — yozilish\n<b>/help</b> — bot qanday ishlaydi",
        "choose_lang": "🌐 Выберите язык / Tilni tanlang / Тілді таңдаңыз / Тилди тандоо / Забонро интихоб кунед:",
        "lang_changed": "Til O'zbek tiliga o'zgartirildi 🇺🇿",
        "instagram_text": "📸 Bizning Instagram\n\nObuna bo'ling!",
        "instagram_btn": "📸 Instagramni ochish",
    },
    "kz": {
        "lang_name": "Қазақ",
        "greeting": "Мен — «Харизма» барбершопына жазылу ботымын.\nМұнда сіз бағаларды біле аласыз, шаш алуға\nжазыла аласыз немесе жазылымды болдыра аласыз.",
        "addr_line": "📍 {addr}",
        "hours_line": "⏰ Күнделікті 9:00 – 21:00",
        "phone_line": "📞 {phone}",
        "master_line": "💈 Шебер: Баха",
        "btn_about": "📖 Біз туралы",
        "btn_services": "💇 Қызметтер мен бағалар",
        "btn_book": "📅 Жазылу",
        "btn_map": "📍 Қалай бару",
        "btn_cancel": "❌ Жазылымды болдыру",
        "btn_help": "❓ Бот қалай жұмыс істейді",
        "btn_site": "🌐 Сайтымыз",
        "btn_instagram": "📸 Instagram",
        "btn_back": "← Артқа",
        "btn_back_menu": "← Мәзірге",
        "btn_back_service": "← Қызмет таңдауға",
        "btn_back_day": "← Күн таңдауға",
        "btn_confirm": "✅ Растау",
        "btn_cancel_booking": "❌ Болдырмау",
        "btn_lang": "🌐 Тіл",
        "btn_book_now": "📅 Жазылу",
        "about_title": "📖 Біз туралы",
        "about_text1": "«Харизма» барбершопы — бұл ерлер стилі мен сапалы қызмет бағаланатын орын.",
        "about_text2": "💈 Шебер: Баха — 5 жылдан астам тәжірибе.\nЕрлер шашы, сақал және стиль туралы бәрін біледі.",
        "about_why": "Неге бізді таңдайды:",
        "about_w1": "✦ Әр клиентке жеке көзқарас",
        "about_w2": "✦ Сапалы материалдар мен құралдар",
        "about_w3": "✦ Жайлы атмосфера ✨",
        "about_w4": "✦ Қалада ыңғайлы орналасу",
        "about_w5": "✦ Демалыссыз жұмыс 9:00 – 21:00",
        "about_what": "Біз не ұсынамыз:",
        "about_offer1": "✦ Кез келген күрделіліктегі шаш алу",
        "about_offer2": "✦ Сақалды сәндеу және түзету",
        "about_offer3": "✦ Шаш пен сақалды тонировкалау",
        "about_offer4": "✦ Балалар мен зейнеткерлерге шаш алу",
        "about_offer5": "✦ «Әке + бала» акциясы — 100 ₽ үнемдеу",
        "about_outro": "Бізде демалуға және жаңа сенімділікпен шығуға болады. ✂",
        "services_title": "💇 Қызметтер мен бағалар",
        "help_title": "❓ Бот қалай жұмыс істейді",
        "help_cap": "🤖 Мүмкіндіктер:",
        "help_cap1": "• 💇 Қызметтер мен бағаларды көру",
        "help_cap2": "• 📅 Онлайн шаш алуға жазылу",
        "help_cap3": "• ❌ Телефон нөмірі бойынша болдыру",
        "help_how": "📱 Қалай жазылу:",
        "help_s1": "1. «Жазылу» түймесін басыңыз",
        "help_s2": "2. Қызметті таңдаңыз",
        "help_s3": "3. Күн мен уақытты таңдаңыз",
        "help_s4": "4. Атыңыз бен телефонды енгізіңіз",
        "help_s5": "5. Жазылымды растаңыз",
        "help_addr": "📍 Мекенжай: {addr}",
        "help_hours": "⏰ Уақыт: Күнделікті 9:00 – 21:00",
        "help_hosting": "🆓 Бот 24/7 JustRunMy.app сайтында жұмыс істейді",
        "map_title": "📍 Бізді қалай табу",
        "map_addr": "🏠 Мекенжай:\n{addr}",
        "map_how": "🚗 Қалай бару:",
        "map_stop1": "• «Советской Армии» аялдамасы — 5 мин",
        "map_stop2": "• «Металлург» аялдамасы — 10 мин",
        "map_hours": "⏰ Жұмыс уақыты:\nКүнделікті 9:00 – 21:00",
        "map_phone": "📞 Телефон:\n{phone}",
        "map_btn": "🗺 Яндекс Карталарды ашу",
        "cancel_title": "❌ Жазылымды болдыру",
        "cancel_text": "Жазылымды болдыру үшін қай телефонға жазылғаныңызды енгізіңіз:\n\n<i>Мысалы: {phone}</i>",
        "cancel_done": "✅ Жазылым болдырылды\n\nКүні: {date}\nУақыт: {time}\n\nСізді басқа жолы күтеміз! ✂",
        "cancel_notfound": "❌ Жазылым табылмады\n\nМүмкін, ол бұрыннан болдырылған.",
        "cancel_search_notfound": "❌ Жазылымдар табылмады\n\n<b>{phone}</b> нөмірі жазылымдарда жоқ.\n\nНөмірді тексеріңіз немесе мәзірге қайтыңыз:",
        "cancel_found_title": "🔍 Табылған жазылымдар",
        "cancel_found_action": "Болдыру үшін жазылымды таңдаңыз:",
        "cancel_btn": "❌ Болдыру {date} {time}",
        "select_service_title": "💇 Қызметті таңдаңыз",
        "select_service_hint": "Қажетті қызметті басыңыз:",
        "select_day_title": "📅 Күнді таңдаңыз",
        "select_day_hint": "14 күн алдын жазылуға болады:",
        "today": "📌 Бүгін",
        "tomorrow": "📌 Ертең",
        "select_time_title": "📅 {date} — уақыт таңдау",
        "select_time_free": "Бос: {free} / {total}",
        "select_time_hint": "Бос уақытты таңдаңыз:",
        "slot_booked": "❌ {time} — {name}",
        "slot_free": "✅ {time}",
        "service_selected": "{emoji} {name}\n{desc}\n\n💰 Бағасы: {price}\n\n📅 Жазылу үшін күнді таңдаңыз:",
        "enter_name": "📝 Шаш алуға жазылу\n\n💇 Қызмет: {service}\n📅 Күн: {date}\n⏰ Уақыт: {time}\n\nАтыңызды енгізіңіз:",
        "enter_phone": "📞 Телефон нөміріңізді енгізіңіз\n\n<i>Мысалы: {phone}</i>",
        "name_error": "Өтінемін, нақты атыңызды енгізіңіз (кемінде 2 әріп):",
        "confirm_title": "📋 Деректерді тексеріңіз\n\n💇 Қызмет: {service}\n📅 Күн: {date}\n⏰ Уақыт: {time}\n👤 Аты: {name}\n📞 Телефон: {phone}\n\nБәрі дұрыс па?",
        "confirm_ask": "✅ Растау немесе ❌ Болдырмау түймесін басыңыз.",
        "booking_done": "✅ Сіз жазылдыңыз!\n\n💇 Қызмет: {service}\n📅 Күн: {date}\n⏰ Уақыт: {time}\n👤 Аты: {name}\n📞 Телефон: {phone}\n\n«Харизма»да күтеміз! ✂\n\n📍 {addr}",
        "booking_cancelled": "❌ Жазылым болдырылды\n\nҚайта жазылғыңыз келсе — жазылыңыз!",
        "owner_new_booking": "✂ Жаңа жазылым!\n\n💇 {service}\n📅 {date}\n⏰ {time}\n👤 {name}\n📞 {phone}\n🗺 {map_url}",
        "owner_cancelled": "❌ Клиент жазылымды болдырды\n\n📅 {date} {time} кезінде",
        "owner_reminder": "⏰ Еске салу: 30 минуттан кейін жазылым\n\n💇 {service}\n📅 {date}\n⏰ {time}\n👤 {name}\n📞 {phone}\n\n<b>Клиент келді ме?</b>",
        "owner_confirm_yes": "✅ Келді",
        "owner_confirm_no": "❌ Келмеді",
        "owner_marked": "Шебермен белгіленді.",
        "unknown_cmd": "Мен сізді түсінбедім. Пәрмендерді қолданыңыз:\n\n<b>/start</b> — негізгі мәзір\n<b>/services</b> — қызметтер мен бағалар\n<b>/booking</b> — жазылу\n<b>/help</b> — бот қалай жұмыс істейді",
        "choose_lang": "🌐 Выберите язык / Tilni tanlang / Тілді таңдаңыз / Тилди тандоо / Забонро интихоб кунед:",
        "lang_changed": "Тіл Қазақ тіліне ауыстырылды 🇰🇿",
        "instagram_text": "📸 Біздің Instagram\n\nЖазылыңыз!",
        "instagram_btn": "📸 Instagram-ды ашу",
    },
    "kg": {
        "lang_name": "Кыргыз",
        "greeting": "Мен — «Харизма» барбершопына жазылу боту.\nБул жерде сиз бааларды биле аласыз, чач алдырууга\nжазыла аласыз же жазылууну жокко чыгара аласыз.",
        "addr_line": "📍 {addr}",
        "hours_line": "⏰ Күн сайын 9:00 – 21:00",
        "phone_line": "📞 {phone}",
        "master_line": "💈 Чебер: Баха",
        "btn_about": "📖 Биз жөнүндө",
        "btn_services": "💇 Кызматтар жана баалар",
        "btn_book": "📅 Жазылуу",
        "btn_map": "📍 Кантип баруу",
        "btn_cancel": "❌ Жазылууну жокко чыгаруу",
        "btn_help": "❓ Бот кантип иштейт",
        "btn_site": "🌐 Сайтыбыз",
        "btn_instagram": "📸 Instagram",
        "btn_back": "← Артка",
        "btn_back_menu": "← Менюга",
        "btn_back_service": "← Кызмат тандоого",
        "btn_back_day": "← Күн тандоого",
        "btn_confirm": "✅ Ырастоо",
        "btn_cancel_booking": "❌ Жокко чыгаруу",
        "btn_lang": "🌐 Тил",
        "btn_book_now": "📅 Жазылуу",
        "about_title": "📖 Биз жөнүндө",
        "about_text1": "«Харизма» барбершопу — бул эркектер стили жана сапаттуу кызмат бааланган жер.",
        "about_text2": "💈 Чебер: Баха — 5 жылдан ашык тажрыйба.\nЭркектер чачы, сакал жана стиль жөнүндө баарын билет.",
        "about_why": "Эмне үчүн бизди тандашат:",
        "about_w1": "✦ Ар бир кардарга жеке мамиле",
        "about_w2": "✦ Сапаттуу материалдар жана шаймандар",
        "about_w3": "✦ Жайлуу атмосфера ✨",
        "about_w4": "✦ Шаарда ыңгайлуу жайгашуу",
        "about_w5": "✦ Дем алышсыз иштейбиз 9:00 – 21:00",
        "about_what": "Биз эмне сунуштайбыз:",
        "about_offer1": "✦ Кандайдыр бир татаалдыктагы чач алуу",
        "about_offer2": "✦ Сакалды жасоо жана оңдоо",
        "about_offer3": "✦ Чач жана сакалды тонировкалоо",
        "about_offer4": "✦ Балдар жана пенсионерлерге чач алуу",
        "about_offer5": "✦ «Ата + уул» акциясы — 100 ₽ үнөмдөө",
        "about_outro": "Бизде эс алып, жаңы ишеним менен чыга аласыз. ✂",
        "services_title": "💇 Кызматтар жана баалар",
        "help_title": "❓ Бот кантип иштейт",
        "help_cap": "🤖 Мүмкүнчүлүктөр:",
        "help_cap1": "• 💇 Кызматтар жана бааларды көрүү",
        "help_cap2": "• 📅 Онлайн чач алдырууга жазылуу",
        "help_cap3": "• ❌ Телефон номери боюнча жокко чыгаруу",
        "help_how": "📱 Кантип жазылуу:",
        "help_s1": "1. «Жазылуу» баскычын басыңыз",
        "help_s2": "2. Кызматты тандаңыз",
        "help_s3": "3. Күн жана убакытты тандаңыз",
        "help_s4": "4. Атыңызды жана телефонду жазыңыз",
        "help_s5": "5. Жазылууну ырастаңыз",
        "help_addr": "📍 Дарек: {addr}",
        "help_hours": "⏰ Убакыт: Күн сайын 9:00 – 21:00",
        "help_hosting": "🆓 Бот 24/7 JustRunMy.App иштейт",
        "map_title": "📍 Бизди кантип табуу",
        "map_addr": "🏠 Дарек:\n{addr}",
        "map_how": "🚗 Кантип баруу:",
        "map_stop1": "• «Советской Армии» аялдамасы — 5 мүн",
        "map_stop2": "• «Металлург» аялдамасы — 10 мүн",
        "map_hours": "⏰ Иш убактысы:\nКүн сайын 9:00 – 21:00",
        "map_phone": "📞 Телефон:\n{phone}",
        "map_btn": "🗺 Яндекс Карталарды ачуу",
        "cancel_title": "❌ Жазылууну жокко чыгаруу",
        "cancel_text": "Жазылууну жокко чыгаруу үчүн кайсы телефонго жазылганыңызды жазыңыз:\n\n<i>Мисалы: {phone}</i>",
        "cancel_done": "✅ Жазылуу жокко чыгарылды\n\nКүнү: {date}\nУбакты: {time}\n\nСизди кийинки жолу күтөбүз! ✂",
        "cancel_notfound": "❌ Жазылуу табылган жок\n\nБалким, ал буга чейин жокко чыгарылган.",
        "cancel_search_notfound": "❌ Жазылуулар табылган жок\n\n<b>{phone}</b> номери жазылууларда жок.\n\nНомерди текшериңиз же менюга кайтыңыз:",
        "cancel_found_title": "🔍 Табылган жазылуулар",
        "cancel_found_action": "Жокко чыгаруу үчүн жазылууну тандаңыз:",
        "cancel_btn": "❌ Жокко чыгаруу {date} {time}",
        "select_service_title": "💇 Кызматты тандаңыз",
        "select_service_hint": "Керектүү кызматты басыңыз:",
        "select_day_title": "📅 Күндү тандаңыз",
        "select_day_hint": "14 күн алдын жазылууга болот:",
        "today": "📌 Бүгүн",
        "tomorrow": "📌 Эртең",
        "select_time_title": "📅 {date} — убакыт тандоо",
        "select_time_free": "Бош: {free} / {total}",
        "select_time_hint": "Бош убакытты тандаңыз:",
        "slot_booked": "❌ {time} — {name}",
        "slot_free": "✅ {time}",
        "service_selected": "{emoji} {name}\n{desc}\n\n💰 Баасы: {price}\n\n📅 Жазылуу үчүн күндү тандаңыз:",
        "enter_name": "📝 Чач алдырууга жазылуу\n\n💇 Кызмат: {service}\n📅 Күн: {date}\n⏰ Убакыт: {time}\n\nАтыңызды жазыңыз:",
        "enter_phone": "📞 Телефон номериңизди жазыңыз\n\n<i>Мисалы: {phone}</i>",
        "name_error": "Сураныч, чыныгы атыңызды жазыңыз (кеминде 2 тамга):",
        "confirm_title": "📋 Маалыматты текшериңиз\n\n💇 Кызмат: {service}\n📅 Күн: {date}\n⏰ Убакыт: {time}\n👤 Аты: {name}\n📞 Телефон: {phone}\n\nБаары туурабы?",
        "confirm_ask": "✅ Ырастоо же ❌ Жокко чыгаруу баскычын басыңыз.",
        "booking_done": "✅ Сиз жазылдыңыз!\n\n💇 Кызмат: {service}\n📅 Күн: {date}\n⏰ Убакыт: {time}\n👤 Аты: {name}\n📞 Телефон: {phone}\n\n«Харизма»да күтөбүз! ✂\n\n📍 {addr}",
        "booking_cancelled": "❌ Жазылуу жокко чыгарылды\n\nКайра жазылгыңыз келсе — жазылыңыз!",
        "owner_new_booking": "✂ Жаңы жазылуу!\n\n💇 {service}\n📅 {date}\n⏰ {time}\n👤 {name}\n📞 {phone}\n🗺 {map_url}",
        "owner_cancelled": "❌ Кардар жазылууну жокко чыгарды\n\n📅 {date} {time} кезінде",
        "owner_reminder": "⏰ Эскертүү: 30 мүнөттөн кийин жазылуу\n\n💇 {service}\n📅 {date}\n⏰ {time}\n👤 {name}\n📞 {phone}\n\n<b>Кардар келдиби?</b>",
        "owner_confirm_yes": "✅ Келди",
        "owner_confirm_no": "❌ Келген жок",
        "owner_marked": "Чебер тарабынан белгиленди.",
        "unknown_cmd": "Мен сизди түшүнгөн жокмун. Буйруктарды колдонуңуз:\n\n<b>/start</b> — негизги меню\n<b>/services</b> — кызматтар жана баалар\n<b>/booking</b> — жазылуу\n<b>/help</b> — бот кантип иштейт",
        "choose_lang": "🌐 Выберите язык / Tilni tanlang / Тілді таңдаңыз / Тилди тандоо / Забонро интихоб кунед:",
        "lang_changed": "Тил Кыргыз тилине өзгөртүлдү 🇰🇬",
        "instagram_text": "📸 Биздин Instagram\n\nЖазылыңыз!",
        "instagram_btn": "📸 Instagram-ды ачуу",
    },
    "tj": {
        "lang_name": "Тоҷикӣ",
        "greeting": "Ман — барои сабт шудан ба барбершопи «Харизма» бот ҳастам.\nДар ин ҷо шумо метавонед нархҳоро фаҳмед, ба мошини\nмардона сабт шавед ё сабтро бекор кунед.",
        "addr_line": "📍 {addr}",
        "hours_line": "⏰ Ҳар рӯз 9:00 – 21:00",
        "phone_line": "📞 {phone}",
        "master_line": "💈 Устод: Баходир",
        "btn_about": "📖 Дар бораи мо",
        "btn_services": "💇 Хизматрасониҳо ва нархҳо",
        "btn_book": "📅 Сабт шудан",
        "btn_map": "📍 Чӣ тавр рафтан",
        "btn_cancel": "❌ Сабтро бекор кардан",
        "btn_help": "❓ Бот чӣ тавр кор мекунад",
        "btn_site": "🌐 Сомонаи мо",
        "btn_instagram": "📸 Instagram",
        "btn_back": "← Баргашт",
        "btn_back_menu": "← Ба меню",
        "btn_back_service": "← Ба интихоби хизмат",
        "btn_back_day": "← Ба интихоби рӯз",
        "btn_confirm": "✅ Тасдиқ",
        "btn_cancel_booking": "❌ Бекор кардан",
        "btn_lang": "🌐 Забон",
        "btn_book_now": "📅 Сабт шудан",
        "about_title": "📖 Дар бораи мо",
        "about_text1": "Барбершопи «Харизма» — ҷоест, ки услуби мардона ва хизмати босифат қадр карда мешавад.",
        "about_text2": "💈 Устод: Баха — таҷрибаи беш аз 5 сол.\nҲама чизро дар бораи мошини мардона, риш ва услуб медонад.",
        "about_why": "Чаро моро интихоб мекунанд:",
        "about_w1": "✦ Муносибати инфиродӣ ба ҳар як мизоҷ",
        "about_w2": "✦ Масолеҳ ва асбобҳои босифат",
        "about_w3": "✦ Фазои бароҳат ✨",
        "about_w4": "✦ Ҷойгиршавии қулай дар шаҳр",
        "about_w5": "✦ Бе рӯзҳои истироҳат кор мекунем 9:00 – 21:00",
        "about_what": "Мо чӣ пешниҳод мекунем:",
        "about_offer1": "✦ Мошини ҳар гуна мураккабӣ",
        "about_offer2": "✦ Тарроҳӣ ва ислоҳи риш",
        "about_offer3": "✦ Тонировкаи мӯй ва риш",
        "about_offer4": "✦ Мошин барои кӯдакон ва нафақахӯрон",
        "about_offer5": "✦ Аксияи «Падар + писар» — сарфаи 100 ₽",
        "about_outro": "Дар назди мо шумо метавонед истироҳат кунед ва бо боварии нав бароед. ✂",
        "services_title": "💇 Хизматрасониҳо ва нархҳо",
        "help_title": "❓ Бот чӣ тавр кор мекунад",
        "help_cap": "🤖 Имкониятҳо:",
        "help_cap1": "• 💇 Дидани хизматрасониҳо ва нархҳо",
        "help_cap2": "• 📅 Сабти онлайн ба мошини мардона",
        "help_cap3": "• ❌ Бекор кардани сабт бо рақами телефон",
        "help_how": "📱 Чӣ тавр сабт шудан:",
        "help_s1": "1. Тугмаи «Сабт шудан»-ро пахш кунед",
        "help_s2": "2. Хизматро интихоб кунед",
        "help_s3": "3. Рӯз ва вақтро интихоб кунед",
        "help_s4": "4. Ном ва телефонро ворид кунед",
        "help_s5": "5. Сабтро тасдиқ кунед",
        "help_addr": "📍 Суроға: {addr}",
        "help_hours": "⏰ Вақт: Ҳар рӯз 9:00 – 21:00",
        "help_hosting": "🆓 Бот 24/7 дар JustRunMy.app кор мекунад",
        "map_title": "📍 Моро чӣ тавр ёфтан",
        "map_addr": "🏠 Суроға:\n{addr}",
        "map_how": "🚗 Чӣ тавр рафтан:",
        "map_stop1": "• Истгоҳи «Советской Армии» — 5 дақ",
        "map_stop2": "• Истгоҳи «Металлург» — 10 дақ",
        "map_hours": "⏰ Вақти корӣ:\nҲар рӯз 9:00 – 21:00",
        "map_phone": "📞 Телефон:\n{phone}",
        "map_btn": "🗺 Харитаҳои Яндексро кушодан",
        "cancel_title": "❌ Бекор кардани сабт",
        "cancel_text": "Барои бекор кардани сабт, рақами телефоне, ки бо он сабт шудаед, ворид кунед:\n\n<i>Масалан: {phone}</i>",
        "cancel_done": "✅ Сабт бекор карда шуд\n\nСана: {date}\nВақт: {time}\n\nШуморо дафъаи дигар интизорем! ✂",
        "cancel_notfound": "❌ Сабт ёфт нашуд\n\nЭҳтимол, он аллакай бекор карда шудааст.",
        "cancel_search_notfound": "❌ Сабтҳо ёфт нашуд\n\nРақами <b>{phone}</b> дар сабтҳо нест.\n\nРақамро тафтиш кунед ё ба меню баргардед:",
        "cancel_found_title": "🔍 Сабтҳои ёфтшуда",
        "cancel_found_action": "Барои бекор кардан сабтро интихоб кунед:",
        "cancel_btn": "❌ Бекор кардан {date} {time}",
        "select_service_title": "💇 Хизматро интихоб кунед",
        "select_service_hint": "Хизмати дилхоҳро пахш кунед:",
        "select_day_title": "📅 Рӯзро интихоб кунед",
        "select_day_hint": "Сабт ба 14 рӯз пеш дастрас аст:",
        "today": "📌 Имрӯз",
        "tomorrow": "📌 Фардо",
        "select_time_title": "📅 {date} — интихоби вақт",
        "select_time_free": "Холӣ: {free} аз {total}",
        "select_time_hint": "Вақти холиро интихоб кунед:",
        "slot_booked": "❌ {time} — {name}",
        "slot_free": "✅ {time}",
        "service_selected": "{emoji} {name}\n{desc}\n\n💰 Нарх: {price}\n\n📅 Барои сабт рӯзро интихоб кунед:",
        "enter_name": "📝 Сабт ба мошини мардона\n\n💇 Хизмат: {service}\n📅 Сана: {date}\n⏰ Вақт: {time}\n\nНоми худро ворид кунед:",
        "enter_phone": "📞 Рақами телефони худро ворид кунед\n\n<i>Масалан: {phone}</i>",
        "name_error": "Илтимос, номи ҳақиқии худро ворид кунед (аз 2 ҳарф):",
        "confirm_title": "📋 Маълумотро тафтиш кунед\n\n💇 Хизмат: {service}\n📅 Сана: {date}\n⏰ Вақт: {time}\n👤 Ном: {name}\n📞 Телефон: {phone}\n\nҲама durust аст?",
        "confirm_ask": "Тугмаи ✅ Тасдиқ ё ❌ Бекор карданро пахш кунед.",
        "booking_done": "✅ Шумо сабт шудед!\n\n💇 Хизмат: {service}\n📅 Сана: {date}\n⏰ Вақт: {time}\n👤 Ном: {name}\n📞 Телефон: {phone}\n\nШуморо дар «Харизма» интизорем! ✂\n\n📍 {addr}",
        "booking_cancelled": "❌ Сабт бекор карда шуд\n\nАгар сабт шудан хоҳед — сабт шавед!",
        "owner_new_booking": "✂ Сабти нав!\n\n💇 {service}\n📅 {date}\n⏰ {time}\n👤 {name}\n📞 {phone}\n🗺 {map_url}",
        "owner_cancelled": "❌ Мизоҷ сабтро бекор кард\n\n📅 {date} соати {time}",
        "owner_reminder": "⏰ Ёдрасӣ: пас аз 30 дақиқа сабт\n\n💇 {service}\n📅 {date}\n⏰ {time}\n👤 {name}\n📞 {phone}\n\n<b>Мизоҷ омад?</b>",
        "owner_confirm_yes": "✅ Омад",
        "owner_confirm_no": "❌ Наомад",
        "owner_marked": "Аз ҷониби устод қайд карда шуд.",
        "unknown_cmd": "Ман шуморо нафаҳмидам. Фармонҳоро истифода баред:\n\n<b>/start</b> — менюи асосӣ\n<b>/services</b> — хизматрасониҳо ва нархҳо\n<b>/booking</b> — сабт шудан\n<b>/help</b> — бот чӣ тавр кор мекунад",
        "choose_lang": "🌐 Выберите язык / Tilni tanlang / Тілді таңдаңыз / Тилди тандоо / Забонро интихоб кунед:",
        "lang_changed": "Забон ба Тоҷикӣ иваз карда шуд 🇹🇯",
        "instagram_text": "📸 Instagram-и мо\n\nОбуна шавед!",
        "instagram_btn": "📸 Instagram-ро кушодан",
    },
}

LANG_CODES = ["ru", "uz", "kz", "kg", "tj"]
LANG_NAMES = {"ru": "🇷🇺 Русский", "uz": "🇺🇿 O'zbek", "kz": "🇰🇿 Қазақ", "kg": "🇰🇬 Кыргыз", "tj": "🇹🇯 Тоҷикӣ"}

def load_languages():
    if not os.path.exists(LANGUAGES_FILE):
        return {}
    try:
        with open(LANGUAGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_languages(data):
    with open(LANGUAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_lang(chat_id, context):
    persisted = load_languages()
    if str(chat_id) in persisted:
        return persisted[str(chat_id)]
    lang = context.user_data.get("lang", "ru")
    return lang

def set_user_lang(chat_id, lang, context):
    context.user_data["lang"] = lang
    data = load_languages()
    data[str(chat_id)] = lang
    save_languages(data)

def _(key, chat_id=None, context=None, **kwargs):
    lang = "ru"
    if chat_id and context:
        lang = get_user_lang(chat_id, context)
    elif context:
        lang = context.user_data.get("lang", "ru")
    if lang not in TR:
        lang = "ru"
    text = TR[lang].get(key, TR["ru"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text

def load_bookings():
    if not os.path.exists(BOOKINGS_FILE):
        return {}
    try:
        with open(BOOKINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_bookings(bookings):
    with open(BOOKINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(bookings, f, ensure_ascii=False, indent=2)

def get_available_days():
    days = []
    today = date.today()
    for i in range(14):
        d = today + timedelta(days=i)
        days.append(d)
    return days

def get_time_slots():
    slots = []
    for h in range(WORK_START, WORK_END + 1):
        slots.append(f"{h:02d}:00")
    return slots

def get_greeting():
    h = datetime.now().hour
    if 5 <= h < 12:
        return GREETINGS["morning"]
    elif 12 <= h < 17:
        return GREETINGS["afternoon"]
    elif 17 <= h < 23:
        return GREETINGS["evening"]
    else:
        return GREETINGS["night"]

async def cleanup_last(chat_id, context):
    bot_id = context.user_data.get("last_bot_msg_id")
    user_id = context.user_data.get("last_user_msg_id")
    if user_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=user_id)
        except Exception:
            pass
    if bot_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=bot_id)
        except Exception:
            pass

DIV = "━" * 20
DIV_THIN = "─" * 20

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    greeting = get_greeting()
    text = (
        f"✂ <b>Харизма | Барбершоп</b> ✂\n"
        f"{DIV}\n\n"
        f"{greeting}\n\n"
        f"{_('greeting', chat_id, context)}\n\n"
        f"{_('addr_line', chat_id, context, addr=ADDRESS)}\n"
        f"{_('hours_line', chat_id, context)}\n"
        f"{_('phone_line', chat_id, context, phone=PHONE)}\n"
        f"{_('master_line', chat_id, context)}\n\n"
        f"{DIV}"
    )
    keyboard = [
        [InlineKeyboardButton(_("btn_about", chat_id, context), callback_data="menu_about")],
        [InlineKeyboardButton(_("btn_services", chat_id, context), callback_data="menu_services")],
        [InlineKeyboardButton(_("btn_book", chat_id, context), callback_data="menu_book")],
        [InlineKeyboardButton(_("btn_map", chat_id, context), callback_data="menu_map")],
        [InlineKeyboardButton(_("btn_cancel", chat_id, context), callback_data="menu_cancel")],
        [InlineKeyboardButton(_("btn_help", chat_id, context), callback_data="menu_help")],
        [InlineKeyboardButton(_("btn_site", chat_id, context), url=SITE_URL), InlineKeyboardButton(_("btn_instagram", chat_id, context), url=INSTAGRAM_URL)],
        [InlineKeyboardButton(_("btn_lang", chat_id, context), callback_data="menu_lang")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = (
        f"{_('about_title', chat_id, context)}\n"
        f"{DIV}\n\n"
        f"{_('about_text1', chat_id, context)}\n\n"
        f"{_('about_text2', chat_id, context)}\n\n"
        f"{_('about_why', chat_id, context)}\n"
        f"{_('about_w1', chat_id, context)}\n"
        f"{_('about_w2', chat_id, context)}\n"
        f"{_('about_w3', chat_id, context)}\n"
        f"{_('about_w4', chat_id, context)}\n"
        f"{_('about_w5', chat_id, context)}\n\n"
        f"{_('about_what', chat_id, context)}\n"
        f"{_('about_offer1', chat_id, context)}\n"
        f"{_('about_offer2', chat_id, context)}\n"
        f"{_('about_offer3', chat_id, context)}\n"
        f"{_('about_offer4', chat_id, context)}\n"
        f"{_('about_offer5', chat_id, context)}\n\n"
        f"{_('about_outro', chat_id, context)}\n\n"
        f"{DIV}\n"
        f"{_('addr_line', chat_id, context, addr=ADDRESS)}\n"
        f"{_('hours_line', chat_id, context)}\n"
        f"{_('phone_line', chat_id, context, phone=PHONE)}\n"
        f"🌐 <a href='{SITE_URL}'>{_('btn_site', chat_id, context)}</a>\n"
        f"📸 <a href='{INSTAGRAM_URL}'>{_('btn_instagram', chat_id, context)}</a>"
    )
    keyboard = [[InlineKeyboardButton(_("btn_back", chat_id, context), callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = f"{_('services_title', chat_id, context)}\n{DIV}\n\n"
    for key, service in SERVICES.items():
        text += f"{service['emoji']} <b>{service['name']}</b>\n   └ {service['desc']}\n   └ 💰 {service['price']}\n\n"
    text += f"{DIV}"
    keyboard = [[InlineKeyboardButton(_("btn_book_now", chat_id, context), callback_data="menu_book")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")

async def show_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    keyboard = []
    for code in LANG_CODES:
        label = LANG_NAMES[code]
        keyboard.append([InlineKeyboardButton(label, callback_data=f"lang_{code}")])
    keyboard.append([InlineKeyboardButton(_("btn_back", chat_id, context), callback_data="back_to_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        _("choose_lang", chat_id, context),
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = update.effective_chat.id

    if data.startswith("lang_"):
        lang = data.replace("lang_", "")
        set_user_lang(chat_id, lang, context)
        await show_languages(update, context)
        await context.bot.send_message(
            chat_id=chat_id,
            text=_("lang_changed", chat_id, context)
        )
        return

    if data == "menu_lang":
        await show_languages(update, context)
        return

    if data == "menu_about":
        await about(update, context)
        return

    elif data == "menu_services":
        await services(update, context)

    elif data == "menu_book":
        await show_services_for_booking(update, context)

    elif data == "menu_map":
        keyboard = [
            [InlineKeyboardButton(_("map_btn", chat_id, context), url=MAP_URL)],
            [InlineKeyboardButton(_("btn_back", chat_id, context), callback_data="back_to_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"{_('map_title', chat_id, context)}\n{DIV}\n\n"
            f"{_('map_addr', chat_id, context, addr=ADDRESS)}\n\n"
            f"{_('map_how', chat_id, context)}\n"
            f"{_('map_stop1', chat_id, context)}\n"
            f"{_('map_stop2', chat_id, context)}\n\n"
            f"{_('map_hours', chat_id, context)}\n\n"
            f"{_('map_phone', chat_id, context, phone=PHONE)}\n\n{DIV}",
            reply_markup=reply_markup, parse_mode="HTML"
        )

    elif data == "menu_help":
        keyboard = [[InlineKeyboardButton(_("btn_back", chat_id, context), callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"{_('help_title', chat_id, context)}\n{DIV}\n\n"
            f"{_('help_cap', chat_id, context)}\n"
            f"{_('help_cap1', chat_id, context)}\n"
            f"{_('help_cap2', chat_id, context)}\n"
            f"{_('help_cap3', chat_id, context)}\n\n"
            f"{_('help_how', chat_id, context)}\n"
            f"{_('help_s1', chat_id, context)}\n"
            f"{_('help_s2', chat_id, context)}\n"
            f"{_('help_s3', chat_id, context)}\n"
            f"{_('help_s4', chat_id, context)}\n"
            f"{_('help_s5', chat_id, context)}\n\n"
            f"{_('help_addr', chat_id, context, addr=ADDRESS)}\n"
            f"{_('help_hours', chat_id, context)}\n\n"
            f"{DIV_THIN}\n\n"
            f"{_('help_hosting', chat_id, context)}",
            reply_markup=reply_markup, parse_mode="HTML"
        )

    elif data == "menu_cancel":
        context.user_data["step"] = "waiting_cancel_phone"
        await query.edit_message_text(
            f"{_('cancel_title', chat_id, context)}\n{DIV}\n\n"
            f"{_('cancel_text', chat_id, context, phone=PHONE)}",
            parse_mode="HTML"
        )

    elif data == "back_to_menu":
        await start(update, context)

    elif data.startswith("serv_"):
        service_key = data.replace("serv_", "")
        context.user_data["selected_service"] = service_key
        await show_days(query, context)

    elif data.startswith("day_"):
        selected_date = data.replace("day_", "")
        context.user_data["selected_date"] = selected_date
        await show_times(query, selected_date, context)

    elif data.startswith("time_"):
        selected_time = data.replace("time_", "")
        selected_date = context.user_data.get("selected_date")
        service_key = context.user_data.get("selected_service", "")
        context.user_data["selected_time"] = selected_time
        context.user_data["step"] = "waiting_name"
        service_name = SERVICES.get(service_key, {}).get("name", "—")
        await query.edit_message_text(
            _("enter_name", chat_id, context, service=service_name, date=selected_date, time=selected_time),
            parse_mode="HTML"
        )

    elif data == "back_to_days":
        await show_days(query, context)

    elif data.startswith("del_"):
        parts = data.split("_", 2)
        if len(parts) == 3:
            date_key = parts[1]
            time_key = parts[2]
            bookings = load_bookings()
            if date_key in bookings and time_key in bookings[date_key]:
                del bookings[date_key][time_key]
                if not bookings[date_key]:
                    del bookings[date_key]
                save_bookings(bookings)
                await query.edit_message_text(
                    _("cancel_done", chat_id, context, date=date_key, time=time_key),
                    parse_mode="HTML"
                )
                await context.bot.send_message(
                    chat_id=OWNER_ID,
                    text=f"\u274c <b>\u0417\u0430\u043f\u0438\u0441\u044c \u043e\u0442\u043c\u0435\u043d\u0435\u043d\u0430 \u043a\u043b\u0438\u0435\u043d\u0442\u043e\u043c</b>\n{DIV_THIN}\n\U0001f4c5 {date_key} \u0432 {time_key}",
                    parse_mode="HTML"
                )
            else:
                await query.edit_message_text(
                    _("cancel_notfound", chat_id, context),
                    parse_mode="HTML"
                )

    elif data == "confirm_booking":
        name = context.user_data.get("client_name", "")
        phone = context.user_data.get("client_phone", "")
        selected_date = context.user_data.get("selected_date", "")
        selected_time = context.user_data.get("selected_time", "")
        service_key = context.user_data.get("selected_service", "")
        service_name = SERVICES.get(service_key, {}).get("name", "—")
        bookings = load_bookings()
        if selected_date not in bookings:
            bookings[selected_date] = {}
        bookings[selected_date][selected_time] = {
            "name": name, "phone": phone, "service": service_name,
            "created_at": datetime.now().isoformat()
        }
        save_bookings(bookings)
        context.user_data["step"] = None
        await query.edit_message_text(
            _("booking_done", chat_id, context, service=service_name, date=selected_date, time=selected_time, name=name, phone=phone, addr=ADDRESS),
            parse_mode="HTML"
        )
        owner_text = (
            f"\u2702 <b>\u041d\u043e\u0432\u0430\u044f \u0437\u0430\u043f\u0438\u0441\u044c!</b>\n{DIV}\n\n"
            f"\U0001f487 {service_name}\n\U0001f4c5 {selected_date}\n\u23f0 {selected_time}\n\U0001f464 {name}\n\U0001f4de {phone}\n{DIV}\n\U0001f5fa {MAP_URL}"
        )
        await context.bot.send_message(chat_id=OWNER_ID, text=owner_text, parse_mode="HTML")
        try:
            await schedule_reminder(context.application, selected_date, selected_time, service_name, name, phone)
        except Exception as e:
            logger.error(f"Reminder error: {e}")

    elif data == "cancel_booking":
        context.user_data["step"] = None
        keyboard = [[InlineKeyboardButton(_("btn_back_menu", chat_id, context), callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            _("booking_cancelled", chat_id, context),
            reply_markup=reply_markup, parse_mode="HTML"
        )

    elif data.startswith("confirm_"):
        parts = data.split("_")
        if len(parts) == 4:
            _, cdate, ctime, answer = parts
            label = _("owner_confirm_yes", chat_id, context) if answer == "yes" else _("owner_confirm_no", chat_id, context)
            await query.edit_message_text(
                f"{label}\n{DIV}\n\n{cdate} в {ctime}\n\n{_('owner_marked', chat_id, context)}",
                parse_mode="HTML"
            )

    elif data == "none":
        pass

async def menu_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    context.user_data["step"] = None
    text = (
        f"{_('help_title', chat_id, context)}\n{DIV}\n\n"
        f"{_('help_cap', chat_id, context)}\n"
        f"{_('help_cap1', chat_id, context)}\n"
        f"{_('help_cap2', chat_id, context)}\n"
        f"{_('help_cap3', chat_id, context)}\n\n"
        f"{_('help_how', chat_id, context)}\n"
        f"{_('help_s1', chat_id, context)}\n"
        f"{_('help_s2', chat_id, context)}\n"
        f"{_('help_s3', chat_id, context)}\n"
        f"{_('help_s4', chat_id, context)}\n"
        f"{_('help_s5', chat_id, context)}\n\n"
        f"{_('help_addr', chat_id, context, addr=ADDRESS)}\n"
        f"{_('help_hours', chat_id, context)}\n\n"
        f"{DIV_THIN}\n\n"
        f"{_('help_hosting', chat_id, context)}"
    )
    await update.message.reply_text(text, parse_mode="HTML")

async def show_services_for_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = f"{_('select_service_title', chat_id, context)}\n{DIV}\n\n{_('select_service_hint', chat_id, context)}"
    keyboard = []
    for key, service in SERVICES.items():
        keyboard.append([InlineKeyboardButton(
            f"{service['emoji']} {service['name']} — {service['price']}",
            callback_data=f"serv_{key}"
        )])
    keyboard.append([InlineKeyboardButton(_("btn_back", chat_id, context), callback_data="back_to_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")

async def show_days(query, context):
    chat_id = query.message.chat_id
    days = get_available_days()
    keyboard = []
    row = []
    for i, d in enumerate(days):
        if d == date.today():
            label = _("today", chat_id, context)
        elif d == date.today() + timedelta(days=1):
            label = _("tomorrow", chat_id, context)
        else:
            label = f"{d.day} {MONTHS[d.month]}"
        callback = f"day_{d.isoformat()}"
        row.append(InlineKeyboardButton(label, callback_data=callback))
        if len(row) == 2 or i == len(days) - 1:
            keyboard.append(row)
            row = []
    keyboard.append([InlineKeyboardButton(_("btn_back_service", chat_id, context), callback_data="menu_book")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        f"{_('select_day_title', chat_id, context)}\n{DIV}\n\n{_('select_day_hint', chat_id, context)}",
        reply_markup=reply_markup, parse_mode="HTML"
    )

async def show_times(query, selected_date, context):
    chat_id = query.message.chat_id
    bookings = load_bookings()
    day_bookings = bookings.get(selected_date, {})
    slots = get_time_slots()
    keyboard = []
    d = date.fromisoformat(selected_date)
    today = date.today()
    if d == today:
        date_label = _("today", chat_id, context)
    elif d == today + timedelta(days=1):
        date_label = _("tomorrow", chat_id, context)
    else:
        date_label = f"{d.day} {MONTHS.get(d.month, '')}"
    for slot in slots:
        if slot in day_bookings:
            client_info = day_bookings[slot]
            label = _("slot_booked", chat_id, context, time=slot, name=client_info.get('name', 'занято'))
            keyboard.append([InlineKeyboardButton(label, callback_data="none")])
        else:
            label = _("slot_free", chat_id, context, time=slot)
            keyboard.append([InlineKeyboardButton(label, callback_data=f"time_{slot}")])
    keyboard.append([InlineKeyboardButton(_("btn_back_day", chat_id, context), callback_data="back_to_days")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    free_slots = sum(1 for s in slots if s not in day_bookings)
    await query.edit_message_text(
        f"{_('select_time_title', chat_id, context, date=date_label)}\n{DIV}\n\n"
        f"{_('select_time_free', chat_id, context, free=free_slots, total=len(slots))}\n"
        f"{DIV_THIN}\n\n{_('select_time_hint', chat_id, context)}",
        reply_markup=reply_markup, parse_mode="HTML"
    )

async def schedule_reminder(app, selected_date, selected_time, service_name, client_name, client_phone):
    try:
        parts = selected_time.split(":")
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
        d = date.fromisoformat(selected_date)
        reminder_dt = datetime(d.year, d.month, d.day, hour, minute) - timedelta(minutes=30)
        now = datetime.now()
        delay = (reminder_dt - now).total_seconds()
        if delay < 0:
            return
        app.job_queue.run_once(
            send_reminder, delay,
            data={"date": selected_date, "time": selected_time, "service": service_name, "name": client_name, "phone": client_phone},
            name=f"reminder_{selected_date}_{selected_time}"
        )
    except Exception as e:
        logger.error(f"Reminder schedule error: {e}")

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    keyboard = [
        [InlineKeyboardButton("✅ Пришёл", callback_data=f"confirm_{data['date']}_{data['time']}_yes")],
        [InlineKeyboardButton("❌ Не пришёл", callback_data=f"confirm_{data['date']}_{data['time']}_no")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=(
            f"⏰ <b>Напоминание: через 30 мин запись</b>\n{DIV}\n\n"
            f"💇 {data['service']}\n📅 {data['date']}\n⏰ {data['time']}\n"
            f"👤 {data['name']}\n📞 {data['phone']}\n\n<b>Клиент пришёл?</b>"
        ),
        reply_markup=reply_markup, parse_mode="HTML"
    )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    step = context.user_data.get("step")

    if step == "waiting_name":
        name = update.message.text.strip()
        if len(name) < 2:
            msg = await update.message.reply_text(_("name_error", chat_id, context))
            context.user_data["last_bot_msg_id"] = msg.message_id
            return
        context.user_data["client_name"] = name
        context.user_data["step"] = "waiting_phone"
        await cleanup_last(chat_id, context)
        msg = await update.message.reply_text(
            _("enter_phone", chat_id, context, phone=PHONE),
            parse_mode="HTML"
        )
        context.user_data["last_bot_msg_id"] = msg.message_id

    elif step == "waiting_phone":
        phone = update.message.text.strip()
        name = context.user_data.get("client_name", "")
        selected_date = context.user_data.get("selected_date", "")
        selected_time = context.user_data.get("selected_time", "")
        service_key = context.user_data.get("selected_service", "")
        service_name = SERVICES.get(service_key, {}).get("name", "—")
        context.user_data["client_phone"] = phone
        context.user_data["step"] = "confirm"
        await cleanup_last(chat_id, context)
        keyboard = [
            [InlineKeyboardButton(_("btn_confirm", chat_id, context), callback_data="confirm_booking")],
            [InlineKeyboardButton(_("btn_cancel_booking", chat_id, context), callback_data="cancel_booking")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            _("confirm_title", chat_id, context, service=service_name, date=selected_date, time=selected_time, name=name, phone=phone),
            reply_markup=reply_markup, parse_mode="HTML"
        )

    elif step == "waiting_cancel_phone":
        phone = update.message.text.strip()
        bookings = load_bookings()
        found = []
        for date_key, slots in bookings.items():
            for time_key, client in list(slots.items()):
                if client.get("phone", "") == phone:
                    found.append((date_key, time_key, client))
        if not found:
            await update.message.reply_text(
                _("cancel_search_notfound", chat_id, context, phone=phone),
                parse_mode="HTML"
            )
            keyboard = [[InlineKeyboardButton(_("btn_back_menu", chat_id, context), callback_data="back_to_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(_("select_service_hint", chat_id, context), reply_markup=reply_markup)
            context.user_data["step"] = None
            return
        text = f"{_('cancel_found_title', chat_id, context)}\n{DIV}\n\n"
        keyboard = []
        for date_key, time_key, client in found:
            service = client.get("service", "—")
            text += f"📅 <b>{date_key}</b> в <b>{time_key}</b>\n💇 {service}\n\n"
            keyboard.append([InlineKeyboardButton(
                _("cancel_btn", chat_id, context, date=date_key, time=time_key),
                callback_data=f"del_{date_key}_{time_key}"
            )])
        text += f"{DIV_THIN}\n\n{_('cancel_found_action', chat_id, context)}"
        keyboard.append([InlineKeyboardButton(_("btn_back_menu", chat_id, context), callback_data="back_to_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data["step"] = None
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")

    elif step == "confirm":
        await update.message.reply_text(_("confirm_ask", chat_id, context))

    else:
        t = update.message.text.lower().strip()
        if t in ["запуск", "меню", "menu", "start"]:
            await start(update, context)
        elif t in ["услуги", "цены", "services"]:
            await services(update, context)
        elif t in ["about", "о нас"]:
            await about(update, context)
        elif t in ["запись", "book", "записаться"]:
            await show_services_for_booking(update, context)
        elif t in ["help", "помощь", "инструкция", "как"]:
            context.user_data["step"] = None
            await menu_help_command(update, context)
        elif t in ["instagram", "инстаграм"]:
            keyboard = [[InlineKeyboardButton(_("instagram_btn", chat_id, context), url=INSTAGRAM_URL)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                _("instagram_text", chat_id, context), reply_markup=reply_markup, parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                _("unknown_cmd", chat_id, context), parse_mode="HTML"
            )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler(["start", "menu"], start))
    app.add_handler(CommandHandler(["services", "service"], services))
    app.add_handler(CommandHandler(["book", "booking"], show_services_for_booking))
    app.add_handler(CommandHandler(["help", "howto"], menu_help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_error_handler(error_handler)
    print("Бот Харизма запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
