#!/bin/bash
# Monthly Clinical Profile Review Check-in Script

PROFILE_PATH="/Users/matt/projects/ai-os/context/clinical-profile.md"

echo "[Monthly Check-in] Triggering clinical profile update reminder..."

osascript -e "display notification \"Please review your weight, medications, and health baseline in context/clinical-profile.md\" with title \"🩺 Monthly Clinical Profile Review\" sound name \"Glass\""

osascript -e "display alert \"Monthly Clinical Profile Review\" message \"It is the 1st of the month! Please check if your weight, active medications (Mounjaro, Prozac, etc.), or baseline parameters in context/clinical-profile.md need updating for the trial scraper.\" buttons {\"Open Profile\", \"OK\"} default button \"OK\"" > /tmp/checkin_response.txt 2>&1

if grep -q "Open Profile" /tmp/checkin_response.txt 2>/dev/null; then
    open "$PROFILE_PATH"
fi
