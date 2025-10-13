#!/bin/bash
# Archive old working files and clean up

set -e

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")

echo "📦 Archiving old working files..."

# Move current working files to archive with timestamp
if [ -f generated/scripts/working/*.txt ]; then
    for file in generated/scripts/working/*.txt; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            mv "$file" "generated/scripts/archive/${TIMESTAMP}_archived_${filename}"
            echo "Archived: $filename"
        fi
    done
fi

if [ -f generated/audio/working/*.mp3 ]; then
    for file in generated/audio/working/*.mp3; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            mv "$file" "generated/audio/archive/${TIMESTAMP}_archived_${filename}"
            echo "Archived: $filename"
        fi
    done
fi

if [ -f generated/metadata/working/*.json ]; then
    for file in generated/metadata/working/*.json; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            mv "$file" "generated/metadata/archive/${TIMESTAMP}_archived_${filename}"
            echo "Archived: $filename"
        fi
    done
fi

echo "✅ Archive complete! Working folders are now clean."