import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import os
import hashlib

from BlockchainConfig import store_signature_result

# === CONFIG ===
IMG_SIZE = 224
MODEL_PATH = r"C:\Users\SARANG\AndroidStudioProjects\signature_Backend\model\model_CNN_CombinedDataset_2025-07-23_02-17-13.pth"
IMAGE_PATH = r"C:\Users\Project\Desktop\Project\Project\test_image.jpg"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
class_names = ['Genuine', 'Forged']

# === CNN Model
class CNN(nn.Module):
    def __init__(self, num_classes=2):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(64 * 56 * 56, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, num_classes)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = x.view(-1, 64 * 56 * 56)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# === Load Model
model = CNN(num_classes=2)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.eval()
model.to(DEVICE)

# === Image Transform
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

def predict_image(image_path):
    image = Image.open(image_path).convert('RGB')
    input_tensor = transform(image).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        output = model(input_tensor)
        probs = torch.nn.functional.softmax(output, dim=1)
        prediction = torch.argmax(probs, dim=1).item()
        confidence = probs[0][prediction].item()
    return class_names[prediction], confidence

# === Main Logic
try:
    label, confidence = predict_image(IMAGE_PATH)
    symbol = "✅" if label == "Genuine" else "❌"
    print(f"{symbol} {IMAGE_PATH}: {label} Signature ({confidence * 100:.2f}%)")

    user_id = input("Enter user ID to store on blockchain: ").strip()
    random_bytes = os.urandom(32)
    sha256_hash = hashlib.sha256(random_bytes).hexdigest()
    print(f"Generated hash: {sha256_hash}")

    try:
        store_signature_result(user_id, label, sha256_hash,)  # label is 'Genuine' or 'Forged'
        print("✅ Record successfully stored on blockchain!")
    except Exception as e:
        print("❌ Error storing to blockchain:", e)

except Exception as e:
    print(f"⚠️ Error processing image: {e}")

def predict_and_store(image_path, user_id):
    label, confidence = predict_image(image_path)

    random_bytes = os.urandom(32)
    sha256_hash = hashlib.sha256(random_bytes).hexdigest()

    try:
        store_signature_result(user_id, label, sha256_hash)
        return {
            "status": "success",
            "label": label,
            "confidence": round(confidence * 100, 2),
            "transaction_hash": sha256_hash
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
