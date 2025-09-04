#!/bin/bash

# UniProt Entries Download Script
# Downloads specified UniProt entries from the UniProt database
# Supports multiple formats: FASTA, XML, TXT, GFF

# Configuration
OUTPUT_DIR="uniprot_files"
DEFAULT_FORMAT="fasta"  # Options: fasta, xml, txt, gff

# Help function
show_help() {
    echo "UniProt Entries Download Script"
    echo "==============================="
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -f, --format FORMAT    Download format (fasta, xml, txt, gff) [default: fasta]"
    echo "  -o, --output DIR       Output directory [default: uniprot_files]"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Available formats:"
    echo "  fasta    - FASTA protein sequences (.fasta)"
    echo "  xml      - UniProtKB XML format (.xml)"
    echo "  txt      - UniProtKB text format (.txt)"
    echo "  gff      - General Feature Format (.gff)"
    echo ""
    echo "Example:"
    echo "  $0                     # Download in FASTA format"
    echo "  $0 -f xml             # Download in XML format"
    echo "  $0 -f txt -o my_dir   # Download in TXT format to custom directory"
}

# Parse command line arguments
FORMAT="$DEFAULT_FORMAT"
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--format)
            FORMAT="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate format
case $FORMAT in
    fasta|xml|txt|gff)
        ;;
    *)
        echo "Error: Invalid format '$FORMAT'. Use: fasta, xml, txt, or gff"
        exit 1
        ;;
esac

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "UniProt Entries Download Script"
echo "==============================="
echo "Format: $FORMAT"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Array of UniProt IDs to download
UNIPROT_IDS=(
    "P01040" "P08581" "P63279" "P00785" "P00927" "P01038" "P00920" "P0ADL1" "P29275" "P02737"
    "P02594" "P00786" "P12345" "P02349" "P00780" "P00784" "P00777" "P42574" "P00935" "P00939"
    "P0DPA6" "Q13485" "P00928" "P27320" "P01131" "P02743" "P28222" "P00363" "P00373" "P00352"
    "P27329" "P02598" "P02735" "P00360" "P00365" "P27327" "P02341" "P00933" "P32241" "P0C0L8"
    "O43641" "P0ABJ5" "P0C0L7" "P41143" "P38398" "P62158" "P0DPA4" "P0DPA5" "Q14790" "P02595"
    "P00361" "P02742" "P02736" "P00366" "P01128" "P00362" "P00782" "P01043" "P00367" "P02347"
    "Q9H234" "P27986" "P00769" "P01344" "P01112" "P21728" "P01123" "P00922" "P62258" "P11229"
    "P00750" "A0A0A6YY23" "P00364" "P0ABJ2" "P0ACK8" "P27315" "P02343" "P02734" "P27319" "P13579"
    "P01035" "Q9H232" "P01129" "P02587" "P01942" "P00919" "P00929" "P27313" "Q92753" "P06213"
    "P00934" "P0ABJ8" "P00374" "P02588" "P68371" "P00774" "P01132" "P04637" "P00781" "P84022"
    "P02740" "Q9Y262" "P00941" "P0ACK2" "P41595" "P02744" "P0C0L5" "P41145" "Q9Y261" "P0DPA3"
    "Q15797" "P42857" "P0ACK0" "P27314" "P00356" "P27321" "P01135" "P01134" "P27307" "P02590"
    "Q15303" "P35916" "P0ACK6" "P0ABJ9" "P27317" "Q03167" "P29274" "P00351" "P27318" "P01122"
    "P00357" "Q15392" "P01044" "P02340" "P27326" "P35355" "P41594" "P28223" "P01116" "P21860"
    "P02592" "P13945" "P02745" "P02353" "P27328" "P02346" "P61073" "P27310" "P0ABJ4" "P35348"
    "P00778" "P27323" "P27330" "P00926" "P00358" "P0ACK1" "P01941" "P02738" "Q9H228" "Q05516"
    "P34969" "P0ABH9" "P51679" "P55212" "P00369" "P20226" "P00938" "Q01094" "O15111" "P10275"
    "P35462" "P54321" "P00776" "Q02750" "P00787" "O15151" "Q9H235" "O15350" "P11230" "Q99459"
    "P0ACK5" "P00930" "P00937" "P0ABJ7" "P02350" "P00783" "P27325" "P01133" "P02593" "Q9Y5N1"
    "P02741" "P0ACK3" "Q99717" "P01124" "P09876" "P00790" "P01126" "P06239" "Q9Y263" "P27311"
    "A0A0A6YY25" "P27309" "P10424" "P01036" "P69905" "P00768" "P00772" "P0ABJ3" "P0ADL3" "P02344"
    "P01037" "P01032" "P27324" "P01042" "P15056" "P00770" "P00372" "P00924" "P00779" "P06241"
    "Q9H231" "Q9H233" "Q13154" "P01039" "P08100" "P16410" "P01127" "P01041" "P63000" "P60709"
    "P02585" "P0ACK9" "P35367" "P62873" "P02591" "P01308" "P00940" "P24530" "P35372" "P19544"
    "P35659" "P68871" "P00932" "P53805" "P10826" "P00370" "P00918" "Q96P88" "P67890" "P0C0L6"
    "P00773" "P00942" "P35568" "P0C0L4" "P00775" "Q9H229" "P00789" "P0ABJ6" "P02597" "P02352"
    "A0A0A6YY26" "P01125" "P00788" "P0DPA2" "A0A0A6YY27" "P00371" "P36544" "P0ACK4" "Q9Y260" "P02351"
    "P30542" "P00354" "Q92786" "P00936" "P01034" "P02739" "P00925" "Q13639" "P27316" "Q9Y264"
    "P32238" "P01189" "P01130" "P27306" "P02589" "Q13153" "P42336" "P00359" "P43286" "A0A0A6YY24"
    "P55210" "P12931" "P00368" "P00931" "P00355" "P04626" "P00766" "P00923" "P00921" "Q15796"
    "P00767" "Q9H230" "P0ABJ0" "P00533" "Q12888" "P01033" "P27308" "P55211" "P03070" "P02596"
    "P15332" "P27322" "P02348" "P02345" "P00771" "P27312" "P41240" "P00353" "P02342" "O00444"
    "P0ABJ1" "P07948" "P0ACK7" "P63104" "P01031" "P52946" "P07947" "P0ADL2" "P00350" "P0ADL0"
    "P02586"
)

# Initialize counters
TOTAL_FILES=${#UNIPROT_IDS[@]}
SUCCESSFUL_DOWNLOADS=0
FAILED_DOWNLOADS=0
SKIPPED_FILES=0

echo "Total UniProt entries to download: $TOTAL_FILES"
echo ""

# Function to get file extension based on format
get_file_extension() {
    case $1 in
        fasta) echo "fasta" ;;
        xml) echo "xml" ;;
        txt) echo "txt" ;;
        gff) echo "gff" ;;
        *) echo "txt" ;;
    esac
}

# Function to get UniProt URL based on format
get_uniprot_url() {
    local uniprot_id="$1"
    local format="$2"

    case $format in
        fasta)
            echo "https://rest.uniprot.org/uniprotkb/${uniprot_id}.fasta"
            ;;
        xml)
            echo "https://rest.uniprot.org/uniprotkb/${uniprot_id}.xml"
            ;;
        txt)
            echo "https://rest.uniprot.org/uniprotkb/${uniprot_id}.txt"
            ;;
        gff)
            echo "https://rest.uniprot.org/uniprotkb/${uniprot_id}.gff"
            ;;
        *)
            echo "https://rest.uniprot.org/uniprotkb/${uniprot_id}.txt"
            ;;
    esac
}

# Function to validate downloaded content based on format
validate_content() {
    local file="$1"
    local format="$2"

    if [ ! -s "$file" ]; then
        return 1
    fi

    case $format in
        fasta)
            grep -q "^>" "$file" 2>/dev/null
            ;;
        xml)
            grep -q "<entry\|<?xml" "$file" 2>/dev/null
            ;;
        txt)
            grep -q "^ID\|^AC\|^DE" "$file" 2>/dev/null
            ;;
        gff)
            grep -q "##gff-version\|^#" "$file" 2>/dev/null
            ;;
        *)
            return 0  # Default to valid for unknown formats
            ;;
    esac
}

# Function to download a single UniProt entry
download_uniprot() {
    local uniprot_id="$1"
    local file_ext=$(get_file_extension "$FORMAT")
    local output_file="$OUTPUT_DIR/${uniprot_id}.${file_ext}"

    # Check if file already exists
    if [ -f "$output_file" ]; then
        echo "⏭️  Skipping $uniprot_id (already exists)"
        ((SKIPPED_FILES++))
        return 0
    fi

    echo "📥 Downloading $uniprot_id ($FORMAT format)..."

    local uniprot_url=$(get_uniprot_url "$uniprot_id" "$FORMAT")

    # Download with wget
    if command -v wget >/dev/null 2>&1; then
        if wget -q --timeout=30 --tries=3 "$uniprot_url" -O "$output_file"; then
            if validate_content "$output_file" "$FORMAT"; then
                echo "✅ Successfully downloaded $uniprot_id"
                ((SUCCESSFUL_DOWNLOADS++))
                return 0
            else
                echo "❌ Downloaded file appears invalid for $uniprot_id"
                rm -f "$output_file"
            fi
        fi
    # Fallback to curl
    elif command -v curl >/dev/null 2>&1; then
        if curl -s --max-time 30 --retry 3 "$uniprot_url" -o "$output_file"; then
            if validate_content "$output_file" "$FORMAT"; then
                echo "✅ Successfully downloaded $uniprot_id"
                ((SUCCESSFUL_DOWNLOADS++))
                return 0
            else
                echo "❌ Downloaded file appears invalid for $uniprot_id"
                rm -f "$output_file"
            fi
        fi
    else
        echo "❌ Neither wget nor curl is available"
        exit 1
    fi

    # If we get here, download failed
    echo "❌ Failed to download $uniprot_id"
    rm -f "$output_file"
    ((FAILED_DOWNLOADS++))
}

# Download all UniProt entries
echo "Starting downloads..."
echo ""

for uniprot_id in "${UNIPROT_IDS[@]}"; do
    download_uniprot "$uniprot_id"
    # Small delay to be respectful to the server
    sleep 0.3
done

# Create a summary file
SUMMARY_FILE="$OUTPUT_DIR/download_summary.txt"
cat > "$SUMMARY_FILE" << EOF
UniProt Download Summary
========================
Date: $(date)
Format: $FORMAT
Total entries: $TOTAL_FILES
Successful downloads: $SUCCESSFUL_DOWNLOADS
Failed downloads: $FAILED_DOWNLOADS
Skipped (existing): $SKIPPED_FILES

Downloaded UniProt IDs:
EOF

# Add list of successfully downloaded files
for file in "$OUTPUT_DIR"/*."$(get_file_extension "$FORMAT")"; do
    if [ -f "$file" ]; then
        basename "$file" .$(get_file_extension "$FORMAT") >> "$SUMMARY_FILE"
    fi
done 2>/dev/null

# Summary
echo ""
echo "Download Summary"
echo "================"
echo "Total entries:      $TOTAL_FILES"
echo "Successful:         $SUCCESSFUL_DOWNLOADS"
echo "Failed:             $FAILED_DOWNLOADS"
echo "Skipped (existing): $SKIPPED_FILES"
echo ""

if [ $FAILED_DOWNLOADS -gt 0 ]; then
    echo "⚠️  Some downloads failed. Check network connection or try again later."
    echo "Failed downloads may be due to:"
    echo "   - Network connectivity issues"
    echo "   - Invalid/obsolete UniProt IDs"
    echo "   - Server temporarily unavailable"
else
    echo "🎉 All downloads completed successfully!"
fi

echo ""
echo "Files are stored in: $OUTPUT_DIR/"
echo "Summary saved to: $SUMMARY_FILE"

# Show file count and disk usage
file_count=$(ls -1 "$OUTPUT_DIR"/*."$(get_file_extension "$FORMAT")" 2>/dev/null | wc -l)
echo ""
echo "Downloaded $(get_file_extension "$FORMAT") files: $file_count"

if command -v du >/dev/null 2>&1; then
    echo "Total size: $(du -sh "$OUTPUT_DIR" 2>/dev/null | cut -f1)"
fi

# Optional: Show first few files as examples
echo ""
echo "Example files:"
ls -1 "$OUTPUT_DIR"/*."$(get_file_extension "$FORMAT")" 2>/dev/null | head -5
