import sys
import os
import random
import asyncio
import logging
import subprocess
from pyrogram import Client

# إعداد البوت
API_ID = '8481709'
API_HASH = '4c61c465f793166c3a0e3472c1ae02c7'
TOKEN = '7886550223:AAEPUrKSv3OoUpe53OHy3Oi97s--7FR2jm0'
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)

# إعداد سجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# اسم المستخدم
username = '@Hashim_521'

# دالة للحصول على مدة الفيديو باستخدام ffprobe
def get_video_duration(file_path):
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        duration = float(result.stdout.strip())
        return duration
    except Exception as e:
        logger.error(f"Error getting video duration: {e}")
        return 0

# دالة لأخذ لقطات من الفيديو
def take_screenshots(file_path, duration, output_dir):
    try:
        os.makedirs(output_dir, exist_ok=True)
        screenshots = []

        # حساب عدد اللقطات بناءً على مدة الفيديو
        if duration < 240:  # أقل من 4 دقائق
            num_screenshots = 2
        elif 240 <= duration < 1200:  # بين 4 دقائق و20 دقيقة
            num_screenshots = 3
        elif 1200 <= duration < 2400:  # بين 20 دقيقة و40 دقيقة
            num_screenshots = 4
        else:  # أكثر من 40 دقيقة
            num_screenshots = 6

        # حساب الطوابع الزمنية عشوائيًا
        timestamps = sorted(random.sample(range(1, int(duration)), num_screenshots))

        for i, timestamp in enumerate(timestamps):
            output_file = os.path.join(output_dir, f"screenshot_{i + 1}.jpg")
            subprocess.run(
                [
                    "ffmpeg", "-ss", str(timestamp), "-i", file_path,
                    "-frames:v", "1", "-q:v", "2", output_file
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            screenshots.append((output_file, timestamp))
        
        return screenshots
    except Exception as e:
        logger.error(f"Error taking screenshots: {e}")
        return []

# دالة لإرسال الفيديو واللقطات إلى اسم المستخدم
async def send_video_with_screenshots(file_path):
    try:
        logger.info(f"Processing video: {file_path}")

        # الحصول على مدة الفيديو
        duration = get_video_duration(file_path)
        if duration == 0:
            logger.error(f"Could not determine duration for video: {file_path}")
            return

        # أخذ لقطات
        output_dir = os.path.join(os.path.dirname(file_path), "screenshots")
        screenshots = take_screenshots(file_path, duration, output_dir)

        # إرسال الفيديو
        video_description = f"Video uploaded: {os.path.basename(file_path)}"
        async def progress(current, total):
            logger.info(f"Uploaded {current * 100 / total:.1f}%")

        await app.send_video(username, video=file_path, caption=video_description, progress=progress)
        logger.info("Video sent successfully!")

        # إرسال لقطات
        for i, (screenshot, timestamp) in enumerate(screenshots, start=1):
            minutes, seconds = divmod(timestamp, 60)
            screenshot_description = f"{os.path.basename(file_path)} | {int(minutes):02}:{int(seconds):02}"
            await app.send_photo(username, photo=screenshot, caption=screenshot_description)
            logger.info(f"Screenshot {screenshot} sent successfully!")

        # حذف الفيديو واللقطات
        os.remove(file_path)
        for screenshot, _ in screenshots:
            os.remove(screenshot)
        os.rmdir(output_dir)
        logger.info(f"Deleted video and screenshots for: {file_path}")

    except Exception as e:
        logger.error(f"Error processing video {file_path}: {e}")

# الدالة الرئيسية
async def main():
    async with app:
        # قراءة مسارات الفيديو من سطر الأوامر
        files_to_upload = sys.argv[1:]
        if not files_to_upload:
            logger.error("No video files provided. Exiting...")
            return

        for file_path in files_to_upload:
            if os.path.exists(file_path):
                await send_video_with_screenshots(file_path)
            else:
                logger.error(f"File not found: {file_path}")

# تشغيل السكربت
if __name__ == "__main__":
    app.run(main())
