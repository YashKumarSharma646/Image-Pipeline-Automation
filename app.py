from flask import Flask, render_template, request
from pipeline import (
    create_folders,
    download_images,
    process_images,
    zip_images,
    send_email
)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        keyword = request.form["keyword"]
        num_images = int(request.form["num_images"])
        email = request.form["email"]

        create_folders()
        download_images(keyword, num_images)
        process_images()
        zip_path = zip_images()
        send_email(email, zip_path)

        return "Pipeline completed successfully. Check your email."

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
