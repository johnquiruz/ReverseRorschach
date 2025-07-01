import os
import json
import numpy as np
import faiss

# CONFIGURATION
EMBEDDINGS_FILE = "data/embeddings/clip_image_embeddings.npy"
PAINTING_META_FILE = "data/paintings_with_local_paths.json"
FAISS_INDEX_FILE = "data/embeddings/clip_image_index.faiss"
INDEX_MAPPING_FILE = "data/embeddings/image_id_mapping.json"

# LOAD PAINTING METADATA
embeddings = np.load(EMBEDDINGS_FILE).astype("float32")

# NORMALIZE EMBEDDINGS
embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True) # Normalize to unit length

# CREATE FAISS INDEX
print("Building FAISS index...")
index = faiss.IndexFlatIP(embeddings.shape[1])  # Inner product indexa
index.add(embeddings)  # Add embeddings to the index

# SAVE FAISS INDEX TO DISK
faiss.write_index(index, FAISS_INDEX_FILE)
print(f"FAISS index saved to {FAISS_INDEX_FILE}")

# BUILD MAPPING FROM IMAGE TITLE AND IMAGE PATH TO INDEX
with open(PAINTING_META_FILE, "r") as f:
    paintings = json.load(f)

mapping = {}
for i, painting in enumerate(paintings):
    image_path = painting["local_path"]
    mapping[str(i)] = {
        "title": painting["title"],
        "image_path": image_path
    }

# SAVE INDEX MAPPING TO DISK
with open(INDEX_MAPPING_FILE, "w") as f:
    json.dump(mapping, f, indent=2)
print(f"Index mapping saved to {INDEX_MAPPING_FILE}")