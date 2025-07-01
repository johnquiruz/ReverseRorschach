# import sys
# print(f"Python version: {sys.version}")
# print(f"sys.path: {sys.path}")
# print(f"Python3 executable: {sys.executable}")

import os
import json
import time
import google.generativeai as genai
from PIL import Image
from tqdm import tqdm
from datetime import datetime

# --- CONFIG ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash-lite-preview-06-17"
INPUT_JSON = "data/paintings_with_local_paths.json"
OUTPUT_JSON = "data/visual_features_gemini.json"
PROGRESS_LOG = "logs/gemini_benchmark_log.txt"
os.makedirs("logs", exist_ok=True)

# --- Load model ---
model = genai.GenerativeModel(MODEL)

# --- Prompt template ---
SCHEMA_PROMPT = """
You are an expert in art interpretation.

You will be given a painting (image) and its title. Your task is to:

1. Write a 3–5 sentence description of the painting that captures its visual qualities (e.g., composition, light, color, subject).
2. Classify the painting's visual features using the exact vocabulary below.

Only use the values provided in each category.

(color)
- dominant_hue_family: [HUE_WARM, HUE_COOL, HUE_NEUTRAL]
- brightness_value: [BRIGHT_HIGH_KEY, MEDIUM_MID_TONE, DARK_LOW_KEY]
- saturation_intensity: [VIBRANT_HIGH_SATURATION, MUTED_LOW_SATURATION]

(composition)
- overall_balance: [SYMMETRICAL_STATIC, ASYMMETRICAL_DYNAMIC, UNBALANCED_TENSE]
- dominant_direction: [UPWARD_ASCENDING, DOWNWARD_DESCENDING, HORIZONTAL_STILL, DIAGONAL_MOVEMENT]
- spatial_feeling: [OPEN_EXPANSIVE, CONFINED_ENCLOSED, SPARSE_EMPTY, DENSE_CLUTTERED]

(line_shape)
- dominant_line_quality: [STRAIGHT_GEOMETRIC, CURVED_ORGANIC, JAGGED_BROKEN]
- implied_form: [ANGULAR_RIGID, FLUID_SOFT]

(lighting_shadow)
- light_quality: [BRIGHT_EVEN, DRAMATIC_CONTRAST, DIM_GLOOMY]
- shadow_presence: [PROMINENT_SHADOWS, SUBTLE_SHADOWS, NO_SHADOWS]

(texture_brushwork)
- surface_feel: [SMOOTH_BLENDED, ROUGH_VISIBLE_BRUSHSTROKES]

(subject_matter)
- figure_presence: [FIGURES_PRESENT, FIGURES_ABSENT]
- dominant_setting: [LANDSCAPE_NATURE, URBAN_ARCHITECTURE, INTERIOR_SPACE, ABSTRACT_NONE]

Return your response in this exact JSON format:

{
  "description": "...",
  "symbolic_tags": {
    "color": { ... },
    "composition": { ... },
    "line_shape": { ... },
    "lighting_shadow": { ... },
    "texture_brushwork": { ... },
    "subject_matter": { ... }
  }
}
"""

# --- Load image bytes ---
def load_image_bytes(image_path):
    with open(image_path, "rb") as f:
        return f.read()

# --- Query Gemini with retry ---
def query_gemini(image_path, title, retries=3, delay=2):
    img_bytes = load_image_bytes(image_path)
    prompt = f'{SCHEMA_PROMPT}\n\nPainting title: "{title}"\n'
    
    for attempt in range(retries):
        try:
            start = time.time()
            response = model.generate_content([prompt, img_bytes], generation_config={"temperature": 0.4})
            duration = time.time() - start
            return response.text.strip(), duration
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return f"__ERROR__:{e}", -1

# --- Load input and existing results (resumable) ---
with open(INPUT_JSON, "r") as f:
    paintings = json.load(f)

if os.path.exists(OUTPUT_JSON):
    with open(OUTPUT_JSON, "r") as f:
        results = json.load(f)
    completed_titles = {r["title"] for r in results}
else:
    results = []
    completed_titles = set()

# --- Process paintings ---
log_entries = []
for painting in tqdm(paintings):
    title = painting["title"]
    image_path = painting.get("local_path")

    if title in completed_titles or not image_path or not os.path.exists(image_path):
        continue

    response_text, elapsed = query_gemini(image_path, title)

    log_entries.append(f"[{datetime.now()}] {title} — {elapsed:.2f}s")

    if response_text.startswith("__ERROR__"):
        print(f"Error on '{title}': {response_text[9:]}")
        continue

    try:
        parsed = json.loads(response_text)
        results.append({
            "title": title,
            "image_path": image_path,
            "description": parsed.get("description", ""),
            "symbolic_tags": parsed.get("symbolic_tags", {})
        })

        # Save intermediate state
        with open(OUTPUT_JSON, "w") as f:
            json.dump(results, f, indent=2)
    except Exception as parse_error:
        print(f"Failed to parse JSON for '{title}': {parse_error}")
        continue

# --- Save log ---
with open(PROGRESS_LOG, "w") as f:
    f.write("\n".join(log_entries))

print(f"\n✅ Completed {len(results)} paintings.")
print(f"⏱️  Benchmark log saved to: {PROGRESS_LOG}")
print(f"📁 Output saved to: {OUTPUT_JSON}")
