import os
import glob
import numpy as np
from essentia.standard import MonoLoader, TensorflowPredictEffnetDiscogs
from sklearn.metrics.pairwise import cosine_similarity
import json

MUSIC_DIR = "music"
EFFNET_MODEL = "discogs-effnet-bs64-1.pb"
PLAYLIST_LENGTH = 10
STARTING_TRACK = "music/09 - Te vistes y te vas.flac"
EMBEDDINGS_FILE = "embeddings.npz"

def compute_embeddings():
    embedding_model = TensorflowPredictEffnetDiscogs(
        graphFilename=EFFNET_MODEL,
        output="PartitionedCall:1"
    )

    files = glob.glob(f"{MUSIC_DIR}/**/*.mp3", recursive=True) + \
            glob.glob(f"{MUSIC_DIR}/**/*.flac", recursive=True)

    embeddings = {}
    for f in files:
        try:
            audio = MonoLoader(filename=f, sampleRate=16000, resampleQuality=4)()
            emb = embedding_model(audio).mean(axis=0)
            embeddings[f] = emb
            print(f"OK: {os.path.basename(f)}")
        except Exception as e:
            print(f"SKIP: {os.path.basename(f)} — {e}")

    # save
    np.savez(EMBEDDINGS_FILE, **{
        str(i): emb for i, emb in enumerate(embeddings.values())
    })
    with open("embeddings_index.json", "w") as f:
        json.dump(list(embeddings.keys()), f)

    return embeddings

def load_embeddings():
    data = np.load(EMBEDDINGS_FILE)
    with open("embeddings_index.json") as f:
        files = json.load(f)
    return {files[int(i)]: data[i] for i in data.files}

# load or compute
if os.path.exists(EMBEDDINGS_FILE):
    print("Loading cached embeddings...")
    embeddings = load_embeddings()
else:
    print("Computing embeddings...")
    embeddings = compute_embeddings()

# build playlist
def build_playlist(start, length=PLAYLIST_LENGTH):
    files = list(embeddings.keys())
    matrix = np.array([embeddings[f] for f in files])
    query = embeddings[start].reshape(1, -1)
    scores = cosine_similarity(query, matrix)[0]
    ranked = sorted(zip(files, scores), key=lambda x: x[1], reverse=True)
    return [f for f, _ in ranked if f != start][:length]

playlist = build_playlist(STARTING_TRACK)
print(f"\nPlaylist starting from: {os.path.basename(STARTING_TRACK)}")
for i, f in enumerate(playlist, 1):
    print(f"  {i}. {os.path.basename(f)}")