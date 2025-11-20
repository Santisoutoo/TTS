import os
from TTS.api import TTS
import torch


class XTTS:

    def __init__(self):

        self.model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"Inicializando XTTS v2")
        print(f"Modelo: {self.model_name}")
        print(f"Dispositivo: {self.device}")

        try:
            self.tts = TTS(self.model_name).to(self.device)
            print("Modelo XTTS v2 cargado exitosamente")
        except Exception as e:
            print(f"Error al cargar XTTS v2: {e}")
            raise

    def synthesize(
        self,
        text: str,
        output_path: str,
        speaker_wav: str,
        language: str = "en"
    ) -> str:

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            self.tts.tts_to_file(
                text=text,
                file_path=output_path,
                speaker_wav=speaker_wav,
                language=language
            )

            print(f"✓ Audio generado exitosamente: {output_path}")
            return output_path

        except Exception as e:
            print(f"✗ Error durante la síntesis: {e}")
            raise

    def list_languages(self):

        if hasattr(self.tts, 'languages') and self.tts.languages:
            print("\nIdiomas disponibles en XTTS v2:")
            for lang in self.tts.languages:
                print(f"  - {lang}")
        else:
            print("XTTS v2 soporta: en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja, ko, hu")
