import sys
from telegram import Bot
import os
import asyncio

# التوكين الخاص بالبوت
TOKEN = '7950203407:AAFCUHikOHiPdGXfOAbwb73VZHVeWIanBYA'
bot = Bot(token=TOKEN)

# قراءة مسارات الملفات من سطر الأوامر
files_to_upload = sys.argv[1:]

# معرف المجموعة
chat_id = '-4691420226'

# دالة غير متزامنة لإرسال الصورة إلى تليجرام
async def send_photo_to_telegram(file_path):
    try:
        with open(file_path, 'rb') as photo:
            message = await bot.send_photo(chat_id=chat_id, photo=photo, caption=os.path.basename(file_path))
            print(f"Photo {file_path} sent successfully!")
            with open('id.txt', 'a') as f:
                f.write(f"{message.message_id}\n")
        # حذف الصورة بعد إرسالها بنجاح
        os.remove(file_path)
        print(f"Photo {file_path} deleted successfully!")
    except Exception as e:
        print(f"Error sending photo {file_path}: {e}")

# الدالة الرئيسية لتشغيل الكود غير المتزامن
async def main():
    for file in files_to_upload:
        await send_photo_to_telegram(file)

# تشغيل الحدث غير المتزامن
asyncio.run(main())
