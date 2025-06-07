#!/usr/bin/env bash

mkdir -p puj

protoc accents.proto --python_out=puj --pyi_out=puj
protoc entries.proto --python_out=puj --pyi_out=puj
protoc phrases.proto --python_out=puj --pyi_out=puj
protoc data.proto --python_out=puj --pyi_out=puj
