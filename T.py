import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters

# إعدادات البوت
TOKEN = '7216683481:AAFg4XeoLGVzSwe604GARV3RtRZL0N1PnSA'
GROUP_CHAT_ID = -1002364051928
USER_CHAT_ID = 421777948
SENT_PHOTOS_FILE = 'sent_photos.txt'
STARRED_PHOTOS_FILE = 'starred_photos.txt'
REJECTED_PHOTOS_FILE = 'rejected_photos.txt'

STARRED2_PHOTOS_FILE = 'starred2_photos.txt'
REJECTED2_PHOTOS_FILE = 'rejected2_photos.txt'

STARRED3_PHOTOS_FILE = 'starred3_photos.txt'
REJECTED3_PHOTOS_FILE = 'rejected3_photos.txt'

STARRED4_PHOTOS_FILE = 'starred4_photos.txt'
REJECTED4_PHOTOS_FILE = 'rejected4_photos.txt'

STARRED5_PHOTOS_FILE = 'starred5_photos.txt'
REJECTED5_PHOTOS_FILE = 'rejected5_photos.txt'
# إعداد المهلة الزمنية
REQUEST_TIMEOUT = 60  # مهلة زمنية أطول (بالثواني)

# إعداد نظام تسجيل الدخول للتسجيلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

logger.info("Starting the bot...")

# حفظ معرف الرسالة في ملف
def save_message_id(file, message_id):
    logger.info(f"Saving message ID {message_id} to file {file}")
    with open(file, 'a') as f:
        f.write(f"{message_id}\n")

# تحميل معرفات الرسائل من ملف
def load_message_ids(file):
    logger.info(f"Loading message IDs from file {file}")
    if not os.path.exists(file):
        logger.info(f"File {file} does not exist")
        return []
    with open(file, 'r') as f:
        return [line.strip() for line in f]

# حفظ معرف الرسالة في ملف الصور المرسلة
def save_sent_photo(message_id):
    save_message_id(SENT_PHOTOS_FILE, message_id)

# حفظ معرف الرسالة في ملف الصور بنجمة
def save_starred_photo(message_id):
    save_message_id(STARRED_PHOTOS_FILE, message_id)

# حفظ معرف الرسالة في ملف الصور المرفوضة
def save_rejected_photo(message_id):
    save_message_id(REJECTED_PHOTOS_FILE, message_id)

def save_starred2_photo(message_id):
    save_message_id(STARRED2_PHOTOS_FILE, message_id)

def save_rejected2_photo(message_id):
    save_message_id(REJECTED2_PHOTOS_FILE, message_id)
    
def save_starred3_photo(message_id):
    save_message_id(STARRED3_PHOTOS_FILE, message_id)

def save_rejected3_photo(message_id):
    save_message_id(REJECTED3_PHOTOS_FILE, message_id)
    
def save_starred4_photo(message_id):
    save_message_id(STARRED4_PHOTOS_FILE, message_id)

def save_rejected4_photo(message_id):
    save_message_id(REJECTED4_PHOTOS_FILE, message_id)
    
def save_starred5_photo(message_id):
    save_message_id(STARRED5_PHOTOS_FILE, message_id)

def save_rejected5_photo(message_id):
    save_message_id(REJECTED5_PHOTOS_FILE, message_id)    
    
# جلب معرفات الصور المرسلة
def get_sent_photos():
    return load_message_ids(SENT_PHOTOS_FILE)

# إرسال 3 صور عشوائية من المرسلة
async def send_random_photos_rate1(update: Update, context: CallbackContext):
    logger.info("Sending photos for rate 1")

    # جلب الصور المرسلة من `SENT_PHOTOS_FILE`
    sent_photos = load_message_ids(SENT_PHOTOS_FILE)
    
    # تصفية الصور التي تم تقييمها من قبل (الصور التي تم تقييمها بنجوم من الفئات الأخرى)
    starred_photos = set(load_message_ids(STARRED_PHOTOS_FILE))  # الصور التي تم تقييمها بنجمة واحدة
    rejected_photos = set(load_message_ids(REJECTED_PHOTOS_FILE))  # الصور المرفوضة

    # اختر الصور التي لم يتم تقييمها بعد (الصور المرسلة ولم يتم تقييمها)
    unrated_photos = [photo_id for photo_id in sent_photos if photo_id not in starred_photos and photo_id not in rejected_photos]
    
    if len(unrated_photos) < 3:
        await update.message.reply_text(f"لا توجد صور كافية لإرسالها. يوجد فقط {len(unrated_photos)} صورة.")
        return
    
    # اختر 3 صور عشوائيًا
    random_photos = random.sample(unrated_photos, 3)
    
    keyboard = []
    for idx, photo_id in enumerate(random_photos):
        await context.bot.forward_message(chat_id=USER_CHAT_ID, from_chat_id=GROUP_CHAT_ID, message_id=photo_id)
        keyboard.append([InlineKeyboardButton(f"اختر صورة {idx + 1}", callback_data=str(photo_id))])

    # إرسال رسالة مع لوحة المفاتيح
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر الصورة التي تريد تقييمها:", reply_markup=reply_markup)
    context.user_data['sent_images'] = random_photos

async def choose_image_rate1(update: Update, context: CallbackContext):
    query = update.callback_query
    chosen_image_id = query.data  # التعامل مع المعرف كنص
    logger.info(f"Chosen image ID: {chosen_image_id}")
    sent_images = context.user_data.get('sent_images', [])
    logger.info(f"Sent images: {sent_images}")

    if chosen_image_id in sent_images:
        # إضافة الصورة المختارة إلى `STARRED_PHOTOS_FILE`
        logger.info(f"Image {chosen_image_id} chosen and saved to starred photos")
        save_starred_photo(chosen_image_id)
        await query.edit_message_text(text=f"تم اختيار الصورة وتقييمها بنجمة: {chosen_image_id}")
        
        # نقل الصور غير المختارة إلى ملف المرفوضة
        for image_id in sent_images:
            if image_id != chosen_image_id:
                logger.info(f"Image {image_id} saved to rejected photos")
                save_rejected_photo(image_id)
    else:
        logger.error(f"Error: Chosen image ID {chosen_image_id} not found in sent images")
        await query.edit_message_text(text="حدث خطأ أثناء اختيار الصورة. الرجاء المحاولة مرة أخرى.")
    
async def send_random_photos_rate2(update: Update, context: CallbackContext):
    logger.info("Sending photos for rate 2")

    # جلب الصور المرسلة من `STARRED_PHOTOS_FILE`
    starred_photos = load_message_ids(STARRED_PHOTOS_FILE)
    
    # تصفية الصور التي تم تقييمها من قبل (الصور التي تم تقييمها بنجوم من الفئات الأخرى)
    starred2_photos = set(load_message_ids(STARRED2_PHOTOS_FILE))  # الصور التي تم تقييمها بنجمة في الفئة الثانية
    rejected_photos = set(load_message_ids(REJECTED2_PHOTOS_FILE))  # الصور المرفوضة في الفئة الثانية

    # اختر الصور التي لم يتم تقييمها بعد (الصور التي لم يتم تقييمها في الفئة الثانية)
    unrated_photos = [photo_id for photo_id in starred_photos if photo_id not in starred2_photos and photo_id not in rejected_photos]
    
    if len(unrated_photos) < 3:
        await update.message.reply_text(f"لا توجد صور كافية لإرسالها. يوجد فقط {len(unrated_photos)} صورة.")
        return
    
    # اختر 3 صور عشوائيًا
    random_photos = random.sample(unrated_photos, 3)
    
    keyboard = []
    for idx, photo_id in enumerate(random_photos):
        await context.bot.forward_message(chat_id=USER_CHAT_ID, from_chat_id=GROUP_CHAT_ID, message_id=photo_id)
        keyboard.append([InlineKeyboardButton(f"اختر صورة {idx + 1}", callback_data=str(photo_id))])

    # إرسال رسالة مع لوحة المفاتيح
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر الصورة التي تريد تقييمها:", reply_markup=reply_markup)
    context.user_data['sent_images'] = random_photos

async def choose_image_rate2(update: Update, context: CallbackContext):
    query = update.callback_query
    chosen_image_id = query.data  # التعامل مع المعرف كنص
    logger.info(f"Chosen image ID: {chosen_image_id}")
    sent_images = context.user_data.get('sent_images', [])
    logger.info(f"Sent images: {sent_images}")

    if chosen_image_id in sent_images:
        # إضافة الصورة المختارة إلى `STARRED2_PHOTOS_FILE`
        logger.info(f"Image {chosen_image_id} chosen and saved to starred2 photos")
        save_starred2_photo(chosen_image_id)
        await query.edit_message_text(text=f"تم اختيار الصورة وتقييمها بنجمة: {chosen_image_id}")
        
        # نقل الصور غير المختارة إلى ملف المرفوضة
        for image_id in sent_images:
            if image_id != chosen_image_id:
                logger.info(f"Image {image_id} saved to rejected2 photos")
                save_rejected2_photo(image_id)
    else:
        logger.error(f"Error: Chosen image ID {chosen_image_id} not found in sent images")
        await query.edit_message_text(text="حدث خطأ أثناء اختيار الصورة. الرجاء المحاولة مرة أخرى.")

async def send_random_photos_rate3(update: Update, context: CallbackContext):
    logger.info("Sending photos for rate 3")

    # جلب الصور المرسلة من `STARRED2_PHOTOS_FILE`
    starred2_photos = load_message_ids(STARRED2_PHOTOS_FILE)
    
    # تصفية الصور التي تم تقييمها من قبل (الصور التي تم تقييمها بنجوم من الفئات الأخرى)
    starred3_photos = set(load_message_ids(STARRED3_PHOTOS_FILE))  # الصور التي تم تقييمها بنجمة في الفئة الثالثة
    rejected_photos = set(load_message_ids(REJECTED3_PHOTOS_FILE))  # الصور المرفوضة في الفئة الثالثة

    # اختر الصور التي لم يتم تقييمها بعد (الصور التي لم يتم تقييمها في الفئة الثالثة)
    unrated_photos = [photo_id for photo_id in starred2_photos if photo_id not in starred3_photos and photo_id not in rejected_photos]
    
    if len(unrated_photos) < 3:
        await update.message.reply_text(f"لا توجد صور كافية لإرسالها. يوجد فقط {len(unrated_photos)} صورة.")
        return
    
    # اختر 3 صور عشوائيًا
    random_photos = random.sample(unrated_photos, 3)
    
    keyboard = []
    for idx, photo_id in enumerate(random_photos):
        await context.bot.forward_message(chat_id=USER_CHAT_ID, from_chat_id=GROUP_CHAT_ID, message_id=photo_id)
        keyboard.append([InlineKeyboardButton(f"اختر صورة {idx + 1}", callback_data=str(photo_id))])

    # إرسال رسالة مع لوحة المفاتيح
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر الصورة التي تريد تقييمها:", reply_markup=reply_markup)
    context.user_data['sent_images'] = random_photos

    
    
# دالة لمعالجة اختيار الصورة، مع تحديد الفئة المناسبة
async def choose_image(update: Update, context: CallbackContext):
    query = update.callback_query
    chosen_image_id = query.data  # التعامل مع المعرف كنص
    logger.info(f"Chosen image ID: {chosen_image_id}")
    
    # الحصول على الفئة المختارة من خلال المتغير user_data
    rate_level = context.user_data.get('rate_level', 1)
    logger.info(f"Rate level: {rate_level}")

    # تحميل الملفات الخاصة بالفئة المناسبة
    if rate_level == 1:
        starred_file = STARRED_PHOTOS_FILE
        rejected_file = REJECTED_PHOTOS_FILE
    elif rate_level == 2:
        starred_file = STARRED2_PHOTOS_FILE
        rejected_file = REJECTED2_PHOTOS_FILE
    elif rate_level == 3:
        starred_file = STARRED3_PHOTOS_FILE
        rejected_file = REJECTED3_PHOTOS_FILE
    elif rate_level == 4:
        starred_file = STARRED4_PHOTOS_FILE
        rejected_file = REJECTED4_PHOTOS_FILE
    elif rate_level == 5:
        starred_file = STARRED5_PHOTOS_FILE
        rejected_file = REJECTED5_PHOTOS_FILE
    else:
        logger.error(f"Invalid rate level: {rate_level}")
        await query.edit_message_text(text="حدث خطأ أثناء اختيار الصورة. الرجاء المحاولة مرة أخرى.")
        return

    # التحقق مما إذا كانت الصورة قد تم إرسالها في هذا المستوى أم لا
    sent_images = context.user_data.get('sent_images', [])
    logger.info(f"Sent images: {sent_images}")

    if chosen_image_id in sent_images:
        # إضافة الصورة المختارة إلى ملف النجوم الخاص بالفئة المختارة
        logger.info(f"Image {chosen_image_id} chosen and saved to starred file: {starred_file}")
        save_starred_photo(chosen_image_id, starred_file)
        await query.edit_message_text(text=f"تم اختيار الصورة وتقييمها بنجمة في الفئة {rate_level}: {chosen_image_id}")
        
        # نقل الصور غير المختارة إلى ملف المرفوضة الخاص بالفئة
        for image_id in sent_images:
            if image_id != chosen_image_id:
                logger.info(f"Image {image_id} saved to rejected file: {rejected_file}")
                save_rejected_photo(image_id, rejected_file)
    else:
        logger.error(f"Error: Chosen image ID {chosen_image_id} not found in sent images")
        await query.edit_message_text(text="حدث خطأ أثناء اختيار الصورة. الرجاء المحاولة مرة أخرى.")

# دالة لحفظ الصور التي تم تقييمها بنجمة
def save_starred_photo(message_id, starred_file):
    save_message_id(starred_file, message_id)

# دالة لحفظ الصور المرفوضة
def save_rejected_photo(message_id, rejected_file):
    save_message_id(rejected_file, message_id)

# دالة لحفظ معرّف الرسالة في ملف معين
def save_message_id(file, message_id):
    logger.info(f"Saving message ID {message_id} to file {file}")
    with open(file, 'a') as f:
        f.write(f"{message_id}\n")

async def send_random_photos_rate4(update: Update, context: CallbackContext):
    logger.info("Sending photos for rate 4")

    # جلب الصور المرسلة من `STARRED3_PHOTOS_FILE`
    starred3_photos = load_message_ids(STARRED3_PHOTOS_FILE)
    
    # تصفية الصور التي تم تقييمها من قبل (الصور التي تم تقييمها بنجوم من الفئات الأخرى)
    starred4_photos = set(load_message_ids(STARRED4_PHOTOS_FILE))  # الصور التي تم تقييمها بنجمة في الفئة الرابعة
    rejected_photos = set(load_message_ids(REJECTED4_PHOTOS_FILE))  # الصور المرفوضة في الفئة الرابعة

    # اختر الصور التي لم يتم تقييمها بعد (الصور التي لم يتم تقييمها في الفئة الرابعة)
    unrated_photos = [photo_id for photo_id in starred3_photos if photo_id not in starred4_photos and photo_id not in rejected_photos]
    
    if len(unrated_photos) < 3:
        await update.message.reply_text(f"لا توجد صور كافية لإرسالها. يوجد فقط {len(unrated_photos)} صورة.")
        return
    
    # اختر 3 صور عشوائيًا
    random_photos = random.sample(unrated_photos, 3)
    
    keyboard = []
    for idx, photo_id in enumerate(random_photos):
        await context.bot.forward_message(chat_id=USER_CHAT_ID, from_chat_id=GROUP_CHAT_ID, message_id=photo_id)
        keyboard.append([InlineKeyboardButton(f"اختر صورة {idx + 1}", callback_data=str(photo_id))])

    # إرسال رسالة مع لوحة المفاتيح
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر الصورة التي تريد تقييمها:", reply_markup=reply_markup)
    context.user_data['sent_images'] = random_photos

async def choose_image_rate4(update: Update, context: CallbackContext):
    query = update.callback_query
    chosen_image_id = query.data  # التعامل مع المعرف كنص
    logger.info(f"Chosen image ID: {chosen_image_id}")
    sent_images = context.user_data.get('sent_images', [])
    logger.info(f"Sent images: {sent_images}")

    if chosen_image_id in sent_images:
        # إضافة الصورة المختارة إلى `STARRED4_PHOTOS_FILE`
        logger.info(f"Image {chosen_image_id} chosen and saved to starred4 photos")
        save_starred4_photo(chosen_image_id)
        await query.edit_message_text(text=f"تم اختيار الصورة وتقييمها بنجمة: {chosen_image_id}")
        
        # نقل الصور غير المختارة إلى ملف المرفوضة
        for image_id in sent_images:
            if image_id != chosen_image_id:
                logger.info(f"Image {image_id} saved to rejected4 photos")
                save_rejected4_photo(image_id)
    else:
        logger.error(f"Error: Chosen image ID {chosen_image_id} not found in sent images")
        await query.edit_message_text(text="حدث خطأ أثناء اختيار الصورة. الرجاء المحاولة مرة أخرى.")
        
async def send_random_photos_rate5(update: Update, context: CallbackContext):
    logger.info("Sending photos for rate 5")

    # جلب الصور المرسلة من `STARRED4_PHOTOS_FILE`
    starred4_photos = load_message_ids(STARRED4_PHOTOS_FILE)
    
    # تصفية الصور التي تم تقييمها من قبل (الصور التي تم تقييمها بنجوم من الفئات الأخرى)
    starred5_photos = set(load_message_ids(STARRED5_PHOTOS_FILE))  # الصور التي تم تقييمها بنجمة في الفئة الخامسة
    rejected_photos = set(load_message_ids(REJECTED5_PHOTOS_FILE))  # الصور المرفوضة في الفئة الخامسة

    # اختر الصور التي لم يتم تقييمها بعد (الصور التي لم يتم تقييمها في الفئة الخامسة)
    unrated_photos = [photo_id for photo_id in starred4_photos if photo_id not in starred5_photos and photo_id not in rejected_photos]
    
    if len(unrated_photos) < 3:
        await update.message.reply_text(f"لا توجد صور كافية لإرسالها. يوجد فقط {len(unrated_photos)} صورة.")
        return
    
    # اختر 3 صور عشوائيًا
    random_photos = random.sample(unrated_photos, 3)
    
    keyboard = []
    for idx, photo_id in enumerate(random_photos):
        await context.bot.forward_message(chat_id=USER_CHAT_ID, from_chat_id=GROUP_CHAT_ID, message_id=photo_id)
        keyboard.append([InlineKeyboardButton(f"اختر صورة {idx + 1}", callback_data=str(photo_id))])

    # إرسال رسالة مع لوحة المفاتيح
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر الصورة التي تريد تقييمها:", reply_markup=reply_markup)
    context.user_data['sent_images'] = random_photos

async def choose_image_rate5(update: Update, context: CallbackContext):
    query = update.callback_query
    chosen_image_id = query.data  # التعامل مع المعرف كنص
    logger.info(f"Chosen image ID: {chosen_image_id}")
    sent_images = context.user_data.get('sent_images', [])
    logger.info(f"Sent images: {sent_images}")

    if chosen_image_id in sent_images:
        # إضافة الصورة المختارة إلى `STARRED5_PHOTOS_FILE`
        logger.info(f"Image {chosen_image_id} chosen and saved to starred5 photos")
        save_starred5_photo(chosen_image_id)
        await query.edit_message_text(text=f"تم اختيار الصورة وتقييمها بنجمة: {chosen_image_id}")
        
        # نقل الصور غير المختارة إلى ملف المرفوضة
        for image_id in sent_images:
            if image_id != chosen_image_id:
                logger.info(f"Image {image_id} saved to rejected5 photos")
                save_rejected5_photo(image_id)
    else:
        logger.error(f"Error: Chosen image ID {chosen_image_id} not found in sent images")
        await query.edit_message_text(text="حدث خطأ أثناء اختيار الصورة. الرجاء المحاولة مرة أخرى.")      


# إعادة إرسال جميع الصور التي تم اختيارها كنجمة
async def send_starred_images(update: Update, context: CallbackContext, starred_file):
    logger.info("Sending starred images")
    message_ids = load_message_ids(starred_file)
    for message_id in message_ids:
        await context.bot.forward_message(chat_id=USER_CHAT_ID, from_chat_id=GROUP_CHAT_ID, message_id=int(message_id))
        await context.bot.send_message(chat_id=USER_CHAT_ID, text="صورة مميزة")

# توجيه الصور الجديدة تلقائيًا وتخزين معرف الرسالة
async def forward_photo(update: Update, context: CallbackContext):
    if update.message.chat_id == GROUP_CHAT_ID and update.message.photo:
        # توجيه الصورة إلى المستخدم المحدد
        await context.bot.forward_message(chat_id=USER_CHAT_ID, from_chat_id=GROUP_CHAT_ID, message_id=update.message.message_id)
        logger.info(f"Forwarded photo from group {GROUP_CHAT_ID} to user {USER_CHAT_ID}")
        # حفظ معرف الرسالة في ملف
        save_sent_photo(update.message.message_id)

# دالة لإرسال عدد من الصور التي لم يتم تقييمها بعد
async def send_unrated_photos(update: Update, context: CallbackContext, source_file, num_photos):
    logger.info(f"Sending {num_photos} unrated photos from {source_file}")
    
    # جلب معرفات الصور من الملف
    sent_photos = load_message_ids(source_file)
    starred_photos = set(load_message_ids(STARRED_PHOTOS_FILE))  # إذا كنت تريد استبعاد الصور المميزة
    rejected_photos = set(load_message_ids(REJECTED_PHOTOS_FILE))  # أو الصور المرفوضة

    # الصور التي لم يتم تقييمها بعد (أي التي لم يتم تقييمها ولا رفضها)
    unrated_photos = [photo_id for photo_id in sent_photos if photo_id not in starred_photos and photo_id not in rejected_photos]
    
    if len(unrated_photos) < num_photos:
        await update.message.reply_text(f"لا توجد صور كافية لإرسالها. يوجد فقط {len(unrated_photos)} صورة.")
        num_photos = len(unrated_photos)  # إرسال العدد المتاح إذا كان أقل من المطلوب

    # إرسال الصور المطلوبة
    for i in range(num_photos):
        photo_id = unrated_photos[i]
        await context.bot.forward_message(chat_id=USER_CHAT_ID, from_chat_id=GROUP_CHAT_ID, message_id=photo_id)
    await update.message.reply_text(f"تم إرسال {num_photos} صورة غير تقييمها.")

# معالجات الأوامر
# معالجة الأمر /many لعدد من الصور غير المقيّمة بناءً على الفئة
async def handle_many(update: Update, context: CallbackContext):
    num_photos = int(context.args[0]) if context.args else 1  # إذا لم يتم تحديد عدد، افترض 1
    # حساب عدد الصور غير المقيّمة في SENT_PHOTOS_FILE
    total_unrated_photos = len(load_message_ids(SENT_PHOTOS_FILE))
    await update.message.reply_text(f"عدد الصور غير المقيّمة المتاحة في SENT_PHOTOS_FILE هو: {total_unrated_photos}")

async def handle_many1(update: Update, context: CallbackContext):
    num_photos = int(context.args[0]) if context.args else 1
    # حساب عدد الصور غير المقيّمة في STARRED_PHOTOS_FILE
    total_unrated_photos = len(load_message_ids(STARRED_PHOTOS_FILE))
    await update.message.reply_text(f"عدد الصور غير المقيّمة المتاحة في STARRED_PHOTOS_FILE هو: {total_unrated_photos}")

async def handle_many2(update: Update, context: CallbackContext):
    num_photos = int(context.args[0]) if context.args else 1
    # حساب عدد الصور غير المقيّمة في STARRED2_PHOTOS_FILE
    total_unrated_photos = len(load_message_ids(STARRED2_PHOTOS_FILE))
    await update.message.reply_text(f"عدد الصور غير المقيّمة المتاحة في STARRED2_PHOTOS_FILE هو: {total_unrated_photos}")

async def handle_many3(update: Update, context: CallbackContext):
    num_photos = int(context.args[0]) if context.args else 1
    # حساب عدد الصور غير المقيّمة في STARRED3_PHOTOS_FILE
    total_unrated_photos = len(load_message_ids(STARRED3_PHOTOS_FILE))
    await update.message.reply_text(f"عدد الصور غير المقيّمة المتاحة في STARRED3_PHOTOS_FILE هو: {total_unrated_photos}")

async def handle_many4(update: Update, context: CallbackContext):
    num_photos = int(context.args[0]) if context.args else 1
    # حساب عدد الصور غير المقيّمة في STARRED4_PHOTOS_FILE
    total_unrated_photos = len(load_message_ids(STARRED4_PHOTOS_FILE))
    await update.message.reply_text(f"عدد الصور غير المقيّمة المتاحة في STARRED4_PHOTOS_FILE هو: {total_unrated_photos}")

async def handle_many5(update: Update, context: CallbackContext):
    num_photos = int(context.args[0]) if context.args else 1
    # حساب عدد الصور غير المقيّمة في STARRED5_PHOTOS_FILE
    total_unrated_photos = len(load_message_ids(STARRED5_PHOTOS_FILE))
    await update.message.reply_text(f"عدد الصور غير المقيّمة المتاحة في STARRED5_PHOTOS_FILE هو: {total_unrated_photos}")

# بدء تشغيل البوت
def main():
    logger.info("Setting up the application...")
    application = Application.builder().token(TOKEN).build()

    # إضافة معالج للرسائل التي تحتوي على صور
    application.add_handler(MessageHandler(filters.PHOTO, forward_photo))

    # إضافة معالج لأوامر /rate1, /rate2, /rate3, /rate4, /rate5
    application.add_handler(CommandHandler('rate1', send_random_photos_rate1))
    application.add_handler(CommandHandler('rate2', send_random_photos_rate2))
    application.add_handler(CommandHandler('rate3', send_random_photos_rate3))
    application.add_handler(CommandHandler('rate4', send_random_photos_rate4))
    application.add_handler(CommandHandler('rate5', send_random_photos_rate5))
    
    # إضافة معالج لاختيار الصورة
    application.add_handler(CallbackQueryHandler(choose_image))
    
    # إضافة معالج لأوامر /many, /many1, /many2, /many3, /many4, /many5
    application.add_handler(CommandHandler('many', handle_many))
    application.add_handler(CommandHandler('many1', handle_many1))
    application.add_handler(CommandHandler('many2', handle_many2))
    application.add_handler(CommandHandler('many3', handle_many3))
    application.add_handler(CommandHandler('many4', handle_many4))
    application.add_handler(CommandHandler('many5', handle_many5))

    # إضافة معالج لأوامر /1, /2, /3, /4, /5 لإرسال الصور المميزة
    application.add_handler(CommandHandler('1', send_starred_images))
    application.add_handler(CommandHandler('2', send_starred_images))
    application.add_handler(CommandHandler('3', send_starred_images))
    application.add_handler(CommandHandler('4', send_starred_images))
    application.add_handler(CommandHandler('5', send_starred_images))

    logger.info("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
