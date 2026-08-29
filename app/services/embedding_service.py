import logging

import numpy as np
from essentia.standard import (
    MonoLoader,
    TensorflowPredictEffnetDiscogs,
    TensorflowPredictMusiCNN,
    TensorflowPredictMAEST,
    TensorflowPredict2D,
)
import essentia

essentia.log.warningActive = False


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


GENRE_LABELS = [
    "Blues---Boogie Woogie","Blues---Chicago Blues","Blues---Country Blues","Blues---Delta Blues","Blues---Electric Blues","Blues---Harmonica Blues","Blues---Jump Blues","Blues---Louisiana Blues","Blues---Modern Electric Blues","Blues---Piano Blues","Blues---Rhythm & Blues","Blues---Texas Blues",
    "Brass & Military---Brass Band","Brass & Military---Marches","Brass & Military---Military",
    "Children's---Educational","Children's---Nursery Rhymes","Children's---Story",
    "Classical---Baroque","Classical---Choral","Classical---Classical","Classical---Contemporary","Classical---Impressionist","Classical---Medieval","Classical---Modern","Classical---Neo-Classical","Classical---Neo-Romantic","Classical---Opera","Classical---Post-Modern","Classical---Renaissance","Classical---Romantic",
    "Electronic---Abstract","Electronic---Acid","Electronic---Acid House","Electronic---Acid Jazz","Electronic---Ambient","Electronic---Bassline","Electronic---Beatdown","Electronic---Berlin-School","Electronic---Big Beat","Electronic---Bleep","Electronic---Breakbeat","Electronic---Breakcore","Electronic---Breaks","Electronic---Broken Beat","Electronic---Chillwave","Electronic---Chiptune","Electronic---Dance-pop","Electronic---Dark Ambient","Electronic---Darkwave","Electronic---Deep House","Electronic---Deep Techno","Electronic---Disco","Electronic---Disco Polo","Electronic---Donk","Electronic---Downtempo","Electronic---Drone","Electronic---Drum n Bass","Electronic---Dub","Electronic---Dub Techno","Electronic---Dubstep","Electronic---Dungeon Synth","Electronic---EBM","Electronic---Electro","Electronic---Electro House","Electronic---Electroclash","Electronic---Euro House","Electronic---Euro-Disco","Electronic---Eurobeat","Electronic---Eurodance","Electronic---Experimental","Electronic---Freestyle","Electronic---Future Jazz","Electronic---Gabber","Electronic---Garage House","Electronic---Ghetto","Electronic---Ghetto House","Electronic---Glitch","Electronic---Goa Trance","Electronic---Grime","Electronic---Halftime","Electronic---Hands Up","Electronic---Happy Hardcore","Electronic---Hard House","Electronic---Hard Techno","Electronic---Hard Trance","Electronic---Hardcore","Electronic---Hardstyle","Electronic---Hi NRG","Electronic---Hip Hop","Electronic---Hip-House","Electronic---House","Electronic---IDM","Electronic---Illbient","Electronic---Industrial","Electronic---Italo House","Electronic---Italo-Disco","Electronic---Italodance","Electronic---Jazzdance","Electronic---Juke","Electronic---Jumpstyle","Electronic---Jungle","Electronic---Latin","Electronic---Leftfield","Electronic---Makina","Electronic---Minimal","Electronic---Minimal Techno","Electronic---Modern Classical","Electronic---Musique Concrète","Electronic---Neofolk","Electronic---New Age","Electronic---New Beat","Electronic---New Wave","Electronic---Noise","Electronic---Nu-Disco","Electronic---Power Electronics","Electronic---Progressive Breaks","Electronic---Progressive House","Electronic---Progressive Trance","Electronic---Psy-Trance","Electronic---Rhythmic Noise","Electronic---Schranz","Electronic---Sound Collage","Electronic---Speed Garage","Electronic---Speedcore","Electronic---Synth-pop","Electronic---Synthwave","Electronic---Tech House","Electronic---Tech Trance","Electronic---Techno","Electronic---Trance","Electronic---Tribal","Electronic---Tribal House","Electronic---Trip Hop","Electronic---Tropical House","Electronic---UK Garage","Electronic---Vaporwave",
    "Folk, World, & Country---African","Folk, World, & Country---Bluegrass","Folk, World, & Country---Cajun","Folk, World, & Country---Canzone Napoletana","Folk, World, & Country---Catalan Music","Folk, World, & Country---Celtic","Folk, World, & Country---Country","Folk, World, & Country---Fado","Folk, World, & Country---Flamenco","Folk, World, & Country---Folk","Folk, World, & Country---Gospel","Folk, World, & Country---Highlife","Folk, World, & Country---Hillbilly","Folk, World, & Country---Hindustani","Folk, World, & Country---Honky Tonk","Folk, World, & Country---Indian Classical","Folk, World, & Country---Laïkó","Folk, World, & Country---Nordic","Folk, World, & Country---Pacific","Folk, World, & Country---Polka","Folk, World, & Country---Raï","Folk, World, & Country---Romani","Folk, World, & Country---Soukous","Folk, World, & Country---Séga","Folk, World, & Country---Volksmusik","Folk, World, & Country---Zouk","Folk, World, & Country---Éntekhno",
    "Funk / Soul---Afrobeat","Funk / Soul---Boogie","Funk / Soul---Contemporary R&B","Funk / Soul---Disco","Funk / Soul---Free Funk","Funk / Soul---Funk","Funk / Soul---Gospel","Funk / Soul---Neo Soul","Funk / Soul---New Jack Swing","Funk / Soul---P.Funk","Funk / Soul---Psychedelic","Funk / Soul---Rhythm & Blues","Funk / Soul---Soul","Funk / Soul---Swingbeat","Funk / Soul---UK Street Soul",
    "Hip Hop---Bass Music","Hip Hop---Boom Bap","Hip Hop---Bounce","Hip Hop---Britcore","Hip Hop---Cloud Rap","Hip Hop---Conscious","Hip Hop---Crunk","Hip Hop---Cut-up/DJ","Hip Hop---DJ Battle Tool","Hip Hop---Electro","Hip Hop---G-Funk","Hip Hop---Gangsta","Hip Hop---Grime","Hip Hop---Hardcore Hip-Hop","Hip Hop---Horrorcore","Hip Hop---Instrumental","Hip Hop---Jazzy Hip-Hop","Hip Hop---Miami Bass","Hip Hop---Pop Rap","Hip Hop---Ragga HipHop","Hip Hop---RnB/Swing","Hip Hop---Screw","Hip Hop---Thug Rap","Hip Hop---Trap","Hip Hop---Trip Hop","Hip Hop---Turntablism",
    "Jazz---Afro-Cuban Jazz","Jazz---Afrobeat","Jazz---Avant-garde Jazz","Jazz---Big Band","Jazz---Bop","Jazz---Bossa Nova","Jazz---Contemporary Jazz","Jazz---Cool Jazz","Jazz---Dixieland","Jazz---Easy Listening","Jazz---Free Improvisation","Jazz---Free Jazz","Jazz---Fusion","Jazz---Gypsy Jazz","Jazz---Hard Bop","Jazz---Jazz-Funk","Jazz---Jazz-Rock","Jazz---Latin Jazz","Jazz---Modal","Jazz---Post Bop","Jazz---Ragtime","Jazz---Smooth Jazz","Jazz---Soul-Jazz","Jazz---Space-Age","Jazz---Swing",
    "Latin---Afro-Cuban","Latin---Baião","Latin---Batucada","Latin---Beguine","Latin---Bolero","Latin---Boogaloo","Latin---Bossanova","Latin---Cha-Cha","Latin---Charanga","Latin---Compas","Latin---Cubano","Latin---Cumbia","Latin---Descarga","Latin---Forró","Latin---Guaguancó","Latin---Guajira","Latin---Guaracha","Latin---MPB","Latin---Mambo","Latin---Mariachi","Latin---Merengue","Latin---Norteño","Latin---Nueva Cancion","Latin---Pachanga","Latin---Porro","Latin---Ranchera","Latin---Reggaeton","Latin---Rumba","Latin---Salsa","Latin---Samba","Latin---Son","Latin---Son Montuno","Latin---Tango","Latin---Tejano","Latin---Vallenato",
    "Non-Music---Audiobook","Non-Music---Comedy","Non-Music---Dialogue","Non-Music---Education","Non-Music---Field Recording","Non-Music---Interview","Non-Music---Monolog","Non-Music---Poetry","Non-Music---Political","Non-Music---Promotional","Non-Music---Radioplay","Non-Music---Religious","Non-Music---Spoken Word",
    "Pop---Ballad","Pop---Bollywood","Pop---Bubblegum","Pop---Chanson","Pop---City Pop","Pop---Europop","Pop---Indie Pop","Pop---J-pop","Pop---K-pop","Pop---Kayōkyoku","Pop---Light Music","Pop---Music Hall","Pop---Novelty","Pop---Parody","Pop---Schlager","Pop---Vocal",
    "Reggae---Calypso","Reggae---Dancehall","Reggae---Dub","Reggae---Lovers Rock","Reggae---Ragga","Reggae---Reggae","Reggae---Reggae-Pop","Reggae---Rocksteady","Reggae---Roots Reggae","Reggae---Ska","Reggae---Soca",
    "Rock---AOR","Rock---Acid Rock","Rock---Acoustic","Rock---Alternative Rock","Rock---Arena Rock","Rock---Art Rock","Rock---Atmospheric Black Metal","Rock---Avantgarde","Rock---Beat","Rock---Black Metal","Rock---Blues Rock","Rock---Brit Pop","Rock---Classic Rock","Rock---Coldwave","Rock---Country Rock","Rock---Crust","Rock---Death Metal","Rock---Deathcore","Rock---Deathrock","Rock---Depressive Black Metal","Rock---Doo Wop","Rock---Doom Metal","Rock---Dream Pop","Rock---Emo","Rock---Ethereal","Rock---Experimental","Rock---Folk Metal","Rock---Folk Rock","Rock---Funeral Doom Metal","Rock---Funk Metal","Rock---Garage Rock","Rock---Glam","Rock---Goregrind","Rock---Goth Rock","Rock---Gothic Metal","Rock---Grindcore","Rock---Grunge","Rock---Hard Rock","Rock---Hardcore","Rock---Heavy Metal","Rock---Indie Rock","Rock---Industrial","Rock---Krautrock","Rock---Lo-Fi","Rock---Lounge","Rock---Math Rock","Rock---Melodic Death Metal","Rock---Melodic Hardcore","Rock---Metalcore","Rock---Mod","Rock---Neofolk","Rock---New Wave","Rock---No Wave","Rock---Noise","Rock---Noisecore","Rock---Nu Metal","Rock---Oi","Rock---Parody","Rock---Pop Punk","Rock---Pop Rock","Rock---Pornogrind","Rock---Post Rock","Rock---Post-Hardcore","Rock---Post-Metal","Rock---Post-Punk","Rock---Power Metal","Rock---Power Pop","Rock---Power Violence","Rock---Prog Rock","Rock---Progressive Metal","Rock---Psychedelic Rock","Rock---Psychobilly","Rock---Pub Rock","Rock---Punk","Rock---Rock & Roll","Rock---Rockabilly","Rock---Shoegaze","Rock---Ska","Rock---Sludge Metal","Rock---Soft Rock","Rock---Southern Rock","Rock---Space Rock","Rock---Speed Metal","Rock---Stoner Rock","Rock---Surf","Rock---Symphonic Rock","Rock---Technical Death Metal","Rock---Thrash","Rock---Twist","Rock---Viking Metal","Rock---Yé-Yé",
    "Stage & Screen---Musical","Stage & Screen---Score","Stage & Screen---Soundtrack","Stage & Screen---Theme"
]


class MainEmbeddingService(metaclass=_Singleton):
    EFFNET_MODEL = '/models/discogs-effnet-bs64-1.pb'
    MUSICNN_MODEL = '/models/msd-musicnn-1.pb'

    MOOD_MODELS = {
        'happy':      '/models/mood_happy-discogs-effnet-1.pb',
        'sad':        '/models/mood_sad-discogs-effnet-1.pb',
        'aggressive': '/models/mood_aggressive-discogs-effnet-1.pb',
        'relaxed':    '/models/mood_relaxed-discogs-effnet-1.pb',
        'party':      '/models/mood_party-discogs-effnet-1.pb',
    }
    DANCEABILITY_MODEL = '/models/danceability-discogs-effnet-1.pb'
    DEAM_MODEL = '/models/deam-msd-musicnn-2.pb'
    VOICE_INSTRUMENTAL_MODEL = '/models/voice_instrumental-discogs-effnet-1.pb'
    TIMBRE_MODEL = '/models/timbre-discogs-effnet-1.pb'
    APPROACHABILITY_MODEL = '/models/approachability_regression-discogs-effnet-1.pb'
    ENGAGEMENT_MODEL = '/models/engagement_regression-discogs-effnet-1.pb'
    GENRE_MODEL = '/models/genre_discogs400-discogs-effnet-1.pb'

    def __init__(self):
        self.effnet_model = TensorflowPredictEffnetDiscogs(
            graphFilename=self.EFFNET_MODEL,
            output="PartitionedCall:1"
        )
        self.musicnn_model = TensorflowPredictMusiCNN(
            graphFilename=self.MUSICNN_MODEL,
            output="model/dense/BiasAdd"
        )
        self.mood_models = {
            mood: TensorflowPredict2D(graphFilename=path, output="model/Softmax")
            for mood, path in self.MOOD_MODELS.items()
        }
        self.danceability_model = TensorflowPredict2D(
            graphFilename=self.DANCEABILITY_MODEL,
            output="model/Softmax"
        )
        self.deam_model = TensorflowPredict2D(
            graphFilename=self.DEAM_MODEL,
            output="model/Identity"
        )
        self.voice_instrumental_model = TensorflowPredict2D(
            graphFilename=self.VOICE_INSTRUMENTAL_MODEL,
            output="model/Softmax"
        )
        self.timbre_model = TensorflowPredict2D(
            graphFilename=self.TIMBRE_MODEL,
            output="model/Softmax"
        )
        self.approachability_model = TensorflowPredict2D(
            graphFilename=self.APPROACHABILITY_MODEL,
            output="model/Identity"
        )
        self.engagement_model = TensorflowPredict2D(
            graphFilename=self.ENGAGEMENT_MODEL,
            output="model/Identity"
        )
        self.genre_model = TensorflowPredict2D(
            graphFilename=self.GENRE_MODEL,
            input="serving_default_model_Placeholder",
            output="PartitionedCall:0"
        )

    def _load_audio(self, file_path: str):
        return MonoLoader(filename=file_path, sampleRate=16000, resampleQuality=4)()

    def compute_audio_embeddings(self, file_path: str):
        logging.info(f"Computing embeddings for file {file_path}")
        audio = self._load_audio(file_path)
        logging.info(f"Audio loaded, shape: {audio.shape}")
        effnet_emb = self.effnet_model(audio)
        logging.info(f"Effnet embedding computed, shape: {effnet_emb.shape}")
        musicnn_emb = self.musicnn_model(audio)
        logging.info(f"MusiCNN embedding computed, shape: {musicnn_emb.shape}")

        mood = {
            mood: float(model(effnet_emb).mean(axis=0)[1])
            for mood, model in self.mood_models.items()
        }
        logging.info(f"Mood predictions: {mood}")
        danceability = float(self.danceability_model(effnet_emb).mean(axis=0)[1])
        arousal_valence = self.deam_model(musicnn_emb).mean(axis=0)
        valence = float(arousal_valence[0])
        arousal = float(arousal_valence[1])

        logging.info(f"Danceability: {danceability}, Valence: {valence}, Arousal: {arousal}")

        voice_instrumental = float(self.voice_instrumental_model(effnet_emb).mean(axis=0)[1])
        timbre = float(self.timbre_model(effnet_emb).mean(axis=0)[1])
        approachability = float(self.approachability_model(effnet_emb).mean(axis=0)[0])
        engagement = float(self.engagement_model(effnet_emb).mean(axis=0)[0])

        logging.info(f"Voice/Instrumental: {voice_instrumental}, Timbre: {timbre}, Approachability: {approachability}, Engagement: {engagement}")

        genre_scores = self.genre_model(effnet_emb).mean(axis=0)
        top_genre_indices = genre_scores.argsort()[-5:][::-1]
        genre = {GENRE_LABELS[i]: float(genre_scores[i]) for i in top_genre_indices}

        logging.info(f"Top genres: {genre}")

        return {
            "vectors": {
                "discogs": effnet_emb.mean(axis=0).tolist(),
                "musicnn": musicnn_emb.mean(axis=0).tolist(),
                "mood": list(mood.values()),
                "arousal_valence": [valence, arousal],
            },
            "features": {
                "mood": mood,
                "danceability": danceability,
                "valence": valence,
                "arousal": arousal,
                "voice": voice_instrumental,
                "timbre_dark": timbre,
                "approachability": approachability,
                "engagement": engagement,
                "genre": genre,
            }
        }


class MaestEmbeddingService(metaclass=_Singleton):
    MAEST_MODEL = '/models/discogs-maest-30s-pw-2.pb'

    def __init__(self):
        self.maest_model = TensorflowPredictMAEST(
            graphFilename=self.MAEST_MODEL,
            output="PartitionedCall/Identity_7"
        )

    def _load_audio(self, file_path: str):
        return MonoLoader(filename=file_path, sampleRate=16000, resampleQuality=4)()

    def compute_maest_embedding(self, file_path: str):
        audio = self._load_audio(file_path)
        output = self.maest_model(audio)[0]
        output = output.mean(axis=0)
        cls = output[0]
        dist = output[1]
        signal_mean = output[2:].mean(axis=0)
        maest_emb = np.concatenate([cls, dist, signal_mean])
        return {"vectors": {"maest": maest_emb.tolist()}}
