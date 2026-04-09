#!/bin/bash
echo "============================================"
echo "   Disk Cleaner Utility v1.0"
echo "   CSE 324 - OS Lab Project"
echo "============================================"
echo ""
echo "Scanning for temporary files..."
sleep 1

TMP_COUNT=$(find /tmp -maxdepth 1 -type f 2>/dev/null | wc -l)
echo "Found $TMP_COUNT temp files in /tmp"
echo ""

echo "--- Current Disk Usage ---"
df -h / 2>/dev/null | head -2
echo ""

echo "--- Largest Directories in Home ---"
du -sh ~/* 2>/dev/null | sort -rh | head -5
echo ""

echo "Disk cleaning simulation complete."
echo "(No files were actually deleted - this is a demo)"
echo ""
echo "============================================"
echo "  Disk Cleaner finished successfully!"
echo "============================================"
