set -e

bash generate_protobuf.sh
pushd src
  python3 generate_db.py
popd
ls -l dist/entries.pb
ls -l dist/accents.pb
ls -l dist/phrases.pb

rm -rf src/__pycache__

mkdir -p dist/src
cp -r src/*.py src/*.proto dist/src
cp LICENSE* dist
