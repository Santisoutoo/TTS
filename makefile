IMAGE := tts-project
PROJECT_DIR := $(shell pwd)
AUDIO_REF := inputs/inference_voice_plane_announcement.wav
TEXT := "Ladies and gentlemen, this is your captain speaking. We’ll be commencing our descent shortly. The weather in Santiago is reported to be partly cloudy with a temperature of around 20 degrees. We expect a smooth landing. Thank you for flying with us."
LANGUAGE := en

# Build Docker image
build:
	docker build -t $(IMAGE) .

# Open shell inside container
shell:
	docker run -it \
		--shm-size=8g \
		-v $(PROJECT_DIR):/opt/project \
		-v $(PROJECT_DIR)/inputs:/opt/project/inputs \
		-v $(PROJECT_DIR)/outputs:/opt/project/outputs \
		--rm \
		$(IMAGE) /bin/bash

# Run YourTTS
run-yourtts:
	docker run \
		--shm-size=8g \
		-e COQUI_TOS_AGREED=1 \
		-v $(PROJECT_DIR):/opt/project \
		-v $(PROJECT_DIR)/inputs:/opt/project/inputs \
		-v $(PROJECT_DIR)/outputs:/opt/project/outputs \
		--rm \
		$(IMAGE) python /opt/project/main.py \
		--model yourtts \
		--audio $(AUDIO_REF) \
		--text $(TEXT) \
		--language $(LANGUAGE)

# Run XTTS v2
run-xtts:
	docker run \
		--shm-size=8g \
		-e COQUI_TOS_AGREED=1 \
		-v $(PROJECT_DIR):/opt/project \
		-v $(PROJECT_DIR)/inputs:/opt/project/inputs \
		-v $(PROJECT_DIR)/outputs:/opt/project/outputs \
		--rm \
		$(IMAGE) python /opt/project/main.py \
		--model xtts \
		--audio $(AUDIO_REF) \
		--text $(TEXT) \
		--language $(LANGUAGE)

# Run both models
run-all: run-yourtts run-xtts

# Clean outputs
clean:
	rm -rf outputs/yourtts/* outputs/xtts/*

# Setup directories
setup:
	mkdir -p inputs outputs/yourtts outputs/xtts

.PHONY: build shell run-yourtts run-xtts run-all clean setup
