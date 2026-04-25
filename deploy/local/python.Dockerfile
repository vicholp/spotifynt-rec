FROM python:3.12.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget

WORKDIR /models

RUN wget https://essentia.upf.edu/models/feature-extractors/discogs-effnet/discogs-effnet-bs64-1.pb

RUN wget https://essentia.upf.edu/models/classification-heads/danceability/danceability-discogs-effnet-1.pb
RUN wget https://essentia.upf.edu/models/classification-heads/mood_happy/mood_happy-discogs-effnet-1.pb
RUN wget https://essentia.upf.edu/models/classification-heads/mood_sad/mood_sad-discogs-effnet-1.pb
RUN wget https://essentia.upf.edu/models/classification-heads/mood_relaxed/mood_relaxed-discogs-effnet-1.pb
RUN wget https://essentia.upf.edu/models/classification-heads/mood_aggressive/mood_aggressive-discogs-effnet-1.pb
RUN wget https://essentia.upf.edu/models/classification-heads/mood_party/mood_party-discogs-effnet-1.pb

RUN wget https://essentia.upf.edu/models/classification-heads/deam/deam-msd-musicnn-2.pb
RUN wget https://essentia.upf.edu/models/feature-extractors/musicnn/msd-musicnn-1.pb

RUN wget https://essentia.upf.edu/models/feature-extractors/maest/discogs-maest-30s-pw-2.pb

RUN wget https://essentia.upf.edu/models/classification-heads/voice_instrumental/voice_instrumental-discogs-effnet-1.pb
RUN wget https://essentia.upf.edu/models/classification-heads/timbre/timbre-discogs-effnet-1.pb
RUN wget https://essentia.upf.edu/models/classification-heads/approachability/approachability_regression-discogs-effnet-1.pb
RUN wget https://essentia.upf.edu/models/classification-heads/engagement/engagement_regression-discogs-effnet-1.pb
RUN wget https://essentia.upf.edu/models/classification-heads/genre_discogs400/genre_discogs400-discogs-effnet-1.pb

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
