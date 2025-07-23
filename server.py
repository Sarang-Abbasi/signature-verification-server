from flask import Flask, request, jsonify
from flask_cors import CORS
from predict_one_image import predict_and_store
import os

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files or "user_id" not in request.form:
        return jsonify({"status": "error", "message": "Missing file or user_id"}), 400

    file = request.files["file"]
    user_id = request.form["user_id"]
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    result = predict_and_store(save_path, user_id)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
