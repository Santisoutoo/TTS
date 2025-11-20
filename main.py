import argparse
import os
from scr.models.yourtts import YourTTS
from scr.models.xtts import XTTS


def run_yourtts(audio_file: str, text: str, language: str = "en"):
    """
    Ejecuta YourTTS con clonación de voz

    Args:
        audio_file: Ruta al archivo de audio para clonación de voz
        text: Texto a sintetizar
        language: Código de idioma (en, es, fr, pt, etc.)
    """
    print("\n" + "="*60)
    print("EJECUTANDO YOURTTS")
    print("="*60)

    yourtts = YourTTS()

    output_dir = "outputs/yourtts"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "yourtts_output.wav")

    yourtts.list_languages()

    yourtts.synthesize(
        text=text,
        output_path=output_path,
        speaker_wav=audio_file,
        language=language
    )

    print(f"\n✓ Proceso completado. Audio guardado en: {output_path}")


def run_xtts(audio_file: str, text: str, language: str = "en"):
    """
    Ejecuta XTTS v2 con clonación de voz

    Args:
        audio_file: Ruta al archivo de audio para clonación de voz
        text: Texto a sintetizar
        language: Código de idioma (en, es, fr, de, it, pt, etc.)
    """
    print("\n" + "="*60)
    print("EJECUTANDO XTTS V2")
    print("="*60)

    xtts = XTTS()

    output_dir = "outputs/xtts"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "xtts_output.wav")

    xtts.list_languages()

    xtts.synthesize(
        text=text,
        output_path=output_path,
        speaker_wav=audio_file,
        language=language
    )

    print(f"\n✓ Proceso completado. Audio guardado en: {output_path}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Clonación de voz usando YourTTS y XTTS v2"
    )

    parser.add_argument(
        "--model",
        required=True,
        choices=["yourtts", "xtts"],
        help="Modelo TTS a utilizar (yourtts o xtts)"
    )

    parser.add_argument(
        "--audio",
        type=str,
        required=True,
        help="Ruta al archivo de audio para clonación de voz"
    )

    parser.add_argument(
        "--text",
        type=str,
        default="Hi, this is captain Santiago speaking, we will be landing soon",
        help="Texto a sintetizar"
    )

    parser.add_argument(
        "--language",
        type=str,
        default="en",
        help="Código de idioma (en, es, fr, de, it, pt, etc.)"
    )

    args = parser.parse_args()

    if args.model == "yourtts":
        run_yourtts(
            audio_file=args.audio,
            text=args.text,
            language=args.language
        )
    elif args.model == "xtts":
        run_xtts(
            audio_file=args.audio,
            text=args.text,
            language=args.language
        )
