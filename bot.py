import os
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# إعداد قاعدة البيانات وتجدولها
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

# أمر البدء للترحيب بالمستخدم
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً بك! أنا بوت إدارة المبيعات والتقارير.\n\n"
        "• أرسل قيمة المبيعات كرسالة نصية (مثال: `250`) لتسجيلها في السجل.\n"
        "• يمكنك إرسال صور الفواتير أو المنتجات وسأستقبلها.\n"
        "• استخدم الأمر /weekly_report لعرض التقرير الأسبوعي والرسوم البيانية."
    )

# معالجة النصوص والصور المدخلة
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        await update.message.reply_text("📷 تم استقبال الصورة بنجاح! (يمكنك إرسال قيمة المبيعات المرتبطة بها كرقم نصي لتسجيلها).")
        return

    text = update.message.text
    try:
        amount = float(text)
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect('sales.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sales (amount, date) VALUES (?, ?)", (amount, date_str))
        conn.commit()
        conn.close()
        
        await update.message.reply_text(f"✅ تم تسجيل مبلغ المبيعات: `{amount}` بنجاح!")
    except ValueError:
        await update.message.reply_text("⚠️ يرجى إرسال رقم صحيح يمثل قيمة المبيعات أو استخدام الأوامر المتاحة.")

# أمر توليد تقرير الأسبوع
async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📊 عرض الرسوم والإحصائيات الأسبوعية", callback_data="weekly_report")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اضغط على الزر أدناه لمعرفة إحصائيات المبيعات خلال الأسبوع الماضي:", reply_markup=reply_markup)

# معالجة الضغط على الزر وإنشاء الرسوم البيانية
async def weekly_report_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    
    # جلب بيانات الأيام السبعة الأخيرة
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    cursor.execute("SELECT date, SUM(amount) FROM sales WHERE date >= ? GROUP BY date ORDER BY date ASC", (seven_days_ago,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        await query.edit_message_text("❌ لا توجد بيانات مبيعات مسجلة خلال الأسبوع الماضي.")
        return

    dates = [row[0] for row in rows]
    amounts = [row[1] for row in rows]
    
    # تحديد أكبر وأقل يوم بيع
    max_sale = max(amounts)
    min_sale = min(amounts)
    max_day = dates[amounts.index(max_sale)]
    min_day = dates[amounts.index(min_sale)]
    
    # تصميم الرسم البياني المانع للأخطاء والمنظم
    plt.figure(figsize=(9, 5))
    plt.plot(dates, amounts, marker='o', color='#2b5c8f', linestyle='-', linewidth=2.5, markersize=8, label='المبيعات اليومية')
    plt.title('منحنى المبيعات الأسبوعي', fontsize=14, fontweight='bold')
    plt.xlabel('التاريخ', fontsize=12)
    plt.ylabel('المبلغ', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    # حفظ الرسم البياني في الذاكرة المؤقتة للإرسال المباشر
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    report_text = (
        f"📈 **التقرير الإحصائي الأسبوعي للمبيعات:**\n\n"
        f"🔥 **أكبر يوم تم البيع فيه:** يوم `{max_day}` بإجمالي مبيعات `{max_sale}`\n"
        f"📉 **أقل يوم تم البيع فيه:** يوم `{min_day}` بإجمالي مبيعات `{min_sale}`\n"
    )
    
    await query.message.reply_photo(photo=buf, caption=report_text, parse_mode='Markdown')

# دالة التشغيل الرئيسية
def main():
    token = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weekly_report", report_command))
    app.add_handler(CallbackQueryHandler(weekly_report_callback, pattern="weekly_report"))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND) | filters.PHOTO, handle_message))
    
    print("البوت يعمل الآن بكفاءة...")
    app.run_polling()

if __name__ == "__main__":
    main()
