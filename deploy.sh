#!/bin/bash

set -e

echo "Building VeriMaint frontend..."

cd frontend
npm install
npm run build

echo "Copying frontend build..."

rm -rf ../backend/public
cp -R dist ../backend/public

echo "Deploying Cloudflare Worker..."

cd ../backend
./deploy.sh

echo "VeriMaint deployed."