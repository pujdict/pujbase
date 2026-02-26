set -e

# Pull the submodule in data/pujcorpora
pushd data/pujcorpora
  git submodule update --init .
popd

pip install -e .

bash generate_protobuf.sh
pushd libpuj
  python3 generate_db.py
popd
ls -l dist/entries.pb
ls -l dist/accents.pb
ls -l dist/phrases.pb

rm -rf libpuj/__pycache__

mkdir -p dist/libpuj
cp -r libpuj/*.py libpuj/*.proto dist/libpuj
cp LICENSE* dist
