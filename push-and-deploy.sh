#!/bin/bash
cd "$(dirname "$0")"

echo "=== PUSH TO GITHUB ==="
git add -A
git commit -m "fix: add better error handling to DashboardConscrit - show actual error details"
git push origin main

echo ""
echo "=== DEPLOY TO VERCEL ==="
cd frontend
npx vercel --prod

echo ""
echo "✅ DONE!"
