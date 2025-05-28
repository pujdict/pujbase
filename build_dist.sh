set -e

bash generate_protobuf.sh
python3 generate_entries_db.py
ls -l dist/entries.pb
python3 generate_accents_db.py
ls -l dist/entries.pb
