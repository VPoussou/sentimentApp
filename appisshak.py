from flask import Flask, request, render_template, jsonify
from flask_mail import Mail, Message
from transformers import pipeline
import os


app = Flask(__name__)

app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''  
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465  # Utilisation du port SSL
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

API_TOKEN = ""

@app.before_request
def check_token():
    token = request.headers.get('Authorization')
    if token != f"Bearer {API_TOKEN}":
        return jsonify({"error": "Unauthorized access"}), 403
    
# Charger le pipeline d'analyse de sentiment
sentiment_analysis = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

@app.route('/')
def home():
    return '''
        <html>
            <head>
                <style>
                    body {
                        font-family: 'Arial', sans-serif;
                        background-color: #f7f7f7;
                        margin: 0;
                        padding: 0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                    }
                    .container {
                        background-color: white;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                        width: 100%;
                        max-width: 600px;
                        text-align: center;
                    }
                    h2 {
                        color: #333;
                        font-size: 2em;
                        margin-bottom: 20px;
                    }
                    textarea {
                        width: 100%;
                        height: 150px;
                        padding: 10px;
                        font-size: 1em;
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        resize: none;
                    }
                    input[type="submit"] {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        padding: 12px 20px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 1.2em;
                        border-radius: 5px;
                        cursor: pointer;
                        transition: background-color 0.3s;
                    }
                    input[type="submit"]:hover {
                        background-color: #45a049;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Analyse de Sentiment pour AirBNB</h2>
                    <form action="/analyze_sentiment" method="post">
                        <label for="comment">Entrez votre commentaire :</label><br>
                        <textarea name="comment" placeholder="Votre commentaire ici..." required></textarea><br>
                        <input type="submit" value="Envoyer le commentaire">
                    </form>
                </div>
            </body>
        </html>
    '''

@app.route('/analyze_sentiment', methods=['POST'])
def analyze_sentiment():
    # Récupérer les données JSON envoyées dans la requête
    data = request.get_json()

    # Extraire le commentaire du JSON
    comment = data.get('comment', '')

    # Analyse du sentiment du commentaire
    result = sentiment_analysis(comment)
    sentiment = result[0]['label']
    score = result[0]['score']

    # Si le sentiment est négatif, envoyer un email d'alerte
    if sentiment == 'NEGATIVE':
        msg = Message('Alerte de sentiment négatif !',
                      sender='',  # Ton adresse email
                      recipients=[''])  # L'adresse email où envoyer l'alerte
        msg.body = f"Un commentaire négatif a été soumis :\n\nCommentaire : {comment}"
        mail.send(msg)

    # Afficher un message de confirmation à l'utilisateur
    return '''
        <html>
            <head>
                <style>
                    body {
                        font-family: 'Arial', sans-serif;
                        background-color: #f7f7f7;
                        margin: 0;
                        padding: 0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                    }
                    .container {
                        background-color: white;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                        width: 100%;
                        max-width: 600px;
                        text-align: center;
                    }
                    h2 {
                        color: #333;
                        font-size: 2em;
                        margin-bottom: 20px;
                    }
                    p {
                        font-size: 1.2em;
                        color: #555;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Votre commentaire a bien été transmis.</h2>
                    <p>Merci d'avoir soumis votre commentaire sur AirBNB. Nous avons analysé votre sentiment. Si c'était négatif, un email a été envoyé à l'équipe concernée.</p>
                </div>
            </body>
        </html>
    '''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)