import os
from typing import Optional
from TTS.api import TTS
import torch


class CoquiTTS:
    
    def __init__(
        self, 
        model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    ):

        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Inicializando Coqui TTS con modelo: {model_name}")
        print(f"Usando dispositivo: {self.device}")

        try:
            self.tts = TTS(model_name).to(self.device)
            print("Modelo cargado exitosamente")
        except Exception as e:
            print(f"Error al cargar el modelo: {e}")
            raise

    def synthesize(
        self,
        text: str,
        output_path: str,
        speaker_wav: Optional[str] = None,
        language: str = "es"
    ) -> str:

        print(f"\nSintetizando texto: '{text[:50]}...'")
        print(f"Idioma: {language}")

        try:
            # Crear directorio de salida si no existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if speaker_wav:
                print(f"Usando referencia de voz: {speaker_wav}")
                # Clonacion de voz con archivo de referencia
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    speaker_wav=speaker_wav,
                    language=language
                )
            else:
                
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    language=language
                )

            print(f"Audio generado exitosamente: {output_path}")
            return output_path

        except Exception as e:
            print(f"Error durante la s�ntesis: {e}")
            raise

    def list_speakers(self):

        if hasattr(self.tts, 'speakers') and self.tts.speakers:
            print("\nHablantes disponibles:")
            for speaker in self.tts.speakers:
                print(f"  - {speaker}")
        else:
            print("Este modelo no tiene hablantes predefinidos")

    def list_languages(self):

        if hasattr(self.tts, 'languages') and self.tts.languages:
            print("\nIdiomas disponibles:")
            for lang in self.tts.languages:
                print(f"  - {lang}")
        else:
            print("Este modelo no tiene idiomas predefinidos")
