"""
Script para evaluar y comparar modelos TTS usando múltiples métricas
Uso:
    python evaluate_models.py --reference data/reference.wav --models outputs/xtts outputs/yourtts
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict
import pandas as pd
from scr.metrics import TTSMetrics


def evaluate_model_output(metrics_evaluator: TTSMetrics,
                          reference_path: Path,
                          synthetic_path: Path,
                          model_name: str,
                          verbose: bool = True) -> Dict:
    """
    Evalúa un audio sintético generado por un modelo TTS

    Args:
        metrics_evaluator: Instancia de TTSMetrics
        reference_path: Ruta al audio de referencia
        synthetic_path: Ruta al audio sintético
        model_name: Nombre del modelo
        verbose: Si True, imprime resultados

    Returns:
        Diccionario con todas las métricas
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"EVALUANDO: {model_name}")
        print(f"{'='*70}")

    results = metrics_evaluator.comprehensive_evaluation(
        original_path=reference_path,
        synthetic_path=synthetic_path,
        verbose=verbose
    )

    results['model_name'] = model_name

    return results


def compare_models(reference_path: Path,
                   model_outputs: Dict[str, Path],
                   output_dir: Path = None,
                   verbose: bool = True) -> pd.DataFrame:
    """
    Compara múltiples modelos TTS

    Args:
        reference_path: Ruta al audio de referencia
        model_outputs: Diccionario {nombre_modelo: ruta_audio_sintetico}
        output_dir: Directorio donde guardar resultados
        verbose: Si True, imprime progreso

    Returns:
        DataFrame con comparación de métricas
    """
    evaluator = TTSMetrics(sr=16000)
    all_results = []

    for model_name, synthetic_path in model_outputs.items():
        if not Path(synthetic_path).exists():
            print(f"⚠️  Audio no encontrado: {synthetic_path}")
            continue

        results = evaluate_model_output(
            evaluator,
            reference_path,
            synthetic_path,
            model_name,
            verbose=verbose
        )
        all_results.append(results)

        # Guardar resultados individuales
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{model_name}_metrics.json"
            evaluator.save_results(results, output_file)

    # Crear DataFrame comparativo
    comparison_data = []
    for result in all_results:
        comparison_data.append({
            'Model': result.get('model_name', 'Unknown'),
            'Speaker Similarity': result.get('speaker_similarity'),
            'MCD (dB)': result.get('mcd'),
            'Spectral Convergence': result.get('spectral_convergence'),
            'SNR (dB)': result.get('snr'),
            'Mel Correlation': result.get('mel_correlation'),
            'Mel MSE': result.get('mel_mse'),
            'Duration Ratio': result.get('duration_ratio'),
            'Pitch Difference (Hz)': result.get('pitch_difference')
        })

    df = pd.DataFrame(comparison_data)

    # Guardar comparación
    if output_dir:
        comparison_file = output_dir / "comparison.csv"
        df.to_csv(comparison_file, index=False)
        print(f"\n✓ Comparación guardada en: {comparison_file}")

        # Guardar comparación JSON completa
        json_file = output_dir / "comparison_full.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"✓ Resultados completos guardados en: {json_file}")

    return df


def print_comparison_table(df: pd.DataFrame):
    """
    Imprime tabla comparativa formateada

    Args:
        df: DataFrame con resultados de comparación
    """
    print("\n" + "="*70)
    print("TABLA COMPARATIVA DE MODELOS")
    print("="*70)
    print("\nMétricas principales (valores ideales entre paréntesis):\n")

    # Formatear tabla
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.float_format', '{:.4f}'.format)

    print(df.to_string(index=False))

    print("\n" + "-"*70)
    print("Interpretación:")
    print("  • Speaker Similarity: >0.80 excelente, >0.70 bueno")
    print("  • MCD: <6.0 excelente, <8.0 bueno")
    print("  • Mel Correlation: >0.90 excelente, >0.85 bueno")
    print("  • SNR: >20 dB excelente, >15 dB bueno")
    print("  • Duration Ratio: ~1.0 ideal")
    print("="*70 + "\n")

    # Determinar mejor modelo por métrica
    print("MEJORES MODELOS POR MÉTRICA:")
    print("-"*70)

    metrics_to_compare = {
        'Speaker Similarity': ('max', 'Mayor es mejor'),
        'MCD (dB)': ('min', 'Menor es mejor'),
        'Mel Correlation': ('max', 'Mayor es mejor'),
        'SNR (dB)': ('max', 'Mayor es mejor')
    }

    for metric, (comparison, description) in metrics_to_compare.items():
        if metric in df.columns:
            valid_data = df[df[metric].notna()]
            if len(valid_data) > 0:
                if comparison == 'max':
                    best_idx = valid_data[metric].idxmax()
                    best_value = valid_data.loc[best_idx, metric]
                else:
                    best_idx = valid_data[metric].idxmin()
                    best_value = valid_data.loc[best_idx, metric]

                best_model = valid_data.loc[best_idx, 'Model']
                print(f"  {metric:25s}: {best_model:15s} ({best_value:.4f}) - {description}")

    print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Evalúa y compara modelos TTS usando métricas objetivas"
    )

    parser.add_argument(
        "--reference",
        type=str,
        required=True,
        help="Ruta al audio de referencia original"
    )

    parser.add_argument(
        "--models",
        type=str,
        nargs='+',
        help="Lista de rutas a audios sintéticos o directorios de modelos (ej: outputs/xtts outputs/yourtts)"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs/comparisons",
        help="Directorio donde guardar resultados (default: outputs/comparisons)"
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Modo silencioso (no imprime detalles durante evaluación)"
    )

    args = parser.parse_args()

    reference_path = Path(args.reference)
    if not reference_path.exists():
        print(f"❌ Error: Audio de referencia no encontrado: {reference_path}")
        return

    # Procesar rutas de modelos
    model_outputs = {}

    if args.models:
        for model_path in args.models:
            path = Path(model_path)

            # Si es un directorio, buscar archivos .wav
            if path.is_dir():
                wav_files = list(path.glob("*.wav"))
                if wav_files:
                    model_name = path.name
                    # Usar el primer archivo wav encontrado
                    model_outputs[model_name] = wav_files[0]
            # Si es un archivo, usarlo directamente
            elif path.is_file() and path.suffix == '.wav':
                model_name = path.stem
                model_outputs[model_name] = path
    else:
        # Si no se especifican modelos, buscar en directorios predeterminados
        default_dirs = ['outputs/xtts', 'outputs/yourtts']
        for dir_name in default_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists() and dir_path.is_dir():
                wav_files = list(dir_path.glob("*.wav"))
                if wav_files:
                    model_name = dir_path.name
                    model_outputs[model_name] = wav_files[0]

    if not model_outputs:
        print("❌ Error: No se encontraron audios sintéticos para evaluar")
        print("\nUso:")
        print("  python evaluate_models.py --reference data/ref.wav --models outputs/xtts outputs/yourtts")
        return

    print(f"\n🎯 Evaluando {len(model_outputs)} modelo(s) contra referencia: {reference_path}")
    print(f"📊 Modelos a evaluar: {', '.join(model_outputs.keys())}\n")

    # Comparar modelos
    df = compare_models(
        reference_path=reference_path,
        model_outputs=model_outputs,
        output_dir=Path(args.output_dir),
        verbose=not args.quiet
    )

    # Imprimir tabla comparativa
    print_comparison_table(df)


if __name__ == "__main__":
    main()
