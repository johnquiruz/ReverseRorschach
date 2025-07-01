import os
import json
import numpy as np
from PIL import Image
from tqdm import tqdm
import torch
import clip

# CONFIGURATION 
IMAGE_DIR = "images"
OUTPUT_EMBEDDINGS = "data/embeddings/clip_image_embeddings.npy"
OUTPUT_INDEX = "data/embeddings/image_index.json"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# LOAD MODEL
model, preprocess = clip.load("ViT-B/32", device=DEVICE)
model.eval()


# LOAD PAINTING IMAGES JSON
with open("data/paintings_with_local_paths.json", "r") as f:
    paintings = json.load(f)


# CREATE EMBEDDING STORAGE
embeddings = []
index = {}


# PROCESS EACH IMAGE
for i, painting in enumerate(tqdm(paintings)):
    image_path = painting.get("local_path")
    if not image_path or not os.path.exists(image_path):
        continue

    try:
        image = preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0).to(DEVICE)
        with torch.no_grad():
            image_features = model.encode_image(image)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        embeddings.append(image_features.cpu().numpy()[0])
        index[image_path] = len(embeddings) - 1
    except Exception as e:
        print(f"Failed to process {image_path}: {e}")


# SAVE OUTPUTS
os.makedirs(os.path.dirname(OUTPUT_EMBEDDINGS), exist_ok=True)
np.save(OUTPUT_EMBEDDINGS, np.array(embeddings, dtype=np.float32))

with open(OUTPUT_INDEX, "w") as f:
    json.dump(index, f, indent=2)

print(f"Saved {len(embeddings)} embeddings to {OUTPUT_EMBEDDINGS}")