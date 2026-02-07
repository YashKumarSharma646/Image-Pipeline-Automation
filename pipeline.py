import os
import zipfile
import smtplib
from email.message import EmailMessage
from icrawler.builtin import BingImageCrawler
from PIL import Image

# Folder paths
DOWNLOAD_DIR = "downloads"
PROCESSED_DIR = "processed"
OUTPUT_DIR = "output"

# Environment variables (must be set in Render)
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")


# -------------------------------
# Folder Management
# -------------------------------

def create_folders():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def clear_folder(folder_path):
    if not os.path.exists(folder_path):
        return
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


# -------------------------------
# Image Download
# -------------------------------

def download_images(keyword, num_images):
    crawler = BingImageCrawler(storage={'root_dir': DOWNLOAD_DIR})
    crawler.crawl(keyword=keyword, max_num=num_images)


# -------------------------------
# Image Processing
# -------------------------------

def process_images():
    for file in os.listdir(DOWNLOAD_DIR):
        input_path = os.path.join(DOWNLOAD_DIR, file)

        try:
            img = Image.open(input_path)

            # Resize to 50%
            width, height = img.size
            img = img.resize((width // 2, height // 2))

            # Convert to grayscale
            img = img.convert("L")

            output_path = os.path.join(PROCESSED_DIR, file)
            img.save(output_path)

        except Exception as e:
            print(f"Error processing {file}: {e}")


# -------------------------------
# Zip Processed Images
# -------------------------------

def zip_images():
    zip_path = os.path.join(OUTPUT_DIR, "processed_images.zip")

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in os.listdir(PROCESSED_DIR):
            file_path = os.path.join(PROCESSED_DIR, file)
            zipf.write(file_path, arcname=file)

    return zip_path


# -------------------------------
# Email Sending
# -------------------------------

def send_email(receiver_email, zip_path):

    if not SENDER_EMAIL or not APP_PASSWORD:
        raise ValueError("Email environment variables are not set.")

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
