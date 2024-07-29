from flask import Flask, request, jsonify
import joblib
import numpy as np
import firebase_admin 
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate('./phishguard-ai-firebase-adminsdk-cxyzs-8d22fd311e.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

# Load the model
model = joblib.load('phishing_model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    url = data.get('url')
    url_features = np.array(data['features']).reshape(1, -1)
    prediction = model.predict(url_features)

    if prediction[0] == 0:
        # Check if the URL exists in the Firebase collection
        phishing_sites_ref = db.collection('phishing_sites')
        query = phishing_sites_ref.where('url', '==', url).stream()

        if any(doc.to_dict() for doc in query):
            return jsonify({'prediction': 1})
        else:
            return jsonify({'prediction': 0})

    else:
        return jsonify({'prediction': 1})


if __name__ == '__main__':
    app.run(debug=True)
