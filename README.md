# Zero-Shot Voice Cloning con TTS

## Descripción del Proyecto

Este proyecto implementa y compara diferentes modelos de Text-to-Speech (TTS) para realizar **zero-shot voice cloning**, una técnica que permite imitar la voz de una persona a partir de tan solo unos segundos de audio, sin necesidad de realizar costosos entrenamientos o fine-tuning del modelo.

A partir de un breve ejemplo de audio original, los modelos generan una voz sintética capaz de aproximarse a las características de la voz original diciendo palabras completamente diferentes.

## Objetivos Académicos

- Implementar y comparar múltiples modelos de TTS para zero-shot voice cloning
- Evaluar la calidad de la síntesis de voz mediante métricas objetivas
- Realizar un análisis comparativo tanto cualitativo (subjetivo) como cuantitativo
- Documentar decisiones de implementación y resultados obtenidos
- Entregar un proyecto containerizado con Docker para reproducibilidad

## Modelos Implementados

### 1. Coqui TTS - Modelo 1: XTTS v2
- **Nombre:** `tts_models/multilingual/multi-dataset/xtts_v2`
- **Características:**
  - Modelo multilingüe
  - Soporte para español
  - Zero-shot voice cloning con audio de referencia
  - Basado en arquitectura Transformer

### 2. Coqui TTS - Modelo 2: YourTTS
- **Nombre:** `tts_models/multilingual/multi-dataset/your_tts`
- **Características:**
  - Arquitectura VITS (Variational Inference TTS)
  - Síntesis de alta calidad
  - Soporte multiidioma
  - Zero-shot speaker adaptation

### 3. GPT-SoVITS
- **Características:**
  - Modelo basado en GPT para síntesis de voz
  - Zero-shot voice cloning de alta calidad
  - Entrenamiento eficiente
  - Excelente naturalidad en el audio generado

## Métricas de Evaluación

Para la evaluación objetiva de los modelos se implementan las siguientes métricas:

1. **Similaridad de Embeddings de Voz (Speaker Similarity)**
   - Utilizando Resemblyzer para extraer embeddings
   - Medición de similitud coseno entre voz original y sintética
   - Rango: 0-1 (mayor es mejor)

2. **Métricas Adicionales:**
   - MOS (Mean Opinion Score) - evaluación subjetiva
   - Calidad de audio y naturalidad percibida
   - Comparación de espectrogramas

## Estructura del Proyecto

```
TTS/
├── dockerfile              # Configuración Docker
├── makefile               # Comandos automatizados
├── main.py                # Script principal
├── pyproject.toml         # Configuración del proyecto
├── requirements.txt       # Dependencias Python
├── README.md             # Este archivo
├── scr/
│   ├── coqui/
│   │   ├── __init__.py
│   │   └── coqui.py      # Implementación Coqui TTS
│   ├── sovits/
│   │   ├── __init__.py
│   │   └── sovits.py     # Implementación GPT-SoVITS
│   └── metrics/
│       ├── __init__.py
│       └── metrics.py    # Métricas de evaluación
├── inputs/               # Audio de referencia
├── outputs/              # Audio generado
│   ├── coqui/
│   ├── sovits/
│   └── comparisons/
└── docs/
    └── memoria.pdf       # Memoria técnica (entrega)
```

## Requisitos del Sistema

- Docker 20.10+
- Make (opcional, facilita comandos)
- 8GB RAM mínimo (recomendado 16GB)
- GPU con CUDA (opcional pero recomendado para mejor rendimiento)

## Instalación y Uso

### 1. Construir la imagen Docker

```bash
make build
```

O manualmente:
```bash
docker build -t tts-project .
```

### 2. Preparar audio de referencia

Coloca tu archivo de audio de referencia en la carpeta `inputs/`:

```bash
cp tu_audio.wav inputs/reference_voice.wav
```

**Requisitos del audio:**
- Formato: WAV, MP3, o FLAC
- Duración: 3-10 segundos recomendado
- Calidad: Buena claridad, sin ruido de fondo
- Contenido: Voz clara de una sola persona

### 3. Ejecutar modelos

#### Coqui TTS
```bash
make run-coqui
```

O manualmente:
```bash
docker run --shm-size=8g \
    -v $(pwd):/opt/project \
    -v $(pwd)/outputs:/opt/project/outputs \
    --rm tts-project \
    python /opt/project/main.py --model coqui --audio inputs/reference_voice.wav
```

#### GPT-SoVITS
```bash
make run-sovits
```

#### Modo interactivo (shell)
```bash
make shell
```

### 4. Evaluar con métricas

```bash
docker run --rm -v $(pwd):/opt/project tts-project \
    python -m scr.metrics.metrics \
    --original inputs/reference_voice.wav \
    --synthetic outputs/coqui/coqui_output.wav
```

## Hoja de Ruta

### Fase 1: Configuración Inicial ✓
- [x] Configurar entorno Docker
- [x] Instalar dependencias base
- [x] Estructura básica del proyecto
- [x] Configurar Makefile

### Fase 2: Implementación de Modelos
- [x] Implementar Coqui TTS - XTTS v2
- [ ] Implementar Coqui TTS - Modelo 2 (YourTTS)
- [ ] Implementar GPT-SoVITS
- [ ] Probar inferencia básica de cada modelo
- [ ] Ajustar parámetros de calidad

### Fase 3: Sistema de Métricas
- [ ] Implementar extracción de embeddings con Resemblyzer
- [ ] Calcular similaridad de speaker (cosine similarity)
- [ ] Implementar MOS subjetivo
- [ ] Crear script de evaluación comparativa automatizada
- [ ] Generar reportes de métricas

### Fase 4: Experimentación y Dataset
- [ ] Seleccionar/crear dataset de audios de referencia variados
- [ ] Definir conjunto de textos objetivo para síntesis
- [ ] Ejecutar experimentos sistemáticos con cada modelo
- [ ] Generar audios sintéticos para todas las combinaciones
- [ ] Recopilar métricas objetivas de todos los experimentos

### Fase 5: Análisis y Comparación
- [ ] Análisis cuantitativo (comparación de métricas)
- [ ] Análisis cualitativo (escucha subjetiva)
- [ ] Crear tablas comparativas de resultados
- [ ] Identificar fortalezas/debilidades de cada modelo
- [ ] Generar visualizaciones (gráficos, espectrogramas)
- [ ] Análisis estadístico de resultados

### Fase 6: Documentación y Entrega
- [ ] Escribir memoria técnica:
  - [ ] Introducción y contexto teórico
  - [ ] Descripción detallada de modelos utilizados
  - [ ] Decisiones de implementación justificadas
  - [ ] Metodología experimental
  - [ ] Resultados cuantitativos y cualitativos
  - [ ] Discusión y análisis crítico
  - [ ] Conclusiones y trabajos futuros
- [ ] Documentar código fuente
- [ ] Verificar reproducibilidad completa con Docker
- [ ] Organizar archivos de entrega
- [ ] Revisión final y preparar entrega

## Uso del Script Principal

El script [main.py](main.py) acepta los siguientes parámetros:

```bash
python main.py --model {coqui|sovits} --audio <ruta_audio> [opciones]
```

**Argumentos:**
- `--model`: Modelo a utilizar (coqui, sovits)
- `--audio`: Ruta al archivo de audio de referencia
- `--text`: Texto a sintetizar (opcional, usa texto por defecto)
- `--output`: Ruta de salida personalizada (opcional)

**Ejemplo:**
```bash
python main.py --model coqui \
    --audio inputs/reference.wav \
    --text "Hola, este es un ejemplo de clonación de voz en español"
```

## Resultados Esperados

Los audios generados se guardarán en:
- `outputs/coqui/` - Resultados de Coqui TTS (XTTS v2 y YourTTS)
- `outputs/sovits/` - Resultados de GPT-SoVITS
- `outputs/comparisons/` - Análisis comparativos y métricas

## Entrega del Proyecto

La entrega incluirá:

1. **Código fuente completo** (este repositorio)
2. **Imagen Docker** funcional y reproducible
3. **Dataset** de audios:
   - Audios de referencia originales
   - Audios sintéticos generados por cada modelo
4. **Memoria técnica** (PDF) que incluya:
   - Introducción al problema de voice cloning
   - Estado del arte y contexto teórico
   - Descripción de modelos y arquitecturas
   - Decisiones de implementación justificadas
   - Metodología experimental detallada
   - Resultados cuantitativos (métricas con tablas/gráficos)
   - Análisis cualitativo (evaluación subjetiva)
   - Comparación crítica entre modelos
   - Conclusiones y posibles mejoras futuras
   - Referencias bibliográficas

### Formato de Entrega

```
entrega_TTS/
├── codigo/                    # Código fuente
│   └── [contenido del repositorio]
├── docker/
│   ├── dockerfile
│   └── instrucciones_ejecucion.txt
├── dataset/
│   ├── referencias/           # Audios originales
│   └── generados/            # Audios sintéticos
│       ├── coqui_xtts/
│       ├── coqui_yourtts/
│       └── sovits/
├── resultados/
│   ├── metricas.csv          # Todas las métricas recopiladas
│   └── graficos/             # Visualizaciones
└── memoria.pdf               # Documento principal
```

## Troubleshooting

### Problemas comunes:

**Error de memoria:**
```bash
# Aumentar shared memory
docker run --shm-size=16g ...
```

**CUDA no disponible:**
- Los modelos funcionarán en CPU (más lento)
- Considera usar presets más rápidos
- Reduce el tamaño de batch si es aplicable

**Audio de baja calidad:**
- Verifica la calidad del audio de referencia
- Prueba con audios más largos (5-10 segundos)
- Elimina ruido de fondo del audio original
- Asegúrate de que el audio esté bien normalizado

**Modelo tarda mucho en cargar:**
- Es normal la primera vez (descarga modelos)
- Los modelos se cachean localmente
- Verifica espacio en disco suficiente

## Referencias

- [Coqui TTS Documentation](https://github.com/coqui-ai/TTS)
- [GPT-SoVITS Repository](https://github.com/RVC-Boss/GPT-SoVITS)
- [Resemblyzer](https://github.com/resemble-ai/Resemblyzer)
- [XTTS Paper](https://arxiv.org/abs/2306.07954)

## Licencia

Este proyecto es con fines académicos exclusivamente.

## Autor

Práctica de TTS y Zero-Shot Voice Cloning

---

**Fecha de última actualización:** Noviembre 2025


## Attributions


- Audio: [We Read And write.wav](https://freesound.org/s/497112/) por ajwphotographic, usado bajo [Licencia Creative Commons Attribution 3.0](https://creativecommons.org/licenses/by/3.0/).

- Audio: [Plane Flight Safety Announcement (part 1).wav](https://freesound.org/s/497189/) por ajwphotographic, usado bajo [Licencia Creative Commons Attribution 3.0](https://creativecommons.org/licenses/by/3.0/).