import os
from typing import Optional
from TTS.api import TTS
import torch


class YourTTS:
    """
    Clase para clonación de voz usando el modelo YourTTS.
    YourTTS es un modelo multilingüe que soporta clonación de voz zero-shot.
    """

    def __init__(self):
        """
        Inicializa el modelo YourTTS
        """
        self.model_name = "tts_models/multilingual/multi-dataset/your_tts"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"Inicializando YourTTS")
        print(f"Modelo: {self.model_name}")
        print(f"Dispositivo: {self.device}")

        try:
            self.tts = TTS(self.model_name).to(self.device)
            print("Modelo YourTTS cargado exitosamente")
        except Exception as e:
            print(f"Error al cargar YourTTS: {e}")
            raise

    def synthesize(
        self,
        text: str,
        output_path: str,
        speaker_wav: str,
        language: str = "en"
    ) -> str:
        """
        Sintetiza voz clonando el audio de referencia.

        Args:
            text: Texto a sintetizar
            output_path: Ruta donde guardar el audio generado
            speaker_wav: Ruta al audio de referencia para clonación de voz
            language: Código de idioma (en, es, fr, pt, etc.)

        Returns:
            Ruta al archivo de audio generado
        """
        print(f"\n=== Sintetizando con YourTTS ===")
        print(f"Texto: '{text[:70]}...'")
        print(f"Idioma: {language}")
        print(f"Audio de referencia: {speaker_wav}")

        try:
            # Crear directorio de salida si no existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Clonación de voz con archivo de referencia
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
        """
        Lista los idiomas soportados por el modelo
        """
        if hasattr(self.tts, 'languages') and self.tts.languages:
            print("\nIdiomas disponibles en YourTTS:")
            for lang in self.tts.languages:
                print(f"  - {lang}")
        else:
            print("No se pueden listar los idiomas del modelo")
