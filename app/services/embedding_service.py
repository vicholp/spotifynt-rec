import os
from essentia.standard import MonoLoader, TensorflowPredictEffnetDiscogs, TensorflowPredictMusiCNN
import essentia

essentia.log.warningActive = False

class EmbeddingService:
    EFFNET_MODEL = '/app/discogs-effnet-bs64-1.pb'
    MUSICNN_MODEL = '/app/msd-musicnn-1.pb'

    def __init__(self):
        self.effnet_model = TensorflowPredictEffnetDiscogs(
            graphFilename=self.EFFNET_MODEL,
            output="PartitionedCall:1"
        )
        self.musicnn_model = TensorflowPredictMusiCNN(
            graphFilename=self.MUSICNN_MODEL,
            output="model/dense/BiasAdd"
        )

    def _load_audio(self, file_path: str):
        return MonoLoader(filename=file_path, sampleRate=16000, resampleQuality=4)()

    def compute_embedding_discogs(self, file_path: str):
        try:
            audio = self._load_audio(file_path)
            emb = self.effnet_model(audio).mean(axis=0)
            print(f"OK: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"SKIP: {os.path.basename(file_path)} — {e}")

        return emb

    def compute_embedding_musicnn(self, file_path: str):
        try:
            audio = self._load_audio(file_path)
            emb = self.musicnn_model(audio).mean(axis=0)
            print(f"OK: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"SKIP: {os.path.basename(file_path)} — {e}")

        return emb

    def compute_audio_embeddings(self, file_path: str):
        discogs_emb = self.compute_embedding_discogs(file_path)
        musicnn_emb = self.compute_embedding_musicnn(file_path)

        return {
            "discogs": discogs_emb.tolist(),
            "musicnn": musicnn_emb.tolist()
        }
