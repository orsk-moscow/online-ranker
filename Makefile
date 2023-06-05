# Author: Igor Popov
# All the launch' parameters are set at the top of this file

# the docker-compose file to use
DC_FILE = docker-compose.yml
# the project name (see it on top of your Docker GUI)
PN = wolt

# the docker-compose command, can be changed to `docker compose` if you have it
DC = docker-compose

# the Dockerfile to build the image for the cache DB:
DF_CACHE = cache/cache.Dockerfile
# the tag of the image to build
TAG_CACHE = cache:latest

# the Dockerfile to build the image for the cache DB:
DF_APP = app/app.Dockerfile
# the tag of the image to build
TAG_APP = app:latest

# the Dockerfile to build the image for the cache DB:
DF_TRAIN = train/train.Dockerfile
# the tag of the image to build
TAG_TRAIN = train:latest

define HELP_MESSAGE
Available options and flags

# GENERAL
help:		show this message

# BUILD IMAGES
bapp:		build image from `$(DF_APP)` with tag `$(TAG_APP)`
bcache:		build image from `$(DF_CACHE)` with tag `$(TAG_CACHE)`
btrain:		build image from `$(DF_TRAIN)` with tag `$(TAG_TRAIN)`

# OPERATE WITH CONTAINERS
up:     	make the containers from `$(DC_FILE)` up 
stop:   	stop the containers from `$(DC_FILE)`
start:  	start the containers from `$(DC_FILE)`
down:   	make the containers from `$(DC_FILE)` down 
du:     	consistently execute down and up

# UNIVERSAL RULES
all:		build `$(TAG_APP)`, `$(TAG_CACHE)`, `$(TAG_TRAIN)` and run the containers from `$(DC_FILE)`
clean:		clean all the containers
re:         relaunch the containers

endef
export HELP_MESSAGE

help: 
	@echo "$$HELP_MESSAGE"

# NOTE We need to set the following environment variables before running the commands, because of the [hard multi-stage builds](https://stackoverflow.com/questions/64221861/an-error-failed-to-solve-with-frontend-dockerfile-v0) on M1 processors:
bcache:
	@export DOCKER_BUILDKIT=1
	@export COMPOSE_DOCKER_CLI_BUILD=0
	@docker build  -t $(TAG_CACHE) -f $(DF_CACHE) ./cache

bapp:
	@export DOCKER_BUILDKIT=1
	@export COMPOSE_DOCKER_CLI_BUILD=0
	@docker build  -t $(TAG_APP) -f $(DF_APP) .

# btrain:
# 	@export DOCKER_BUILDKIT=1
# 	@export COMPOSE_DOCKER_CLI_BUILD=0
# 	@docker build  -t $(TAG_TRAIN) -f $(DF_TRAIN) .

up:
	@$(DC) -f $(DC_FILE) -p "$(PN)" up

down: 
	@$(DC) -f $(DC_FILE) down

du: down up

stop: 
	@$(DC) -f $(DC_FILE) stop

start:
	@$(DC) -f $(DC_FILE) start

clean: down
	@docker system prune -f

all: bcache bapp up

re: clean up