import json
import faiss
# import numpy as np
import torch
from transformers import CLIPProcessor, CLIPModel

# --- CONFIG ---
INDEX_FILE = "data/embeddings/clip_image_index.faiss"
MAPPING_FILE = "data/embeddings/image_id_mapping.json"
TOP_K = 20  # Number of top matches to return
DEVICE = "cpu"

# --- Load FAISS index ---
index = faiss.read_index(INDEX_FILE)

# --- Load mapping (row → painting metadata) ---
with open(MAPPING_FILE, "r") as f:
    id_map = json.load(f)

# --- Load CLIP model and processor ---
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(DEVICE)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# --- Query loop ---
while True:
    query = input("\nEnter a query (or 'q' to quit): ").strip()
    if query.lower() in {"q", "quit", "exit"}:
        break

    # Encode query as CLIP text embedding
    inputs = processor(text=query, return_tensors="pt", padding=True).to(DEVICE)
    with torch.no_grad():
        text_features = model.get_text_features(**inputs)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        vector = text_features.cpu().numpy().astype("float32")

    # Search the FAISS index
    D, I = index.search(vector, TOP_K)

    print(f"\nTop {TOP_K} matches for: '{query}'")
    for rank, idx in enumerate(I[0]):
        meta = id_map.get(str(idx), {})
        print(f"{rank+1}. {meta.get('title')} — {meta.get('image_path')}")
