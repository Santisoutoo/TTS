IMAGE := tts-project
PROJECT_DIR := $(shell pwd)

# Build image
build:
	docker build -t $(IMAGE) .

# Open shell inside container
shell:
	docker run -it \
		--shm-size=8g \
		-v $(PROJECT_DIR):/opt/project \
		-v $(PROJECT_DIR)/outputs:/opt/project/outputs \
        --rm \
		$(IMAGE) /bin/bash

# Run Tortoise-TTS
run-tortoise:
	docker run \
		--shm-size=8g \
		-v $(PROJECT_DIR):/opt/project \
		-v $(PROJECT_DIR)/outputs:/opt/project/outputs \
		--rm \
		$(IMAGE) python /opt/project/main.py --model tortoise

# Run GPT-SoVITS
run-sovits:
	docker run \
		--shm-size=8g \
		-v $(PROJECT_DIR):/opt/project \
		-v $(PROJECT_DIR)/outputs:/opt/project/outputs \
		--rm \
		$(IMAGE) python /opt/project/main.py --model sovits

# Run Coqui-TTS
run-coqui:
	docker run \
		--shm-size=8g \
		-v $(PROJECT_DIR):/opt/project \
		-v $(PROJECT_DIR)/outputs:/opt/project/outputs \
		--rm \
		$(IMAGE) python /opt/project/main.py --model coqui
