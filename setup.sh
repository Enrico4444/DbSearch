# LOCAL DEPLOYMENT
virtualenv api/env
api/env/Scripts/activate
pip install -r api/requirements.txt
docker-compose --env-file ./api/src/local.env up -d --build postgresdb minio
cd api/src
python app.py local

# DEPLOYMENT WITH DOCKER COMPOSE
# windows: $env:ENVIRON=dev
docker-compose --env-file ./api/src/prod.env up -d --build postgresdb minio
docker-compose --env-file ./api/src/prod.env up -d --build api nginx

# DEPLOYMENT WITH MINIKUBE
# minikube start
# kubectl cluster-info
# kubectl get nodes

# DEPLOYMENT WITH KUBERNETES IN DOCKER DESKTOP
# Minikube on windows cannot communicate with docker as they are on two separate VMs
# Thus, it cannot pull images from local docker registry. It will give error: cannot connect
# In alternative, use minikube load <local-image-name> and then the image can be used from within kubernetes, without the need of a local registry: https://www.youtube.com/watch?v=-g9r8BSlDFI

# Thus, use Docker Desktop Kubernetes feature: https://docs.docker.com/desktop/kubernetes/
# This makes kubernetes (single node) run inside a docker container on the same VM as docker
# 1. Enable Kubernetes on Docker Desktop: Settings > Kubernetes > Enable Kubernetes > Restart and Install
# 2. Ensure kubectl command points to Docker Desktop and not minikube
kubectl config get-contexts
kubectl config use-context docker-desktop

# create a local registry

# IMPORTANT: docker push cannot resolve localhost or 127.0.0.1. 
# Thus, add to hosts file (C:\Windows\System32\drivers\etc\hosts) entry 127.0.0.1 docker.registry.me
# This maps localhost to docker.registry.me DNS, with which now the registry can be referred to
# https://github.com/docker/for-mac/issues/3611
# https://www.manageengine.com/network-monitoring/how-to/how-to-add-static-entry.html

# TODO: setup password for private registry, then supply credentials to kubernetes (see section: You're using a private registry in link below)
# https://www.tutorialworks.com/kubernetes-imagepullbackoff/#:~:text=So%20what%20exactly%20does%20ImagePullBackOff,'back%2Doff').
# see also how to setup tls, basic auth:
# https://medium.com/@ManagedKube/docker-registry-2-setup-with-tls-basic-auth-and-persistent-data-8b98a2a73eec
# https://stackoverflow.com/questions/38247362/how-i-can-use-docker-registry-with-login-password
# https://github.com/distribution/distribution/blob/main/docs/deploying.md

docker run -d -p 4001:4001 --restart=always --name registry registry:2

# build db and minio containers
docker-compose --env-file ./api/src/k8s.env up -d --build postgresdb minio

# build my images and push them to the registry
cd api
docker build . -t docker.registry.me:4001/ting-api
docker push docker.registry.me:4001/ting-api
cd ../nginx
docker build . -t docker.registry.me:4001/nginx
docker push docker.registry.me:4001/nginx

# deploy on kubernetes
cd ../api
kubectl apply -f deployment.yaml
cd ../nginx
kubectl apply -f deployment.yaml
# go to localhost:30007

