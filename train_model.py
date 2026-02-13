import json
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.join(BASE_DIR, "data", "job_roles.json")
model_dir = os.path.join(BASE_DIR, "model")

os.makedirs(model_dir, exist_ok=True)

with open(data_path, "r", encoding="utf-8") as f:
    job_roles = json.load(f)

X = []
y = []

for role, skills in job_roles.items():
    X.append(" ".join(skills))
    y.append(role)

vectorizer = TfidfVectorizer()
X_vec = vectorizer.fit_transform(X)

model = LogisticRegression()
model.fit(X_vec, y)

with open(os.path.join(model_dir, "role_model.pkl"), "wb") as f:
    pickle.dump(model, f)

with open(os.path.join(model_dir, "vectorizer.pkl"), "wb") as f:
    pickle.dump(vectorizer, f)

print("Model trained and saved successfully")
