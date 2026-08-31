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

## Demonstration

**Docker build + run working locally**
---
<img width="749" height="214" alt="image" src="https://github.com/user-attachments/assets/7ee1129f-96ed-45ee-89b6-eb10803e4ca1" />

<img width="571" height="355" alt="WhatsApp Image 2026-08-31 at 3 46 13 PM" src="https://github.com/user-attachments/assets/fa0ad8df-5f47-4fbf-acdf-967cb6cea2b9" />

---
**Image pushed to Docker Hub**
---
<img width="931" height="368" alt="image" src="https://github.com/user-attachments/assets/921a7b9b-ec0a-4237-ba3e-80e75edf07b1" />

---
**Pods running on Kubernetes**
---
<img width="732" height="79" alt="WhatsApp Image 2026-08-31 at 3 51 59 PM" src="https://github.com/user-attachments/assets/14be84ca-5093-4ef6-8354-9308fe2090f7" />

---
**Service + Ingress + TLS secret created**
---
<img width="880" height="249" alt="WhatsApp Image 2026-08-31 at 3 52 12 PM" src="https://github.com/user-attachments/assets/e8bdd72c-472c-4cf3-9900-740219e8c47f" />

---
**HTTPS working (curl to wisecow.local)**
---
<img width="623" height="340" alt="image" src="https://github.com/user-attachments/assets/2b4f9076-4941-4e5b-bd96-c10ff7c2cdca" />

<img width="1176" height="405" alt="WhatsApp Image 2026-08-31 at 2 52 30 PM" src="https://github.com/user-attachments/assets/78376fa8-6206-4edf-b9ef-2bc2fd40e7d9" />

---
**SelfHosted Runner**
---
<img width="1566" height="655" alt="WhatsApp Image 2026-08-31 at 3 08 57 PM" src="https://github.com/user-attachments/assets/10790020-7595-42da-9777-24c0b245be5f" />
<img width="1600" height="476" alt="WhatsApp Image 2026-08-31 at 3 10 19 PM" src="https://github.com/user-attachments/assets/c22adb6c-10c2-450b-a0b2-c8d20f59a803" />


---
**GitHub Actions pipeline running successfully**
---
<img width="749" height="214" alt="image" src="https://github.com/user-attachments/assets/2e9edd24-1c4b-44fb-ae9c-cf8de2156163" />

---
**Pods updated after pipeline deploy**
---
<img width="432" height="101" alt="image" src="https://github.com/user-attachments/assets/b27205cd-23fd-40d5-ac79-2b7e4db6f8b0" />


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
