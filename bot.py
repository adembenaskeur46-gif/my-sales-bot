import os
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

def init_db():
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

async def start(command_context: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = command_context.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("📊 تقرير الأسبوع", callback_data="weekly_report")],
        [InlineKeyboardButton("↩️ حذف آخر إدخال", callback_data="undo_last")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await command_context.message.reply_text(
        f"أهلاً بك يا {user_name} في بوت إدارة الأرباح! 💰\n\n"
        "فقط قم بإرسال **قيمة البيع** اليومية مباشرة كـ رقم (مثلاً: `500` أو `120.5`) وسأقوم بتسجيلها تلقائياً.\n\n"
        "يمكنك استخدام الأزرار أدناه أو الأوامر:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_sale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        amount = float(text)
        today_date = datetime.now().strftime("%Y-%m-%d %H:%M")

        conn = sqlite3.connect('sales.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sales (amount, date) VALUES (?, ?)", (amount, today_date))
        conn.commit()
        conn.close()

        await update.message.reply_text(f"✅ تم تسجيل مبلغ: **{amount}** بنجاح!\nالتاريخ: {today_date}", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("⚠️ أرجو إرسال رقم صحيح يمثل قيمة البيع فقط (مثلاً: `350`).")

async def weekly_report_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    cursor.execute("SELECT amount, date FROM sales ORDER BY id DESC LIMIT 7")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await query.edit_message_text("📭 لا توجد مبيعات مسجلة حتى الآن.")
        return

    total = sum(row[0] for row in rows)
    average = total / len(rows)
    max_sale = max(rows, key=lambda x: x[0])

    report = "📈 **تقرير الأرباح (آخر الإدخالات الأسبوعية):**\n\n"
    for amount, date in rows:
        report += f"• {date}: **{amount}**\n"

    report += f"\n-------------------\n"
    report += f"💰 **المجموع:** {total}\n"
    report += f"📊 **المتوسط اليومي:** {average:.2f}\n"
    report += f"🔥 **الأعلى مبيعاً:** {max_sale[0]} (بتاريخ {max_sale[1]})\n"

    await query.edit_message_text(report, parse_mode="Markdown")

async def undo_last_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, amount, date FROM sales ORDER BY id DESC LIMIT 1")
    last = cursor.fetchone()

    if last:
        cursor.execute("DELETE FROM sales WHERE id = ?", (last[0],))
        conn.commit()
        conn.close()
        await query.edit_message_text(f"🗑️ تم حذف آخر إدخال بنجاح:\nالمبلغ: {last[1]} بتاريخ {last[2]}")
    else:
        conn.close()
        await query.edit_message_text("⚠️ لا توجد أي سجلات لحذفها.")

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(weekly_report_callback, pattern="weekly_report"))
    app.add_handler(CallbackQueryHandler(undo_last_callback, pattern="undo_last"))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_sale))

    print("🤖 البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()import os
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

def init_db():
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

async def start(command_context: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = command_context.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("📊 تقرير الأسبوع", callback_data="weekly_report")],
        [InlineKeyboardButton("↩️ حذف آخر إدخال", callback_data="undo_last")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await command_context.message.reply_text(
        f"أهلاً بك يا {user_name} في بوت إدارة الأرباح! 💰\n\n"
        "فقط قم بإرسال **قيمة البيع** اليومية مباشرة كـ رقم (مثلاً: `500` أو `120.5`) وسأقوم بتسجيلها تلقائياً.\n\n"
        "يمكنك استخدام الأزرار أدناه أو الأوامر:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_sale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        amount = float(text)
        today_date = datetime.now().strftime("%Y-%m-%d %H:%M")

        conn = sqlite3.connect('sales.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sales (amount, date) VALUES (?, ?)", (amount, today_date))
        conn.commit()
        conn.close()

        await update.message.reply_text(f"✅ تم تسجيل مبلغ: **{amount}** بنجاح!\nالتاريخ: {today_date}", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("⚠️ أرجو إرسال رقم صحيح يمثل قيمة البيع فقط (مثلاً: `350`).")

async def weekly_report_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    cursor.execute("SELECT amount, date FROM sales ORDER BY id DESC LIMIT 7")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await query.edit_message_text("📭 لا توجد مبيعات مسجلة حتى الآن.")
        return

    total = sum(row[0] for row in rows)
    average = total / len(rows)
    max_sale = max(rows, key=lambda x: x[0])

    report = "📈 **تقرير الأرباح (آخر الإدخالات الأسبوعية):**\n\n"
    for amount, date in rows:
        report += f"• {date}: **{amount}**\n"

    report += f"\n-------------------\n"
    report += f"💰 **المجموع:** {total}\n"
    report += f"📊 **المتوسط اليومي:** {average:.2f}\n"
    report += f"🔥 **الأعلى مبيعاً:** {max_sale[0]} (بتاريخ {max_sale[1]})\n"

    await query.edit_message_text(report, parse_mode="Markdown")

async def undo_last_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, amount, date FROM sales ORDER BY id DESC LIMIT 1")
    last = cursor.fetchone()

    if last:
        cursor.execute("DELETE FROM sales WHERE id = ?", (last[0],))
        conn.commit()
        conn.close()
        await query.edit_message_text(f"🗑️ تم حذف آخر إدخال بنجاح:\nالمبلغ: {last[1]} بتاريخ {last[2]}")
    else:
        conn.close()
        await query.edit_message_text("⚠️ لا توجد أي سجلات لحذفها.")

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(weekly_report_callback, pattern="weekly_report"))
    app.add_handler(CallbackQueryHandler(undo_last_callback, pattern="undo_last"))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_sale))

    print("🤖 البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()