import os
import zipfile
import smtplib
from email.message import EmailMessage
from icrawler.builtin import BingImageCrawler
from PIL import Image

DOWNLOAD_DIR = "downloads"
PROCESSED_DIR = "processed"
OUTPUT_DIR = "output"

def create_folders():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_images(keyword, num_images):
    crawler = BingImageCrawler(storage={'root_dir': DOWNLOAD_DIR})
    crawler.crawl(keyword=keyword, max_num=num_images)

def process_images():
    for file in os.listdir(DOWNLOAD_DIR):
        img_path = os.path.join(DOWNLOAD_DIR, file)
        img = Image.open(img_path)

        width, height = img.size
        img = img.resize((width // 2, height // 2))
        img = img.convert("L")

        img.save(os.path.join(PROCESSED_DIR, file))

def zip_images():
    zip_path = os.path.join(OUTPUT_DIR, "processed_images.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in os.listdir(PROCESSED_DIR):
            zipf.write(
                os.path.join(PROCESSED_DIR, file),
                arcname=file
            )
    return zip_path

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

def send_email(receiver_email, zip_path):
    msg = EmailMessage()
    msg['Subject'] = "Processed Images"
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg.set_content("Attached are your processed images.")

    with open(zip_path, 'rb') as f:
        file_data = f.read()
        msg.add_attachment(
            file_data,
            maintype='application',
            subtype='zip',
            filename="processed_images.zip"
        )

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER_EMAIL, APP_PASSWORD)
        smtp.send_message(msg)

