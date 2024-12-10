import sys
import subprocess
import os
import asyncio
import random
import math
from telegram import Bot

# التوكين الخاص بالبوت
TOKEN = '7886550223:AAEPUrKSv3OoUpe53OHy3Oi97s--7FR2jm0'
bot = Bot(token=TOKEN)

# قراءة مسارات الملفات من سطر الأوامر
files_to_upload = sys.argv[1:]

# معرف الدردشة
chat_id = '-4614656936'


# دالة للحصول على طول الفيديو باستخدام ffprobe
def get_video_duration(video_path):
    command = [
        'ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(result.stdout.strip()) if result.returncode == 0 else None


# دالة لتقسيم الفيديو إلى أجزاء متساوية بناءً على الحجم
def ensure_video_size(video_path, max_size_mb=48):
    max_size_bytes = max_size_mb * 1024 * 1024
    file_size = os.path.getsize(video_path)

    # إذا كان حجم الفيديو أقل من الحجم الأقصى، فلا حاجة للتقسيم
    if file_size <= max_size_bytes:
        return [video_path]

    # حساب عدد الأجزاء المطلوبة
    num_parts = math.ceil(file_size / max_size_bytes)

    # الحصول على طول الفيديو
    duration = get_video_duration(video_path)
    if not duration:
        print(f"Error: Unable to get duration for {video_path}.")
        return []

    # حساب مدة كل جزء
    part_duration = duration / num_parts
    parts = []

    # تقسيم الفيديو
    for i in range(num_parts):
        start_time = i * part_duration
        output_file = f"{video_path.rsplit('.', 1)[0]}_part{i+1}.mp4"
        command = [
            'ffmpeg', '-i', video_path, '-ss', str(start_time), '-t', str(part_duration),
            '-c', 'copy', output_file
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # التحقق من نجاح العملية
        if result.returncode == 0 and os.path.exists(output_file):
            parts.append(output_file)
        else:
            print(f"Error: Failed to create part {i+1} for {video_path}")
            break

    # التحقق من نجاح تقسيم جميع الأجزاء قبل حذف الملف الأصلي
    if len(parts) == num_parts:
        os.remove(video_path)
        print(f"Original file {video_path} deleted successfully after splitting.")
    else:
        print(f"Error: Not all parts were created successfully for {video_path}")

    return parts


# دالة لإنشاء لقطات شاشة عشوائية
def create_screenshots(video_path):
    duration = get_video_duration(video_path)
    if not duration:
        print(f"Error: Unable to determine duration for {video_path}")
        return []

    timestamps = sorted([
        random.uniform(0, duration * 0.2),
        random.uniform(duration * 0.4, duration * 0.6),
        random.uniform(duration * 0.8, duration)
    ])

    screenshot_paths = []
    for i, timestamp in enumerate(timestamps):
        screenshot_path = video_path.rsplit('.', 1)[0] + f"_screenshot_{i+1}.jpg"
        command = [
            'ffmpeg', '-i', video_path, '-ss', str(timestamp), '-vframes', '1', screenshot_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0 and os.path.exists(screenshot_path):
            screenshot_paths.append(screenshot_path)
        else:
            print(f"Error: Failed to create screenshot {i+1} for {video_path}")
            break

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

        os.remove(file_path)
        print(f"Video {file_path} deleted successfully!")
        for screenshot_path in screenshot_paths:
            os.remove(screenshot_path)
        print(f"Screenshots for {file_path} deleted successfully!")
    except Exception as e:
        print(f"Error sending video {file_path}: {e}")


# الدالة الرئيسية لتشغيل الكود غير المتزامن
async def main():
    if not files_to_upload:
        print("Error: No files provided. Please provide file paths as arguments.")
        return

    for file in files_to_upload:
        if not os.path.exists(file):
            print(f"Error: File {file} does not exist.")
            continue

        try:
            parts = ensure_video_size(file)
            for part in parts:
                await send_video_to_telegram(part)
        except Exception as e:
            print(f"Error processing file {file}: {e}")


# تشغيل الحدث غير المتزامن
asyncio.run(main())
