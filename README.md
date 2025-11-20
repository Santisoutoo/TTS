# Zero-Shot Voice Cloning con TTS

## Descripción del Proyecto

Este proyecto implementa y compara diferentes modelos de Text-to-Speech (TTS) para realizar **zero-shot voice cloning**, una técnica que permite imitar la voz de una persona a partir de tan solo unos segundos de audio, sin necesidad de realizar costosos entrenamientos o fine-tuning del modelo.

A partir de un breve ejemplo de audio original, los modelos generan una voz sintética capaz de aproximarse a las características de la voz original diciendo palabras completamente diferentes.

## Modelos Implementados

Este proyecto incluye dos modelos de la biblioteca Coqui TTS:

1. **XTTS v2** (`tts_models/multilingual/multi-dataset/xtts_v2`)
   - Arquitectura Transformer multilingüe
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



## Guía de Uso

### 1. Generar Audio Sintético

Los modelos se ejecutan usando los comandos make definidos en el Makefile. Esto simplifica la ejecución y maneja automáticamente la configuración de Docker.

#### Construir la imagen Docker

Antes de ejecutar los modelos por primera vez:

```bash
make build
```

#### Ejecutar XTTS v2

```bash
make run-xtts
```

Este comando ejecuta XTTS v2 con los parámetros por defecto definidos en el Makefile.

#### Ejecutar YourTTS

```bash
make run-yourtts
```

#### Ejecutar ambos modelos

Para ejecutar ambos modelos secuencialmente:

```bash
make run-all
```

#### Personalizar parámetros

Para cambiar el audio de referencia, texto o idioma, modifica las variables en el Makefile:

```makefile
AUDIO_REF := inputs/tu_audio.wav
TEXT := "Tu texto aquí"
LANGUAGE := es
```


#### Salida

Los audios generados se guardarán en:
- `outputs/xtts/xtts_output.wav` para XTTS v2
- `outputs/yourtts/yourtts_output.wav` para YourTTS

### 2. Evaluar y Comparar Modelos (Métricas)

Una vez generados los audios sintéticos, usa el script `evaluate_models.py` para calcular métricas de similitud y comparar el desempeño de los modelos.

#### Comparar XTTS v2 y YourTTS

```bash
python evaluate_models.py \
  --reference inputs/inference_voice_plane_announcement.wav \
  --models outputs/xtts outputs/yourtts
```

Este comando:
1. Calcula la métrica **Speaker Similarity** para cada modelo
2. Genera una tabla comparativa
3. Guarda los resultados en archivos JSON y CSV

#### Parámetros

- `--reference`: Audio de referencia original - **Requerido**
- `--models`: Lista de rutas a directorios con audios sintéticos o archivos .wav específicos - **Requerido**
- `--output-dir`: Directorio donde guardar resultados (default: `outputs/comparisons`)
- `--quiet`: Modo silencioso (no imprime detalles durante evaluación)

#### Ejemplos adicionales

**Comparar archivos específicos:**

```bash
python evaluate_models.py \
  --reference inputs/reference.wav \
  --models outputs/xtts/xtts_output.wav outputs/yourtts/yourtts_output.wav
```

**Cambiar directorio de salida:**

```bash
python evaluate_models.py \
  --reference inputs/reference.wav \
  --models outputs/xtts outputs/yourtts \
  --output-dir results/experiment_1
```

#### Salida del script

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

- ✅ Grabación de estudio o en ambiente silencioso
- ✅ Voz clara y bien articulada
- ✅ Sin música de fondo
- ✅ Sin reverberación excesiva

### Ejemplos de audios problemáticos

- ❌ Audio con mucho ruido de fondo
- ❌ Múltiples personas hablando
- ❌ Audio muy corto (< 2 segundos)
- ❌ Audio muy distorsionado o comprimido

## Workflow Completo de Ejemplo

### Ejemplo 1: Comparar dos modelos con el mismo audio

```bash
# Paso 1: Construir la imagen Docker (solo la primera vez)
make build

# Paso 2: Configurar parámetros en el Makefile (opcional)
# Edita las variables AUDIO_REF, TEXT, y LANGUAGE en el Makefile

# Paso 3: Generar audios con ambos modelos
make run-all

# Paso 4: Evaluar y comparar resultados
python evaluate_models.py \
  --reference inputs/inference_voice_plane_announcement.wav \
  --models outputs/xtts outputs/yourtts
```

### Ejemplo 2: Generar y evaluar con audio personalizado

```bash
# Paso 1: Ejecutar con parámetros personalizados
make run-xtts AUDIO_REF=inputs/mi_voz.wav TEXT="Hola mundo" LANGUAGE=es
make run-yourtts AUDIO_REF=inputs/mi_voz.wav TEXT="Hola mundo" LANGUAGE=es

# Paso 2: Evaluar resultados
python evaluate_models.py \
  --reference inputs/mi_voz.wav \
  --models outputs/xtts outputs/yourtts
```

### Ejemplo 3: Probar solo un modelo y ver métricas

```bash
# Generar con XTTS v2
make run-xtts

# Evaluar solo este modelo
python evaluate_models.py \
  --reference inputs/inference_voice_plane_announcement.wav \
  --models outputs/xtts/xtts_output.wav
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

- **[docs/informe.pdf](docs/informe.pdf)**: Informe técnico completo con detalles de implementación, metodología y explicación de las métricas
- **[docs/metricas_guia.md](docs/metricas_guia.md)**: Guía rápida de interpretación de métricas
- **[docs/resultados.md](docs/resultados.md.md)**: Resultados similitud
## Contribuciones y Atribuciones

### Audios de Referencia

- Audio: [Plane Flight Safety Announcement (part 1).wav](https://freesound.org/s/497189/) por ajwphotographic, usado bajo [Licencia Creative Commons Attribution 3.0](https://creativecommons.org/licenses/by/3.0/)

## Licencia

Este proyecto es con fines académicos exclusivamente.