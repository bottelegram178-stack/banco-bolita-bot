import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime

# ==================== CONFIGURACIÓN ====================
TOKEN = "TU_TOKEN_AQUI"  # Reemplaza esto con el token de tu bot de BotFather
ADMIN_ID = 123456789     # Reemplaza con tu ID de Telegram de administrador

bot = telebot.TeleBot(TOKEN)

# Diccionario temporal para guardar apuestas antes de confirmarlas
temp_apuestas = {}

# ==================== MENÚ PRINCIPAL ====================
@bot.message_handler(commands=['start'])
def enviar_bienvenida(message):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎲 Jugar Fijo", callback_data="jugar_fijo"),
        InlineKeyboardButton("🚂 Jugar Corrido", callback_data="jugar_corrido")
    )
    markup.row(
        InlineKeyboardButton("🔗 Jugar Palé", callback_data="jugar_pale"),
        InlineKeyboardButton("📊 Ver Mis Jugadas", callback_data="ver_jugadas")
    )
    
    if message.from_user.id == ADMIN_ID:
        markup.row(InlineKeyboardButton("👑 Panel Admin", callback_data="panel_admin"))

    texto = (
        "<b>🏦 BIENVENIDO A EMPIRE BANCA 🏦</b>\n\n"
        "Tu sistema seguro para realizar jugadas de la bolita.\n"
        "Selecciona una opción del menú para comenzar:"
    )
    bot.send_message(message.chat.id, texto, parse_mode="HTML", reply_markup=markup)

# ==================== CALLBACKS Y LÓGICA ====================
@bot.callback_query_handler(func=lambda call: True)
def manejar_botones(call):
    user_id = call.from_user.id
    
    if call.data == "jugar_fijo":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "✏️ Envía tu jugada en formato: <code>Número Importe</code>\nEjemplo: <code>45 100</code>", parse_mode="HTML")
        bot.register_next_step_handler(msg, procesar_fijo)

@bot.callback_query_handler(func=lambda call: call.data == "panel_admin")
def panel_admin(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "⚠️ No tienes permisos de administrador.", show_alert=True)
        return
    
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("📈 Reporte del Día", callback_data="admin_reporte"))
    markup.row(InlineKeyboardButton("🔙 Volver", callback_data="menu_principal"))
    
    bot.edit_message_text(
        "<b>👑 PANEL DE ADMINISTRACIÓN 👑</b>\n\nElige una opción de control:",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
        reply_markup=markup
    )

def procesar_fijo(message):
    try:
        partes = message.text.split()
        numero = partes[0]
        importe = float(partes[1])
        
        if len(numero) != 2:
            bot.send_message(message.chat.id, "❌ El Fijo debe ser de 2 dígitos. Intenta de nuevo con /start")
            return

        # Generación del ticket con el formato estético solicitado
        fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        ticket_id = f"EB-{datetime.datetime.now().strftime('%H%M%S')}"

        ticket_texto = (
            f"🎟 <b>TICKET DE JUGADA - EMPIRE BANCA</b> 🎟\n"
            f"──────────────────\n"
            f"🆔 <b>Ticket:</b> <code>{ticket_id}</code>\n"
            f"👤 <b>Jugador:</b> {message.from_user.first_name}\n"
            f"📅 <b>Fecha:</b> {fecha_actual}\n"
            f"──────────────────\n"
            f"📌 <b>Modalidad:</b> Fijo\n"
            f"🔢 <b>Jugada:</b> <code>{numero}</code>\n"
            f"💰 <b>Importe:</b> ${importe:.2f}\n"
            f"──────────────────\n"
            f"✅ <i>Apuesta registrada con éxito</i>"
        )
        
        bot.send_message(message.chat.id, ticket_texto, parse_mode="HTML")
        
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Formato incorrecto. Asegúrate de enviar número y monto (Ej: 45 100).")

# ==================== INICIO DEL BOT ====================
if __name__ == "__main__":
    print("Bot iniciado correctamente y listo para operar...")
    bot.infinity_polling()
