#!/bin/bash

# PDB Files Download Script
# Downloads specified PDB files from the RCSB Protein Data Bank

# Create output directory
OUTPUT_DIR="pdb_files"
mkdir -p "$OUTPUT_DIR"

echo "PDB Files Download Script"
echo "========================="
echo "Output directory: $OUTPUT_DIR"
echo ""

# Array of PDB IDs to download
PDB_IDS=(
    "1AVX" "1ZAD" "1F34" "1B3Y" "1YAG" "2G8P" "2B0D" "1E6Z" "1B3Z" "1G2D"
    "1FIN" "2CRN" "1M1Q" "1TEN" "1BPI" "2HTM" "1A4Y" "1VFB" "2L0J" "1LYZ"
    "1M40" "2B0K" "1E9H" "2B0M" "2LYZ" "3PBL" "1ZAC" "1PDB" "1B41" "2B0I"
    "2KJ3" "1D8V" "2B0F" "1A2Z" "2H5N" "1L2Y" "1D5Y" "1A00" "1D3Z" "1B3X"
    "1ZAI" "4HHB" "1B3T" "3B4R" "1C00" "3B4Z" "2B0J" "1B00" "1H9D" "3B50"
    "1FJL" "2FHA" "1GFL" "1B3W" "1ZAG" "2B0L" "1CMA" "3B4V" "3B4S" "1HCL"
    "1D00" "1ZAF" "5YAG" "1ZAH" "1A3N" "1UBI" "4YAG" "1K60" "2B4J" "3B4U"
    "3B4W" "1AAY" "1ZAB" "3C2N" "4GCR" "1HTM" "2YAG" "3B4X" "1X8R" "1B40"
    "2B0H" "3B4T" "3B4Y" "1UBQ" "1B3U" "1HAG" "3YAG" "1SVA" "1J2Q" "1ZAJ"
    "1ZAA" "1ZAE" "1C4Z" "1L1O" "1CRN" "3HVT" "1A3O" "1A2K" "1B3V" "2B0G"
    "2K39" "1JXO" "2B0E" "1B42"
)

# Initialize counters
TOTAL_FILES=${#PDB_IDS[@]}
SUCCESSFUL_DOWNLOADS=0
FAILED_DOWNLOADS=0
SKIPPED_FILES=0

echo "Total PDB files to download: $TOTAL_FILES"
echo ""

# Function to download a single PDB file
download_pdb() {
    local pdb_id="$1"
    local output_file="$OUTPUT_DIR/${pdb_id}.pdb"

    # Check if file already exists
    if [ -f "$output_file" ]; then
        echo "⏭️  Skipping $pdb_id (already exists)"
        ((SKIPPED_FILES++))
        return 0
    fi

    echo "📥 Downloading $pdb_id..."

    # Primary URL from RCSB PDB
    local pdb_url="https://files.rcsb.org/download/${pdb_id}.pdb"

    # Download with wget (with timeout and retry)
    if command -v wget >/dev/null 2>&1; then
        if wget -q --timeout=30 --tries=2 "$pdb_url" -O "$output_file"; then
            # Verify the file is not empty and contains PDB content
            if [ -s "$output_file" ] && grep -q "HEADER\|ATOM\|HETATM" "$output_file" 2>/dev/null; then
                echo "✅ Successfully downloaded $pdb_id"
                ((SUCCESSFUL_DOWNLOADS++))
                return 0
            else
                echo "❌ Downloaded file appears invalid for $pdb_id"
                rm -f "$output_file"
            fi
        fi
    # Fallback to curl if wget is not available
    elif command -v curl >/dev/null 2>&1; then
        if curl -s --max-time 30 --retry 2 "$pdb_url" -o "$output_file"; then
            # Verify the file is not empty and contains PDB content
            if [ -s "$output_file" ] && grep -q "HEADER\|ATOM\|HETATM" "$output_file" 2>/dev/null; then
                echo "✅ Successfully downloaded $pdb_id"
                ((SUCCESSFUL_DOWNLOADS++))
                return 0
            else
                echo "❌ Downloaded file appears invalid for $pdb_id"
                rm -f "$output_file"
            fi
        fi
    else
        echo "❌ Neither wget nor curl is available"
        exit 1
    fi

    # Try alternative URL if primary failed
    echo "🔄 Trying alternative URL for $pdb_id..."
    local alt_url="https://files.rcsb.org/view/${pdb_id}.pdb"

    if command -v wget >/dev/null 2>&1; then
        wget -q --timeout=30 --tries=2 "$alt_url" -O "$output_file"
    elif command -v curl >/dev/null 2>&1; then
        curl -s --max-time 30 --retry 2 "$alt_url" -o "$output_file"
    fi

    # Final verification
    if [ -s "$output_file" ] && grep -q "HEADER\|ATOM\|HETATM" "$output_file" 2>/dev/null; then
        echo "✅ Successfully downloaded $pdb_id (alternative URL)"
        ((SUCCESSFUL_DOWNLOADS++))
    else
        echo "❌ Failed to download $pdb_id"
        rm -f "$output_file"
        ((FAILED_DOWNLOADS++))
    fi
}

# Download all PDB files
echo "Starting downloads..."
echo ""

for pdb_id in "${PDB_IDS[@]}"; do
    download_pdb "$pdb_id"
    # Small delay to be respectful to the server
    sleep 0.5
done

# Summary
echo ""
echo "Download Summary"
echo "================"
echo "Total files:        $TOTAL_FILES"
echo "Successful:         $SUCCESSFUL_DOWNLOADS"
echo "Failed:             $FAILED_DOWNLOADS"
echo "Skipped (existing): $SKIPPED_FILES"
echo ""

if [ $FAILED_DOWNLOADS -gt 0 ]; then
    echo "⚠️  Some downloads failed. You may want to retry failed downloads manually."
    echo "Files are stored in: $OUTPUT_DIR/"
else
    echo "🎉 All downloads completed successfully!"
    echo "Files are stored in: $OUTPUT_DIR/"
fi

# List downloaded files
echo ""
echo "Downloaded files:"
ls -1 "$OUTPUT_DIR"/*.pdb 2>/dev/null | wc -l | xargs echo "Total .pdb files:"
echo ""

# Optional: Show disk usage
if command -v du >/dev/null 2>&1; then
    echo "Total size: $(du -sh "$OUTPUT_DIR" 2>/dev/null | cut -f1)"
fi
