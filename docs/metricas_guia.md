# ¿Cómo interpretar métricas?

## ¿Qué evalúan las métricas?

### Las 3 métricas principales:

1. **Speaker Similarity** (Similitud de voz)
   - ¿Suena igual que el original?
   - **Bueno:** > 0.80
   - **Regular:** 0.70 - 0.80
   - **Malo:** < 0.70

2. **MCD** (Calidad del audio)
   - ¿Qué tan distorsionado está?
   - **Bueno:** < 6.0 dB
   - **Regular:** 6.0 - 8.0 dB
   - **Malo:** > 8.0 dB

3. **Mel Correlation** (Similitud espectral)
   - ¿Qué tan parecido es el espectro?
   - **Bueno:** > 0.90
   - **Regular:** 0.85 - 0.90
   - **Malo:** < 0.85

---

## Cómo ejecutar los programas de evaluación

### Evaluar un solo audio

```bash
python -m scr.metrics.metrics \
  --original inputs/reference.wav \
  --synthetic outputs/xtts/xtts_output.wav
```

### Comparar varios modelos

```bash
python evaluate_models.py \
  --reference inputs/reference.wav \
  --models outputs/xtts outputs/yourtts
```

---

## Interpretar resultados

### Ejemplo de salida:

```
Model         Speaker Similarity    MCD (dB)    Mel Correlation
xtts          0.8324               6.23        0.9156
yourtts       0.7891               7.89        0.8876
```

### ¿Qué modelo es mejor?

**XTTS es mejor** en este ejemplo porque:
- Similitud > 0.80 (vs 0.78)
- MCD < 7.0 (vs 7.89)
- Correlación > 0.90 (vs 0.88)

---

## Workflow completo

```bash
# 1. Generar audios
python main.py --model xtts --audio inputs/ref.wav --text "Hola"
python main.py --model yourtts --audio inputs/ref.wav --text "Hola"

# 2. Comparar
python evaluate_models.py \
  --reference inputs/ref.wav \
  --models outputs/xtts outputs/yourtts
```

---

## Consejos

**Audio de referencia:**
- Sin ruido de fondo
- 3-10 segundos
- Una sola persona

**Recuerda:**
- Las métricas ayudan, pero **siempre escucha los audios**
- Usa el mismo texto y referencia para comparar
- Prueba con varios audios para conclusiones fiables

---

## Archivos generados

```
outputs/comparisons/
├── xtts_metrics.json      # Métricas XTTS
├── yourtts_metrics.json   # Métricas YourTTS
└── comparison.csv         # Tabla comparativa
```