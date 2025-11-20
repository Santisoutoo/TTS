# -*- coding: utf-8 -*-
"""
Módulo de métricas para evaluar la calidad de síntesis de voz (TTS)
Implementa métricas objetivas para medir la similitud entre audio original y sintético
"""

import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Dict, Tuple, Optional, Union
import warnings
from resemblyzer import VoiceEncoder, preprocess_wav
from scipy.spatial.distance import cosine
from scipy.signal import get_window
from sklearn.metrics import mean_squared_error
import json


warnings.filterwarnings('ignore')


class TTSMetrics:
    """
    Clase para calcular métricas de evaluación de sistemas TTS
    """

    def __init__(self, sr: int = 16000):
        """
        Inicializa el evaluador de métricas

        Args:
            sr: Sample rate para procesamiento de audio
        """
        self.sr = sr
        self.encoder = None  # Se cargará bajo demanda

    def _load_audio(self, audio_path: Union[str, Path]) -> Tuple[np.ndarray, int]:
        """
        Carga un archivo de audio

        Args:
            audio_path: Ruta al archivo de audio

        Returns:
            Tupla (audio_data, sample_rate)
        """
        audio, sr = librosa.load(audio_path, sr=self.sr, mono=True)
        return audio, sr

    def _get_encoder(self) -> VoiceEncoder:
        """
        Obtiene el encoder de Resemblyzer (lazy loading)
        """
        if self.encoder is None:
            print("Cargando VoiceEncoder de Resemblyzer...")
            self.encoder = VoiceEncoder()
        return self.encoder

    def speaker_similarity(self,
                          original_path: Union[str, Path],
                          synthetic_path: Union[str, Path]) -> float:
        """
        Calcula la similaridad entre speakers usando embeddings de voz
        Utiliza Resemblyzer para extraer embeddings y calcula similitud coseno

        Args:
            original_path: Ruta al audio original (referencia)
            synthetic_path: Ruta al audio sintético

        Returns:
            Similaridad (0-1, mayor es mejor)
        """
        encoder = self._get_encoder()

        # Preprocesar audios según requerimientos de Resemblyzer
        original_wav = preprocess_wav(original_path)
        synthetic_wav = preprocess_wav(synthetic_path)

        # Extraer embeddings
        original_embed = encoder.embed_utterance(original_wav)
        synthetic_embed = encoder.embed_utterance(synthetic_wav)

        # Calcular similitud coseno (1 - distancia_coseno)
        similarity = 1 - cosine(original_embed, synthetic_embed)

        return float(similarity)

    def mel_cepstral_distortion(self,
                                original_path: Union[str, Path],
                                synthetic_path: Union[str, Path],
                                n_mfcc: int = 13) -> float:
        """
        Calcula Mel Cepstral Distortion (MCD)
        Métrica estándar en TTS para medir distorsión espectral

        Args:
            original_path: Ruta al audio original
            synthetic_path: Ruta al audio sintético
            n_mfcc: Número de coeficientes MFCC

        Returns:
            MCD en dB (menor es mejor)
        """
        # Cargar audios
        original, _ = self._load_audio(original_path)
        synthetic, _ = self._load_audio(synthetic_path)

        # Asegurar misma longitud
        min_len = min(len(original), len(synthetic))
        original = original[:min_len]
        synthetic = synthetic[:min_len]

        # Extraer MFCCs
        mfcc_orig = librosa.feature.mfcc(y=original, sr=self.sr, n_mfcc=n_mfcc)
        mfcc_synth = librosa.feature.mfcc(y=synthetic, sr=self.sr, n_mfcc=n_mfcc)

        # Asegurar mismas dimensiones
        min_frames = min(mfcc_orig.shape[1], mfcc_synth.shape[1])
        mfcc_orig = mfcc_orig[:, :min_frames]
        mfcc_synth = mfcc_synth[:, :min_frames]

        # Calcular MCD (excluyendo el primer coeficiente que es la energía)
        diff = mfcc_orig[1:, :] - mfcc_synth[1:, :]
        mcd = (10.0 / np.log(10.0)) * np.sqrt(2 * np.sum(diff ** 2, axis=0))

        return float(np.mean(mcd))

    def spectral_convergence(self,
                            original_path: Union[str, Path],
                            synthetic_path: Union[str, Path]) -> float:
        """
        Calcula Spectral Convergence - mide diferencia en espectrogramas

        Args:
            original_path: Ruta al audio original
            synthetic_path: Ruta al audio sintético

        Returns:
            Spectral Convergence (menor es mejor)
        """
        # Cargar audios
        original, _ = self._load_audio(original_path)
        synthetic, _ = self._load_audio(synthetic_path)

        # Asegurar misma longitud
        min_len = min(len(original), len(synthetic))
        original = original[:min_len]
        synthetic = synthetic[:min_len]

        # Calcular espectrogramas
        stft_orig = np.abs(librosa.stft(original))
        stft_synth = np.abs(librosa.stft(synthetic))

        # Calcular convergencia espectral
        numerator = np.linalg.norm(stft_orig - stft_synth, ord='fro')
        denominator = np.linalg.norm(stft_orig, ord='fro')

        return float(numerator / denominator)

    def pitch_metrics(self, audio_path: Union[str, Path]) -> Dict[str, float]:
        """
        Calcula métricas relacionadas con el pitch (F0)

        Args:
            audio_path: Ruta al archivo de audio

        Returns:
            Diccionario con estadísticas de pitch
        """
        audio, _ = self._load_audio(audio_path)

        # Extraer pitch con librosa
        f0 = librosa.yin(audio,
                        fmin=librosa.note_to_hz('C2'),
                        fmax=librosa.note_to_hz('C7'),
                        sr=self.sr)

        # Filtrar valores válidos (no NaN ni 0)
        valid_f0 = f0[(f0 > 0) & (~np.isnan(f0))]

        if len(valid_f0) == 0:
            return {
                'mean_pitch': 0.0,
                'std_pitch': 0.0,
                'min_pitch': 0.0,
                'max_pitch': 0.0,
                'pitch_range': 0.0
            }

        return {
            'mean_pitch': float(np.mean(valid_f0)),
            'std_pitch': float(np.std(valid_f0)),
            'min_pitch': float(np.min(valid_f0)),
            'max_pitch': float(np.max(valid_f0)),
            'pitch_range': float(np.max(valid_f0) - np.min(valid_f0))
        }

    def energy_metrics(self, audio_path: Union[str, Path]) -> Dict[str, float]:
        """
        Calcula métricas de energía del audio

        Args:
            audio_path: Ruta al archivo de audio

        Returns:
            Diccionario con estadísticas de energía
        """
        audio, _ = self._load_audio(audio_path)

        # Calcular RMS energy
        rms = librosa.feature.rms(y=audio)[0]

        # Calcular Zero Crossing Rate
        zcr = librosa.feature.zero_crossing_rate(audio)[0]

        return {
            'mean_energy': float(np.mean(rms)),
            'std_energy': float(np.std(rms)),
            'max_energy': float(np.max(rms)),
            'mean_zcr': float(np.mean(zcr)),
            'std_zcr': float(np.std(zcr))
        }

    def signal_to_noise_ratio(self,
                              original_path: Union[str, Path],
                              synthetic_path: Union[str, Path]) -> float:
        """
        Calcula Signal-to-Noise Ratio (SNR) aproximado
        Trata la diferencia como "ruido"

        Args:
            original_path: Ruta al audio original (señal)
            synthetic_path: Ruta al audio sintético

        Returns:
            SNR en dB (mayor es mejor)
        """
        # Cargar audios
        original, _ = self._load_audio(original_path)
        synthetic, _ = self._load_audio(synthetic_path)

        # Asegurar misma longitud
        min_len = min(len(original), len(synthetic))
        original = original[:min_len]
        synthetic = synthetic[:min_len]

        # Calcular potencia de señal y "ruido"
        signal_power = np.mean(synthetic ** 2)
        noise_power = np.mean((original - synthetic) ** 2)

        # Evitar división por cero
        if noise_power == 0:
            return float('inf')

        snr = 10 * np.log10(signal_power / noise_power)
        return float(snr)

    def spectral_similarity(self,
                           original_path: Union[str, Path],
                           synthetic_path: Union[str, Path]) -> Dict[str, float]:
        """
        Calcula métricas de similitud espectral

        Args:
            original_path: Ruta al audio original
            synthetic_path: Ruta al audio sintético

        Returns:
            Diccionario con métricas espectrales
        """
        # Cargar audios
        original, _ = self._load_audio(original_path)
        synthetic, _ = self._load_audio(synthetic_path)

        # Asegurar misma longitud
        min_len = min(len(original), len(synthetic))
        original = original[:min_len]
        synthetic = synthetic[:min_len]

        # Calcular espectrogramas mel
        mel_orig = librosa.feature.melspectrogram(y=original, sr=self.sr)
        mel_synth = librosa.feature.melspectrogram(y=synthetic, sr=self.sr)

        # Convertir a escala log
        log_mel_orig = librosa.power_to_db(mel_orig, ref=np.max)
        log_mel_synth = librosa.power_to_db(mel_synth, ref=np.max)

        # Asegurar mismas dimensiones
        min_frames = min(log_mel_orig.shape[1], log_mel_synth.shape[1])
        log_mel_orig = log_mel_orig[:, :min_frames]
        log_mel_synth = log_mel_synth[:, :min_frames]

        # Calcular MSE
        mse = mean_squared_error(log_mel_orig.flatten(), log_mel_synth.flatten())

        # Calcular correlación
        correlation = np.corrcoef(log_mel_orig.flatten(), log_mel_synth.flatten())[0, 1]

        return {
            'mel_mse': float(mse),
            'mel_correlation': float(correlation)
        }

    def duration_analysis(self,
                         original_path: Union[str, Path],
                         synthetic_path: Union[str, Path]) -> Dict[str, float]:
        """
        Analiza diferencias de duración entre audios

        Args:
            original_path: Ruta al audio original
            synthetic_path: Ruta al audio sintético

        Returns:
            Diccionario con análisis de duración
        """
        # Cargar audios
        original, sr_orig = self._load_audio(original_path)
        synthetic, sr_synth = self._load_audio(synthetic_path)

        # Calcular duraciones
        dur_orig = len(original) / sr_orig
        dur_synth = len(synthetic) / sr_synth

        # Calcular diferencia
        diff = abs(dur_orig - dur_synth)
        ratio = dur_synth / dur_orig if dur_orig > 0 else 0

        return {
            'original_duration': float(dur_orig),
            'synthetic_duration': float(dur_synth),
            'duration_difference': float(diff),
            'duration_ratio': float(ratio)
        }

    def comprehensive_evaluation(self,
                                original_path: Union[str, Path],
                                synthetic_path: Union[str, Path],
                                verbose: bool = True) -> Dict:
        """
        Realiza evaluación completa con todas las métricas

        Args:
            original_path: Ruta al audio original (referencia)
            synthetic_path: Ruta al audio sintético
            verbose: Si True, imprime progreso

        Returns:
            Diccionario con todas las métricas calculadas
        """
        results = {
            'original_audio': str(original_path),
            'synthetic_audio': str(synthetic_path)
        }

        if verbose:
            print("\n" + "="*60)
            print("EVALUACIÓN DE MÉTRICAS TTS")
            print("="*60)
            print(f"Audio original: {original_path}")
            print(f"Audio sintético: {synthetic_path}\n")

        # 1. Speaker Similarity (métrica más importante para voice cloning)
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

        # 2. Mel Cepstral Distortion
        if verbose:
            print("\nCalculando Mel Cepstral Distortion (MCD)...")
        try:
            mcd = self.mel_cepstral_distortion(original_path, synthetic_path)
            results['mcd'] = mcd
            if verbose:
                print(f"   MCD: {mcd:.4f} dB")
        except Exception as e:
            if verbose:
                print(f"   Error en MCD: {e}")
            results['mcd'] = None

        # 3. Spectral Convergence
        if verbose:
            print("\nCalculando Spectral Convergence...")
        try:
            spec_conv = self.spectral_convergence(original_path, synthetic_path)
            results['spectral_convergence'] = spec_conv
            if verbose:
                print(f"   Spectral Convergence: {spec_conv:.4f}")
        except Exception as e:
            if verbose:
                print(f"   Error en Spectral Convergence: {e}")
            results['spectral_convergence'] = None

        # 4. SNR
        if verbose:
            print("\nCalculando Signal-to-Noise Ratio...")
        try:
            snr = self.signal_to_noise_ratio(original_path, synthetic_path)
            results['snr'] = snr
            if verbose:
                print(f"   SNR: {snr:.4f} dB")
        except Exception as e:
            if verbose:
                print(f"   Error en SNR: {e}")
            results['snr'] = None

        # 5. Spectral Similarity
        if verbose:
            print("\nCalculando Spectral Similarity...")
        try:
            spec_sim = self.spectral_similarity(original_path, synthetic_path)
            results.update(spec_sim)
            if verbose:
                print(f"   Mel MSE: {spec_sim['mel_mse']:.4f}")
                print(f"   Mel Correlation: {spec_sim['mel_correlation']:.4f}")
        except Exception as e:
            if verbose:
                print(f"   Error en Spectral Similarity: {e}")
            results['mel_mse'] = None
            results['mel_correlation'] = None

        # 6. Duration Analysis
        if verbose:
            print("\nAnalizando duraciones...")
        try:
            duration = self.duration_analysis(original_path, synthetic_path)
            results.update(duration)
            if verbose:
                print(f"   Duración original: {duration['original_duration']:.2f}s")
                print(f"   Duración sintética: {duration['synthetic_duration']:.2f}s")
                print(f"   Diferencia: {duration['duration_difference']:.2f}s")
        except Exception as e:
            if verbose:
                print(f"   Error en Duration Analysis: {e}")

        # 7. Pitch Analysis (ambos audios)
        if verbose:
            print("\nAnalizando pitch...")
        try:
            pitch_orig = self.pitch_metrics(original_path)
            pitch_synth = self.pitch_metrics(synthetic_path)
            results['original_pitch'] = pitch_orig
            results['synthetic_pitch'] = pitch_synth

            # Calcular diferencia de pitch promedio
            pitch_diff = abs(pitch_orig['mean_pitch'] - pitch_synth['mean_pitch'])
            results['pitch_difference'] = pitch_diff

            if verbose:
                print(f"   Pitch medio original: {pitch_orig['mean_pitch']:.2f} Hz")
                print(f"   Pitch medio sintético: {pitch_synth['mean_pitch']:.2f} Hz")
                print(f"   Diferencia: {pitch_diff:.2f} Hz")
        except Exception as e:
            if verbose:
                print(f"   Error en Pitch Analysis: {e}")

        # 8. Energy Analysis
        if verbose:
            print("\nAnalizando energía...")
        try:
            energy_orig = self.energy_metrics(original_path)
            energy_synth = self.energy_metrics(synthetic_path)
            results['original_energy'] = energy_orig
            results['synthetic_energy'] = energy_synth

            if verbose:
                print(f"   Energía media original: {energy_orig['mean_energy']:.4f}")
                print(f"   Energía media sintética: {energy_synth['mean_energy']:.4f}")
        except Exception as e:
            if verbose:
                print(f"   Error en Energy Analysis: {e}")

        if verbose:
            print("\n" + "="*60)
            print("RESUMEN DE MÉTRICAS PRINCIPALES")
            print("="*60)
            if results.get('speaker_similarity'):
                print(f"Speaker Similarity:      {results['speaker_similarity']:.4f} (objetivo: >0.8)")
            if results.get('mcd'):
                print(f"MCD:                     {results['mcd']:.4f} dB (objetivo: <6.0)")
            if results.get('mel_correlation'):
                print(f"Mel Correlation:         {results['mel_correlation']:.4f} (objetivo: >0.9)")
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
