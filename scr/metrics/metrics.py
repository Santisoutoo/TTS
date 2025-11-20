# -*- coding: utf-8 -*-
"""
Módulo de métricas para evaluar la calidad de síntesis de voz (TTS)
Implementa métricas objetivas para medir la similitud entre audio original y sintético
"""

import numpy as np
from pathlib import Path
from typing import Dict, Union
import warnings
from resemblyzer import VoiceEncoder, preprocess_wav
from scipy.spatial.distance import cosine
import json


warnings.filterwarnings('ignore')


class TTSMetrics:
    """
    Clase para calcular métricas de evaluación de sistemas TTS
    """

    def __init__(self, sr: int = 16000):
        self.sr = sr
        self.encoder = None  # Se cargará bajo demanda

    def _get_encoder(self) -> VoiceEncoder:
        if self.encoder is None:
            print("Cargando VoiceEncoder de Resemblyzer...")
            self.encoder = VoiceEncoder()
        return self.encoder

    def speaker_similarity(
        self,
        original_path: Union[str, Path],
        synthetic_path: Union[str, Path]
        ) -> float:
        encoder = self._get_encoder()

        original_wav = preprocess_wav(original_path)
        synthetic_wav = preprocess_wav(synthetic_path)

        original_embed = encoder.embed_utterance(original_wav)
        synthetic_embed = encoder.embed_utterance(synthetic_wav)

        similarity = 1 - cosine(original_embed, synthetic_embed)

        return float(similarity)

    def comprehensive_evaluation(self,
                                original_path: Union[str, Path],
                                synthetic_path: Union[str, Path],
                                verbose: bool = True) -> Dict:
        """
        Realiza evaluación de speaker similarity

        Args:
            original_path: Ruta al audio original (referencia)
            synthetic_path: Ruta al audio sintético
            verbose: Si True, imprime progreso

        Returns:
            Diccionario con las métricas calculadas
        """
        results = {
            'original_audio': str(original_path),
            'synthetic_audio': str(synthetic_path)
        }

        if verbose:
            print("\n" + "="*60)
            print("EVALUACIÓN DE SPEAKER SIMILARITY")
            print("="*60)
            print(f"Audio original: {original_path}")
            print(f"Audio sintético: {synthetic_path}\n")

        # Speaker Similarity
        if verbose:
            print("Calculando Speaker Similarity (Resemblyzer)...")
        try:
            similarity = self.speaker_similarity(original_path, synthetic_path)
            results['speaker_similarity'] = similarity
            if verbose:
                print(f"   Speaker Similarity: {similarity:.4f}")
        except Exception as e:
            if verbose:
                print(f"   Error en Speaker Similarity: {e}")
            results['speaker_similarity'] = None

        if verbose:
            print("\n" + "="*60)
            print("RESUMEN")
            print("="*60)
            if results.get('speaker_similarity'):
                print(f"Speaker Similarity: {results['speaker_similarity']:.4f} (objetivo: >0.8)")
            print("="*60 + "\n")

        return results

    def save_results(self, results: Dict, output_path: Union[str, Path]):
        """
        Guarda resultados en formato JSON

        Args:
            results: Diccionario con resultados
            output_path: Ruta de salida
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"Resultados guardados en: {output_path}")


def main():
    """
    Función principal para uso standalone
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Evalúa la calidad de audio TTS usando múltiples métricas"
    )
    parser.add_argument(
        "--original",
        required=True,
        help="Ruta al audio original (referencia)"
    )
    parser.add_argument(
        "--synthetic",
        required=True,
        help="Ruta al audio sintético"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Ruta para guardar resultados JSON (opcional)"
    )
    parser.add_argument(
        "--sr",
        type=int,
        default=16000,
        help="Sample rate para procesamiento (default: 16000)"
    )

    args = parser.parse_args()

    # Crear evaluador
    evaluator = TTSMetrics(sr=args.sr)

    # Evaluar
    results = evaluator.comprehensive_evaluation(
        original_path=args.original,
        synthetic_path=args.synthetic,
        verbose=True
    )

    # Guardar resultados si se especifica
    if args.output:
        evaluator.save_results(results, args.output)

    return results


if __name__ == "__main__":
    main()
