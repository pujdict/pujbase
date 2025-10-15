#!/usr/bin/env bash

pushd libpuj
  protoc accents.proto --python_out=. --pyi_out=.
  protoc entries.proto --python_out=. --pyi_out=.
  protoc phrases.proto --python_out=. --pyi_out=.
popd
