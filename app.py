from flask import Flask, render_template, request
from threading import Thread
from pipeline import (
    create_folders,
    clear_folder,
    download_images,
    process_images,
    zip_images,
    send_email
)

app = Flask(__name__)

def run_pipeline(keyword, num_images, email):
    create_folders()

    clear_folder("downloads")
    clear_folder("processed")
    clear_folder("output")

    download_images(keyword, num_images)
    process_images()
    zip_path = zip_images()
    send_email(email, zip_path)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        keyword = request.form["keyword"]
        num_images = int(request.form["num_images"])
        email = request.form["email"]

        thread = Thread(target=run_pipeline, args=(keyword, num_images, email))
        thread.start()

        return "Processing started. You will receive an email once completed."

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
