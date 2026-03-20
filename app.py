from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from featureExtractor import featureExtraction
from gemini_report import generate_url_report, ask_gemini_about_url
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import os
import joblib

app = Flask(__name__)
app.secret_key = "real_time_threat_detection_secret"

app.config["UPLOAD_FOLDER"] = "static/uploads"

# Mail config (safe defaults)
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)

# ==============================
# MODEL LOADING (SAFE)
# ==============================
model = None
pca = None

def load_models():
    global model, pca
    if model is None:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        try:
            model_path = os.path.join(BASE_DIR, "model/phishingdetection.pkl")
            pca_path = os.path.join(BASE_DIR, "model/pca_model.pkl")

            if not os.path.exists(model_path):
                raise Exception(f"Model file not found: {model_path}")

            if not os.path.exists(pca_path):
                raise Exception(f"PCA file not found: {pca_path}")

            model = joblib.load(model_path)
            pca = joblib.load(pca_path)

        except Exception as e:
            raise Exception(f"Model loading failed: {str(e)}")


# ==============================
# PREDICTION
# ==============================
def predict(url):
    load_models()

    if model is None:
        raise Exception("Model not loaded")

    data = featureExtraction(url)

    if pca:
        data = pca.transform(data)

    pred = model.predict(data)[0]
    prob = model.predict_proba(data)[0].max()

    return {
        "prediction_label": int(pred),
        "prediction_score": round(prob * 100, 2),
    }


# ==============================
# DEBUG ROUTE
# ==============================
@app.route("/test")
def test():
    try:
        load_models()
        return "✅ Server + Model Loaded Successfully"
    except Exception as e:
        return f"❌ Error: {str(e)}"


# ==============================
# MAIN ROUTE
# ==============================
@app.route("/", methods=["GET", "POST"])
def index():
    url = request.args.get("url")
    data = None
    report = None
    answer = None

    try:
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

    except Exception as e:
        return f"❌ ERROR: {str(e)}"

    return render_template(
        "index.html",
        url=url,
        data=data,
        report=report,
        answer=answer
    )


# ==============================
# COMPLAINT ROUTE
# ==============================
@app.route("/complaint", methods=["POST"])
def complaint():
    try:
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
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
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
"""

        if filename:
            with app.open_resource(os.path.join(app.config["UPLOAD_FOLDER"], filename)) as fp:
                msg.attach(filename, "image/png", fp.read())

        mail.send(msg)

        flash("✅ Complaint sent successfully!", "success")

    except Exception as e:
        return f"❌ Complaint Error: {str(e)}"

    return redirect(url_for("index", url=url))


# ❌ DO NOT USE app.run() for Render
