#!/bin/bash

PROJECT_DIR=$1

cp ./Dockerfile "$PROJECT_DIR/docker/Dockerfile"
cp ./run_docker.sh "$PROJECT_DIR/docker/run_docker.sh"
cp ./app.py "$PROJECT_DIR/app.py"

rm "$PROJECT_DIR/cli/core/inference.py"
wget https://raw.githubusercontent.com/blue0620/simple_reading_order/main/inference.py -P "$PROJECT_DIR/cli/core/"
wget https://lab.ndl.go.jp/dataset/ndlocr/appendix/simple_reading_order_model.joblib -P "$PROJECT_DIR"