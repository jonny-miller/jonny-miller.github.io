#!/bin/bash -x
THEMES=(
    eloquent
    rocketspacer
)
for THEME in "${THEMES[@]}"; do
    node node_modules/resume-cli export -t $THEME $THEME.html
done

