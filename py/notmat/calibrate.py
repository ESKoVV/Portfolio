import warnings
warnings.filterwarnings("ignore")

import numpy as np
import sounddevice as sd
from resemblyzer import VoiceEncoder, preprocess_wav

SR = 16000
OUT_FILE = "profiles_ilyusha.npz"
NAME = "Илюша"

encoder = VoiceEncoder()

def to_float_wav(x: np.ndarray) -> np.ndarray:
    return (x.astype(np.float32) / 32768.0).clip(-1, 1)

def embed_voice(int16_audio: np.ndarray) -> np.ndarray:
    wav = to_float_wav(int16_audio)
    wav = preprocess_wav(wav, source_sr=SR)
    return encoder.embed_utterance(wav)

def record(seconds: int) -> np.ndarray:
    audio = sd.rec(int(SR * seconds), samplerate=SR, channels=1, dtype=np.int16)
    sd.wait()
    return audio[:, 0].copy()

def main():
    print("=== Калибровка (Илюша) ===")
    print(f"Сохраним в {OUT_FILE}\n")

    input(f"[{NAME}] Нажми Enter и начинай говорить...")
    print("Запись 30 сек...")
    audio = record(30)

    np.savez(OUT_FILE, **{NAME: embed_voice(audio)})
    print(f"Готово! Профиль сохранён в {OUT_FILE}")

if __name__ == "__main__":
    main()
