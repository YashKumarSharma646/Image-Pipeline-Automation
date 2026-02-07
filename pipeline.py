import os
import shutil
import base64
from icrawler.builtin import BingImageCrawler
from PIL import Image
import resend


# =========================
# Folder Setup
# =========================

DOWNLOAD_FOLDER = "downloads"
PROCESSED_FOLDER = "processed"
OUTPUT_FOLDER = "output"


def create_folders():
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def clear_folder(folder_path):
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)


# =========================
# Download Images
# =========================

def download_images(keyword, num_images):
    crawler = BingImageCrawler(storage={'root_dir': DOWNLOAD_FOLDER})
    crawler.crawl(keyword=keyword, max_num=num_images)


# =========================
# Process Images
# =========================

def process_images():
    for filename in os.listdir(DOWNLOAD_FOLDER):
        input_path = os.path.join(DOWNLOAD_FOLDER, filename)

        try:
            with Image.open(input_path) as img:
                # Resize to 50%
                width, height = img.size
                resized_img = img.resize((width // 2, height // 2))

                # Convert to grayscale
                gray_img = resized_img.convert("L")

                output_path = os.path.join(PROCESSED_FOLDER, filename)
                gray_img.save(output_path)

        except Exception as e:
            print(f"Error processing {filename}: {e}")


# =========================
# Zip Processed Images
# =========================

def zip_images():
    zip_path = os.path.join(OUTPUT_FOLDER, "processed_images")
    shutil.make_archive(zip_path, 'zip', PROCESSED_FOLDER)
    return zip_path + ".zip"


# =========================
# Send Email via Resend
# =========================

resend.api_key = os.getenv("RESEND_API_KEY")


def send_email(receiver_email, zip_path):

    if not resend.api_key:
        raise ValueError("RESEND_API_KEY not set.")

    with open(zip_path, "rb") as f:
        file_data = f.read()

    encoded_file = base64.b64encode(file_data).decode()

    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": receiver_email,
        "subject": "Processed Images",
        "html": "<p>Your processed images are attached.</p>",
        "attachments": [
            {
                "filename": "processed_images.zip",
                "content": encoded_file
            }
        ]
    })
