# Resultados de Evaluación - Speaker Similarity

## Audio con Ruido Ambiental: Anuncio de Avión

### YourTTS
```
============================================================
EVALUACIÓN DE SPEAKER SIMILARITY
============================================================
Audio original: data/inference_voice_plane_announcement.wav
Audio sintético: outputs/yourtts/yourtts_output_plane_announcement.wav

Calculando Speaker Similarity (Resemblyzer)...
Cargando VoiceEncoder de Resemblyzer...
Loaded the voice encoder model on cpu in 0.04 seconds.
   Speaker Similarity: 0.5765

============================================================
RESUMEN
============================================================
Speaker Similarity: 0.5765 (objetivo: >0.8)
============================================================
```

### XTTS v2
```
============================================================
EVALUACIÓN DE SPEAKER SIMILARITY
============================================================
Audio original: data/inference_voice_plane_announcement.wav
Audio sintético: outputs/xtts/xtts_output_plane_announcement.wav

Calculando Speaker Similarity (Resemblyzer)...
Cargando VoiceEncoder de Resemblyzer...
Loaded the voice encoder model on cpu in 0.05 seconds.
   Speaker Similarity: 0.8490

============================================================
RESUMEN
============================================================
Speaker Similarity: 0.8490 (objetivo: >0.8)
============================================================
```

## Audio Limpio: Cita del Poeta

### YourTTS
```
============================================================
EVALUACIÓN DE SPEAKER SIMILARITY
============================================================
Audio original: data/inference_voice_poeta.wav
Audio sintético: outputs/yourtts/yourtts_output_cita_Armstrong.wav

Calculando Speaker Similarity (Resemblyzer)...
Cargando VoiceEncoder de Resemblyzer...
Loaded the voice encoder model on cpu in 0.05 seconds.
   Speaker Similarity: 0.7920

============================================================
RESUMEN
============================================================
Speaker Similarity: 0.7920 (objetivo: >0.8)
============================================================
```

### XTTS v2
```
============================================================
EVALUACIÓN DE SPEAKER SIMILARITY
============================================================
Audio original: data/inference_voice_poeta.wav
Audio sintético: outputs/xtts/xtts_output_cita_Armstrong.wav

Calculando Speaker Similarity (Resemblyzer)...
Cargando VoiceEncoder de Resemblyzer...
Loaded the voice encoder model on cpu in 0.05 seconds.
   Speaker Similarity: 0.8460

============================================================
RESUMEN
============================================================
Speaker Similarity: 0.8460 (objetivo: >0.8)
============================================================
```

## Resumen Comparativo

| Audio | Modelo | Speaker Similarity | Cumple Objetivo (>0.8) |
|-------|--------|-------------------|------------------------|
| Anuncio de Avión (con ruido) | YourTTS | 0.5765 | ✗ No |
| Anuncio de Avión (con ruido) | XTTS v2 | 0.8490 | ✓ Sí |
| Cita del Poeta (limpio) | YourTTS | 0.7920 | ✗ No |
| Cita del Poeta (limpio) | XTTS v2 | 0.8460 | ✓ Sí |

## Conclusión

XTTS v2 supera consistentemente a YourTTS en ambas condiciones de audio, alcanzando valores superiores al objetivo de 0.8 en todos los casos. YourTTS muestra especial dificultad con audio ruidoso (0.5765) pero se acerca al objetivo en condiciones limpias (0.7920).