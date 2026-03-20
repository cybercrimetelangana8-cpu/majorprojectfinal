from flask import Flask, request, render_template, redirect, url_for, flash
from featureExtractor import featureExtraction
from gemini_report import generate_url_report, ask_gemini_about_url
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import os
import joblib

app = Flask(__name__)
app.secret_key = "real_time_threat_detection_secret"

app.config["UPLOAD_FOLDER"] = "static/uploads"

# Mail config
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)

# ✅ Lazy loading models


model = None
pca = None

def load_models():
    global model, pca
    try:
        if model is None:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            model = joblib.load(os.path.join(BASE_DIR, "model/phishingdetection.pkl"))
            pca = joblib.load(os.path.join(BASE_DIR, "model/pca_model.pkl"))
    except Exception as e:
        print("MODEL LOAD ERROR:", e)
        

def predict(url):
    load_models()
    data = featureExtraction(url)

    # If PCA used
    if pca:
        data = pca.transform(data)

    pred = model.predict(data)[0]
    prob = model.predict_proba(data)[0].max()

    return {
        "prediction_label": int(pred),
        "prediction_score": round(prob * 100, 2),
    }

@app.route("/test")
def test():
    return "Server is running ✅"

@app.route("/", methods=["GET", "POST"])
def index():
    url = request.args.get("url")
    data = None
    report = None
    answer = None

    if request.method == "POST":
        url = request.form.get("url")

    if url:
        data = predict(url)

        report = generate_url_report(
            url,
            data["prediction_label"],
            data["prediction_score"]
        )

        question = request.form.get("question")
        if question:
            answer = ask_gemini_about_url(
                url,
                data["prediction_label"],
                data["prediction_score"],
                question
            )

    return render_template(
        "index.html",
        url=url,
        data=data,
        report=report,
        answer=answer
    )


@app.route("/complaint", methods=["POST"])
def complaint():
    url = request.form["url"]
    sender = request.form["sender"]
    contact = request.form["contact"]
    medium = request.form["medium"]
    notes = request.form["notes"]
    extra_email = request.form.get("extra_email")

    screenshot = request.files.get("screenshot")
    filename = None

    if screenshot and screenshot.filename:
        filename = secure_filename(screenshot.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        screenshot.save(filepath)

    recipients = ["cyber.crime.telangana8@gmail.com"]
    if extra_email:
        recipients.append(extra_email)

    msg = Message(
        subject="🚨 Phishing Website Complaint",
        sender=app.config["MAIL_USERNAME"],
        recipients=recipients
    )

    msg.body = f"""
REAL TIME WEBSITE THREAT DETECTION - COMPLAINT

Phishing URL:
{url}

Who sent this link:
{sender}

Contact details:
{contact}

Received via:
{medium}

Additional notes:
{notes}

This complaint was generated automatically.
"""

    if filename:
        with app.open_resource(os.path.join(app.config["UPLOAD_FOLDER"], filename)) as fp:
            msg.attach(filename, "image/png", fp.read())

    mail.send(msg)

    flash("✅ Complaint sent successfully to Cyber Crime authorities.", "success")
    return redirect(url_for("index", url=url))


# ❌ REMOVE THIS (important for Vercel)
# if __name__ == "__main__":
#     app.run(debug=True)
