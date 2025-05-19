#!/usr/bin/env bash

protoc entries.proto --python_out=. --pyi_out=.
