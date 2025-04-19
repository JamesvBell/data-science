#!/bin/bash

# Project Setup Script
# Usage: ./project_setup_commands.sh your-project-name

PROJECT_NAME=$1

mkdir "$PROJECT_NAME"
cd "$PROJECT_NAME"

mkdir data notebooks reports requirements src
touch README.md SETUP.md requirements/${PROJECT_NAME}_brief.md

