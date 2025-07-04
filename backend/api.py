from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import faiss
import json
import torch
import numpy as np
from transformers import CLIPModel, CLIPProcessor

app = FastAPI()

# --- CORS for local React dev ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load FAISS index and metadata ---
faiss_index = faiss.read_index("data/embeddings/clip_image_index.faiss")
with open("data/embeddings/image_id_mapping.json") as f:
    id_map = json.load(f)
with open("data/visual_features_gemini.json") as f:
    visual_tags = {entry["title"]: entry for entry in json.load(f)}
with open("data/paintings_with_local_paths.json") as f:
    paintings_info = {entry["title"]: entry for entry in json.load(f)}

# --- Load CLIP model ---
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").eval()
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# --- Query model ---
@app.get("/search")
def search(query: str = Query(...), top_k: int = 5):
    inputs = processor(text=query, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        text_features = model.get_text_features(**inputs)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        vector = text_features.cpu().numpy().astype("float32")

    D, I = faiss_index.search(vector, top_k)  # Search the FAISS index

    results = []
    for idx in I[0]:
        item = id_map.get(str(idx), {})
        title = item.get("title")
        tags_entry = visual_tags.get(title, {})
        tags = tags_entry.get("symbolic_tags", {})
        description = tags_entry.get("description", "")

        # Get author from paintings_with_local_paths.json
        author = paintings_info.get(title, {}).get("artist")

        results.append({
            "title": title,
            "author": author,
            "description": description,
            "image_path": item.get("image_path"),
            "symbolic_tags": tags
        })

    return {"results": results}
