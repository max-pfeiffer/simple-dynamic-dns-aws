#!/bin/bash

aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 887556373425.dkr.ecr.eu-central-1.amazonaws.com
docker build -t simple-dyn-dns --platform linux/arm64 -f ./container/Dockerfile .
docker tag simple-dyn-dns:latest 887556373425.dkr.ecr.eu-central-1.amazonaws.com/simple-dyn-dns:latest
docker push 887556373425.dkr.ecr.eu-central-1.amazonaws.com/simple-dyn-dns:latest
