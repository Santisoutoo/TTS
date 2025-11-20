IMAGE := tts-project
PROJECT_DIR := $(shell pwd)
AUDIO_REF := inputs/inference_voice_poeta.wav
TEXT := "Hi, this is captain Santiago speaking, we will be landing soon"
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
