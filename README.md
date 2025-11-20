# Zero-Shot Voice Cloning con TTS

## Descripción del Proyecto

Este proyecto implementa y compara diferentes modelos de Text-to-Speech (TTS) para realizar **zero-shot voice cloning**, una técnica que permite imitar la voz de una persona a partir de tan solo unos segundos de audio, sin necesidad de realizar costosos entrenamientos o fine-tuning del modelo.

A partir de un breve ejemplo de audio original, los modelos generan una voz sintética capaz de aproximarse a las características de la voz original diciendo palabras completamente diferentes.

## Modelos Implementados

Este proyecto incluye dos modelos de la biblioteca Coqui TTS:

1. **XTTS v2** (`tts_models/multilingual/multi-dataset/xtts_v2`)
   - Arquitectura Transformer multilingüe
   - Soporte para 16 idiomas
   - Zero-shot voice cloning de alta calidad

2. **YourTTS** (`tts_models/multilingual/multi-dataset/your_tts`)
   - Arquitectura VITS (Variational Inference TTS)
   - Síntesis end-to-end en un solo paso
   - Generación rápida y eficiente

## Estructura del Proyecto

```
TTS/
├── main.py                      # Script principal para generar audio sintético
├── evaluate_models.py           # Script para evaluar y comparar modelos
├── requirements.txt             # Dependencias Python
├── dockerfile                   # Configuración Docker
├── pyproject.toml              # Configuración del proyecto
├── README.md                   # Este archivo
│
├── scr/                        # Código fuente
│   ├── __init__.py
│   ├── models/                 # Implementaciones de modelos TTS
│   │   ├── __init__.py
│   │   ├── xtts.py            # Implementación de XTTS v2
│   │   └── yourtts.py         # Implementación de YourTTS
│   └── metrics/               # Sistema de métricas
│       ├── __init__.py
│       └── metrics.py         # Cálculo de Speaker Similarity
│
├── inputs/                     # Audios de referencia para clonación
│   └── inference_voice_plane_announcement.wav
│
├── outputs/                    # Audios generados por los modelos
│   ├── xtts/                  # Salidas de XTTS v2
│   └── yourtts/               # Salidas de YourTTS
│
└── docs/                       # Documentación del proyecto
    ├── memoria.md             # Informe técnico completo
    └── metricas_guia.md       # Guía de interpretación de métricas
```

## Requisitos del Sistema

### Software necesario

- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Docker 20.10+ (opcional, para entorno containerizado)
- 8GB RAM mínimo (16GB recomendado)

### Espacio en disco

- Al menos 10GB de espacio libre
- Los modelos pre-entrenados ocupan ~2.5GB
- Las dependencias ocupan ~3GB

## Instalación

### Opción 1: Instalación Local (Recomendada para desarrollo)

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repo>
   cd TTS
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # o en Windows:
   # .venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Verificar instalación**
   ```bash
   python -c "from TTS.api import TTS; print('TTS instalado correctamente')"
   ```

### Opción 2: Usando Docker

1. **Construir la imagen Docker**
   ```bash
   docker build -t tts-project .
   ```

   **Nota:** La imagen es pesada (~7-8GB). Asegúrate de tener suficiente espacio en disco.

2. **Ejecutar contenedor interactivo**
   ```bash
   docker run -it --rm \
     -v $(pwd):/workspace \
     tts-project bash
   ```

## Guía de Uso

### 1. Generar Audio Sintético

El script `main.py` permite generar audio sintético usando cualquiera de los dos modelos:

#### Uso básico con XTTS v2

```bash
python main.py \
  --model xtts \
  --audio inputs/inference_voice_plane_announcement.wav \
  --text "Hi, this is captain Santiago speaking, we will be landing soon" \
  --language en
```

#### Uso básico con YourTTS

```bash
python main.py \
  --model yourtts \
  --audio inputs/inference_voice_plane_announcement.wav \
  --text "Hi, this is captain Santiago speaking, we will be landing soon" \
  --language en
```

#### Parámetros disponibles

- `--model`: Modelo a utilizar (`xtts` o `yourtts`) - **Requerido**
- `--audio`: Ruta al archivo de audio de referencia para clonación - **Requerido**
- `--text`: Texto a sintetizar (opcional, usa texto por defecto si no se especifica)
- `--language`: Código de idioma (default: `en`)
  - Idiomas soportados: `en`, `es`, `fr`, `de`, `it`, `pt`, `pl`, `tr`, `ru`, `nl`, `cs`, `ar`, `zh-cn`, `ja`, `ko`, `hu`

#### Ejemplo en español

```bash
python main.py \
  --model xtts \
  --audio inputs/mi_voz.wav \
  --text "Hola, este es un ejemplo de clonación de voz en español" \
  --language es
```

#### Salida

Los audios generados se guardarán en:
- `outputs/xtts/xtts_output.wav` para XTTS v2
- `outputs/yourtts/yourtts_output.wav` para YourTTS

### 2. Evaluar Similitud de Voz (Speaker Similarity)

#### Evaluar un solo audio

Para evaluar la similitud entre un audio de referencia y un audio sintético:

```bash
python -m scr.metrics.metrics \
  --original inputs/inference_voice_plane_announcement.wav \
  --synthetic outputs/xtts/xtts_output.wav
```

**Salida esperada:**
```
============================================================
EVALUACIÓN DE SPEAKER SIMILARITY
============================================================
Audio original: inputs/inference_voice_plane_announcement.wav
Audio sintético: outputs/xtts/xtts_output.wav

Cargando VoiceEncoder de Resemblyzer...
Calculando Speaker Similarity (Resemblyzer)...
   Speaker Similarity: 0.8234

============================================================
RESUMEN
============================================================
Speaker Similarity: 0.8234 (objetivo: >0.8)
============================================================
```

#### Comparar múltiples modelos

Para comparar XTTS v2 y YourTTS automáticamente:

```bash
python evaluate_models.py \
  --reference inputs/inference_voice_plane_announcement.wav \
  --models outputs/xtts outputs/yourtts
```

**Parámetros:**
- `--reference`: Audio de referencia original - **Requerido**
- `--models`: Lista de rutas a directorios con audios sintéticos o archivos .wav específicos
- `--output-dir`: Directorio donde guardar resultados (default: `outputs/comparisons`)
- `--quiet`: Modo silencioso (no imprime detalles durante evaluación)

**Ejemplo especificando archivos específicos:**

```bash
python evaluate_models.py \
  --reference inputs/reference.wav \
  --models outputs/xtts/xtts_output.wav outputs/yourtts/yourtts_output.wav
```

#### Salida del script de comparación

El script genera:

1. **Tabla comparativa en consola:**
   ```
   ======================================================================
   TABLA COMPARATIVA DE MODELOS
   ======================================================================

   Speaker Similarity:

   Model     Speaker Similarity
   xtts                  0.8234
   yourtts               0.7891

   ----------------------------------------------------------------------
   Interpretación:
     • Speaker Similarity: >0.80 excelente, >0.70 bueno
   ======================================================================

   MEJORES MODELOS POR MÉTRICA:
   ----------------------------------------------------------------------
     Speaker Similarity      : xtts            (0.8234) - Mayor es mejor
   ======================================================================
   ```

2. **Archivos JSON con métricas individuales:**
   - `outputs/comparisons/xtts_metrics.json`
   - `outputs/comparisons/yourtts_metrics.json`

3. **Archivo CSV comparativo:**
   - `outputs/comparisons/comparison.csv`

4. **JSON con resultados completos:**
   - `outputs/comparisons/comparison_full.json`

### 3. Interpretación de Resultados

#### Speaker Similarity

La métrica **Speaker Similarity** mide qué tan parecida es la voz sintética a la voz original. Es un valor entre 0 y 1:

| Rango | Interpretación | Significado |
|-------|----------------|-------------|
| **> 0.80** | Excelente | La voz sintética es casi indistinguible de la original |
| **0.70 - 0.80** | Buena | La voz se parece claramente, con diferencias leves |
| **0.60 - 0.70** | Regular | Se reconocen características, pero hay diferencias notables |
| **< 0.60** | Baja | La voz no captura bien las características del hablante |

Para más detalles sobre cómo se calcula esta métrica, consulta [docs/memoria.md](docs/memoria.md).

## Requisitos de Audio de Referencia

Para obtener los mejores resultados en la clonación de voz:

### Características ideales

- **Duración:** Entre 3 y 10 segundos
- **Calidad:** Audio limpio sin ruido de fondo
- **Contenido:** Una sola persona hablando
- **Formato:** WAV, MP3, o FLAC
- **Sample rate:** 16kHz o superior (se re-muestrea automáticamente)

### Ejemplos de buenos audios de referencia

✅ Grabación de estudio o en ambiente silencioso
✅ Voz clara y bien articulada
✅ Sin música de fondo
✅ Sin reverberación excesiva

### Ejemplos de audios problemáticos

❌ Audio con mucho ruido de fondo
❌ Múltiples personas hablando
❌ Audio muy corto (< 2 segundos)
❌ Audio muy distorsionado o comprimido

## Workflow Completo de Ejemplo

### Ejemplo 1: Comparar dos modelos con el mismo audio

```bash
# Paso 1: Generar audio con XTTS v2
python main.py \
  --model xtts \
  --audio inputs/mi_voz.wav \
  --text "Hello, this is a test of voice cloning" \
  --language en

# Paso 2: Generar audio con YourTTS
python main.py \
  --model yourtts \
  --audio inputs/mi_voz.wav \
  --text "Hello, this is a test of voice cloning" \
  --language en

# Paso 3: Comparar ambos modelos
python evaluate_models.py \
  --reference inputs/mi_voz.wav \
  --models outputs/xtts outputs/yourtts
```

### Ejemplo 2: Probar diferentes textos con el mismo modelo

```bash
# Texto 1
python main.py --model xtts --audio inputs/ref.wav \
  --text "The quick brown fox jumps over the lazy dog" --language en

# Renombrar salida
mv outputs/xtts/xtts_output.wav outputs/xtts/xtts_output_1.wav

# Texto 2
python main.py --model xtts --audio inputs/ref.wav \
  --text "To be or not to be, that is the question" --language en

# Renombrar salida
mv outputs/xtts/xtts_output.wav outputs/xtts/xtts_output_2.wav

# Evaluar ambos
python -m scr.metrics.metrics --original inputs/ref.wav --synthetic outputs/xtts/xtts_output_1.wav
python -m scr.metrics.metrics --original inputs/ref.wav --synthetic outputs/xtts/xtts_output_2.wav
```

## Solución de Problemas

### Error: "CUDA not available"

Este mensaje es normal si no tienes una GPU NVIDIA. Los modelos funcionarán en CPU, aunque más lento. No es un error crítico.

### Error: "Out of memory"

Si te quedas sin memoria RAM:
- Cierra otras aplicaciones
- Reduce el tamaño del audio de referencia
- Usa textos más cortos

### Los modelos se descargan muy lento

La primera vez que ejecutas cada modelo, se descargan automáticamente (total ~2.5GB). Esto puede tardar según tu conexión. Los modelos se cachean localmente para usos futuros.

### Audio de salida de mala calidad

Posibles causas:
- Audio de referencia con mucho ruido → Usa un audio más limpio
- Audio de referencia muy corto → Usa al menos 3-5 segundos
- Idioma no soportado bien → Prueba con inglés que tiene mejor soporte

### Docker: Error de espacio en disco

Las imágenes Docker para este proyecto son grandes (~7-8GB). Si te quedas sin espacio:

```bash
# Limpiar Docker completamente
docker system prune -a --volumes

# Reconstruir la imagen
docker build -t tts-project .
```

### Problemas de dependencias

Si encuentras errores al instalar:

```bash
# Actualizar pip
pip install --upgrade pip

# Reinstalar desde cero
pip uninstall -y TTS
pip install --no-cache-dir -r requirements.txt
```

## Documentación Adicional

- **[docs/memoria.md](docs/memoria.md)**: Informe técnico completo con detalles de implementación, metodología y explicación profunda de las métricas
- **[docs/metricas_guia.md](docs/metricas_guia.md)**: Guía rápida de interpretación de métricas

## Contribuciones y Atribuciones

### Audios de Referencia

- Audio: [Plane Flight Safety Announcement (part 1).wav](https://freesound.org/s/497189/) por ajwphotographic, usado bajo [Licencia Creative Commons Attribution 3.0](https://creativecommons.org/licenses/by/3.0/)

### Bibliotecas Utilizadas

- [Coqui TTS](https://github.com/coqui-ai/TTS) - Framework de síntesis de voz
- [Resemblyzer](https://github.com/resemble-ai/Resemblyzer) - Embeddings de voz para verificación de hablante
- [PyTorch](https://pytorch.org/) - Framework de deep learning

## Licencia

Este proyecto es con fines académicos exclusivamente.

---

**Fecha de última actualización:** Noviembre 2025
