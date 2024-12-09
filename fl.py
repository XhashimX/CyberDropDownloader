import sys
import subprocess
from telegram import Bot
import os
import asyncio

# التوكين الخاص بالبوت
TOKEN = '7886550223:AAEPUrKSv3OoUpe53OHy3Oi97s--7FR2jm0'
bot = Bot(token=TOKEN)

# قراءة مسارات الملفات من سطر الأوامر
files_to_upload = sys.argv[1:]

# معرف الدردشة
chat_id = '421777948'

# دالة لتقسيم الفيديو
def split_video(video_path):
    output_pattern = video_path.rsplit('.', 1)[0] + "_part%03d.mp4"
    command = [
        'ffmpeg', '-i', video_path, '-c', 'copy', '-map', '0',
        '-segment_time', '00:01:20', '-force_key_frames', 'expr:gte(t,n_forced*80)',
        '-f', 'segment', '-reset_timestamps', '1', output_pattern
    ]
    subprocess.run(command)
    parts = [output_pattern % i for i in range(100)]  # توقع عدد الأجزاء (يمكنك تعديل هذا إذا لزم الأمر)
    parts = [part for part in parts if os.path.exists(part)]
    return parts

# دالة لإنشاء لقطات شاشة من الفيديو
def create_screenshots(video_path):
    timestamps = ['00:00:15', '00:00:50', '00:01:10']  # النقاط الزمنية المختلفة
    screenshot_paths = []
    for i, timestamp in enumerate(timestamps):
        screenshot_path = video_path.rsplit('.', 1)[0] + f"_screenshot_{i+1}.jpg"
        command = [
            'ffmpeg', '-i', video_path, '-ss', timestamp, '-vframes', '1', screenshot_path
        ]
        subprocess.run(command, check=True)
        screenshot_paths.append(screenshot_path)
    return screenshot_paths

# دالة غير متزامنة لإرسال الفيديو مع لقطات الشاشة
async def send_video_to_telegram(file_path):
    try:
        screenshot_paths = create_screenshots(file_path)
        with open(file_path, 'rb') as video:
            await bot.send_video(chat_id=chat_id, video=video, caption=os.path.basename(file_path))
        for screenshot_path in screenshot_paths:
            with open(screenshot_path, 'rb') as screenshot:
                await bot.send_photo(chat_id=chat_id, photo=screenshot, caption=f'Screenshot of {os.path.basename(file_path)}')
        print(f"Video {file_path} and screenshots sent successfully!")
        # حذف الفيديو ولقطات الشاشة بعد إرسالهما بنجاح
        os.remove(file_path)
        for screenshot_path in screenshot_paths:
            os.remove(screenshot_path)
        print(f"Video {file_path} and screenshots deleted successfully!")
    except Exception as e:
        print(f"Error sending video {file_path}: {e}")

# الدالة الرئيسية لتشغيل الكود غير المتزامن
async def main():
    for file in files_to_upload:
        parts = split_video(file)
        for part in parts:
            await send_video_to_telegram(part)
        # حذف الملف الأساسي بعد إرسال جميع الأجزاء
        os.remove(file)
        print(f"Original video {file} deleted successfully!")

# تشغيل الحدث غير المتزامن
asyncio.run(main())
