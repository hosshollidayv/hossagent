#!/usr/bin/env bash
set -euo pipefail

echo "Paste new SAM.gov API key below."
echo "It will not display while you type."
read -r -s SAM_KEY
echo

if [ -z "$SAM_KEY" ]; then
  echo "ERROR: empty key. Nothing changed."
  exit 1
fi

cat > .hossagent.secrets <<EOF
SAM_API_KEY=$SAM_KEY
EOF

chmod 600 .hossagent.secrets

echo "✓ SAM.gov key saved to .hossagent.secrets"
echo "✓ Key is not printed and should not be committed"
