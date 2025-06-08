set -e

bash generate_protobuf.sh
python3 generate_entries_db.py
ls -l dist/entries.pb
python3 generate_accents_db.py
ls -l dist/accents.pb
python3 generate_phrases_db.py
ls -l dist/phrases.pb

rm -rf puj/__pycache__

cp -r puj dist
cp LICENSE* dist
