#!/bin/bash
THEMES=(
    eloquent
    rocketspacer
)
PACKAGES=""
for THEME in "${THEMES[@]}"; do
    PACKAGES="${PACKAGES} jsonresume-theme-${THEME}"
done
npm install resume-cli ${PACKAGES}
