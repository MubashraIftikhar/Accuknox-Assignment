#!/bin/bash
# Generates a self-signed cert for wisecow.local and loads it into the
# cluster as the TLS secret the Ingress expects.
set -e

DOMAIN="wisecow.local"
NAMESPACE="wisecow"

openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout tls.key \
  -out tls.crt \
  -subj "/CN=${DOMAIN}/O=${DOMAIN}"

kubectl create secret tls wisecow-tls \
  --cert=tls.crt --key=tls.key \
  -n "${NAMESPACE}" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "TLS secret 'wisecow-tls' created/updated in namespace ${NAMESPACE}."
