# Wisecow on Kubernetes — Problem 1

Containerized and deployed the Wisecow app on Kubernetes with TLS and CI/CD.

## What I did

1. **Dockerized** the app — Ubuntu-based image, non-root user, installs bash/fortune-mod/cowsay/netcat-openbsd.
2. **Pushed image to Docker Hub**: `mubashraiftikhar10/wisecow`
3. **Deployed to Kubernetes** (kind cluster on AWS EC2) — Deployment (2 replicas) + Service, in a dedicated `wisecow` namespace.
4. **Added TLS** via ingress-nginx + a self-signed cert for `wisecow.local`.
5. **Set up CI/CD** with GitHub Actions (self-hosted runner on the same EC2 box) — every push to `Problem1/` builds the image, pushes it to Docker Hub, and auto-deploys it to the cluster.

## Repo structure

```
Accuknox-Assignment/
├── .github/workflows/problem1-ci-cd.yaml
├── Problem1/
│   ├── wisecow.sh
│   ├── Dockerfile
│   ├── k8s/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml
│   └── certs/
│       └── generate-cert.sh
├── .gitignore
└── README.md
```

## Screenshots

**Docker build + run working locally**
<!-- ADD SS HERE -->

**Image pushed to Docker Hub**
<!-- ADD SS HERE -->

**Pods running on Kubernetes**
<!-- ADD SS HERE -->

**Service + Ingress + TLS secret created**
<!-- ADD SS HERE -->

**HTTPS working (curl to wisecow.local)**
<!-- ADD SS HERE -->

**GitHub Actions pipeline running successfully**
<!-- ADD SS HERE -->

**Pods updated after pipeline deploy**
<!-- ADD SS HERE -->

## Live Actions runs
https://github.com/MubashraIftikhar/Accuknox-Assignment/actions

## How to reproduce

```bash
git clone https://github.com/MubashraIftikhar/Accuknox-Assignment.git
cd Accuknox-Assignment/Problem1

# Build & test image locally
docker build -t wisecow:local .
docker run --rm -p 4499:4499 wisecow:local

# Create cluster + namespace
kind create cluster --name wisecow
kubectl create namespace wisecow

# Install ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Deploy app
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Generate TLS cert + secret
cd certs && ./generate-cert.sh && cd ..

# Test
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8443:443 &
curl -k https://wisecow.local:8443 --resolve wisecow.local:8443:127.0.0.1
```
