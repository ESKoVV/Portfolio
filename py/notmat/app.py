import warnings
warnings.filterwarnings("ignore")

import os
import queue
import json
import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from resemblyzer import VoiceEncoder, preprocess_wav
from scipy.spatial.distance import cosine
import pygame

MODEL_PATH = "vosk-model-small-ru-0.22"
BADWORDS_FILE = "badwords.txt"

PROFILES_FILES = ["profiles.npz", "profiles_ilyusha.npz"]  # <-- оба файла
SOUND_FILE = "notmat.mp3"

SR = 16000
BLOCKSIZE = 8000
AUDIO_SECONDS_BUFFER = 6
CHUNK_FOR_SPEAKER_SEC = 2.5
CONFIDENCE_THRESHOLD = 0.45

q = queue.Queue()
ring = np.zeros(SR * AUDIO_SECONDS_BUFFER, dtype=np.int16)
ring_pos = 0

encoder = VoiceEncoder()


def init_sound():
    if not os.path.exists(SOUND_FILE):
        raise FileNotFoundError(f"Не найден {SOUND_FILE} рядом со скриптом.")
    pygame.mixer.init()
    pygame.mixer.music.load(SOUND_FILE)


def play_sound():
    pygame.mixer.music.stop()
    pygame.mixer.music.play()


def load_bad_words(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]


def load_profiles_from_files(paths):
    profiles = {}
    found_any = False

    for p in paths:
        if not os.path.exists(p):
            continue
        data = np.load(p)
        for k in data.files:
            profiles[k] = data[k]
        found_any = True

    if not found_any:
        raise FileNotFoundError(
            "Не найдены файлы профилей. Запусти calibrate_main.py и calibrate_ilyusha.py."
        )

    return profiles


def callback(indata, frames, time, status):
    global ring_pos
    raw = indata[:, 0].copy()
    q.put(raw)

    n = len(raw)
    end = ring_pos + n
    if end <= len(ring):
        ring[ring_pos:end] = raw
    else:
        part = len(ring) - ring_pos
        ring[ring_pos:] = raw[:part]
        ring[: end - len(ring)] = raw[part:]
    ring_pos = (ring_pos + n) % len(ring)


def get_last_seconds(sec: float) -> np.ndarray:
    n = int(SR * sec)
    n = min(n, len(ring))
    start = (ring_pos - n) % len(ring)
    if start < ring_pos:
        return ring[start:ring_pos].copy()
    return np.concatenate([ring[start:], ring[:ring_pos]]).copy()


def to_float_wav(int16_audio: np.ndarray) -> np.ndarray:
    return (int16_audio.astype(np.float32) / 32768.0).clip(-1, 1)


def embed_voice(int16_audio: np.ndarray) -> np.ndarray:
    wav = to_float_wav(int16_audio)
    wav = preprocess_wav(wav, source_sr=SR)
    return encoder.embed_utterance(wav)


def predict_speaker(profiles, int16_audio: np.ndarray):
    emb = embed_voice(int16_audio)
    best_name, best_score = None, 1e9
    for name, ref in profiles.items():
        d = cosine(emb, ref)
        if d < best_score:
            best_score = d
            best_name = name
    return best_name, best_score


def main():
    init_sound()

    bad_words = load_bad_words(BADWORDS_FILE)
    profiles = load_profiles_from_files(PROFILES_FILES)

    # статистика по всем, кто есть в профилях
    stats = {name: 0 for name in profiles.keys()}

    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, SR)

    print(f"Загружено матов: {len(bad_words)}")
    print("Профили:", ", ".join(sorted(profiles.keys())))
    print("Слушаю... Скажи 'маты' для статистики.\n")

    with sd.InputStream(
        samplerate=SR,
        blocksize=BLOCKSIZE,
        dtype=np.int16,
        channels=1,
        callback=callback,
    ):
        while True:
            audio_block = q.get()
            if rec.AcceptWaveform(audio_block.tobytes()):
                result = json.loads(rec.Result())
                text = result.get("text", "").lower()
                if not text:
                    continue

                if "маты" in text:
                    print("📊 Статистика:")
                    for name in sorted(stats.keys()):
                        print(f"  {name}: {stats[name]}")
                    print()
                    continue

                if any(w in text for w in bad_words):
                    play_sound()

                    sample = get_last_seconds(CHUNK_FOR_SPEAKER_SEC)
                    who, score = predict_speaker(profiles, sample)

                    if who is not None and score < CONFIDENCE_THRESHOLD:
                        stats[who] += 1
                        print(f"🤬 Мат: {who} (score={score:.3f}) | {text}")
                    else:
                        print(f"🤬 Мат, но не уверен кто (score={score:.3f}) | {text}")


if __name__ == "__main__":
    main()
