# Installation

### environment
```virtualenv api/env```
```api/env/Scripts/activate```
```pip install -r api/requirements.txt```
**NOTE**: do not use venv, or psycopg2 won"t be able to install

### launch postgres on docker container
```docker compose -f docker/compose/docker-compose.yaml up -d```

### inspect postgres 
```docker exec -it ting_postgres_container bash```  

```POSTGRES_PASSWORD=postgres_password```  

```psql -U postgres_user ting_postgres_db``` or 
  
```\dt``` # list tables

### test postgres connection from local machine

**NOTE**: postgres must be installed on windows, and you must add the path to the postgres bin directory (C:\Program Files\PostgreSQL\13\bin) to the system path environment variable
https://www.microfocus.com/documentation/idol/IDOL_12_0/MediaServer/Guides/html/English/Content/Getting_Started/Configure/_TRN_Set_up_PostgreSQL.htm

```psql -U postgres_user -p 5433 ting_postgres_db``` 

### query a table

```SELECT * FROM supplier;``` !!! ricorda ";" 

### RUN
./setup.sh 

### NGINX LOGS
https://stackoverflow.com/questions/30269672/unable-to-use-lt-when-running-nginx-docker-or-cat-logs
if Internal Server Error, check logs from app (docker logs app_container_name)

### KUBERNETES
#### Components
**node**: machine in which pods run
**pod**: abstraction over a container. One container per pod usually.
- each pod has an internal IP address.
- pods are ephemeral. When they die, their IP changes
**service**: static IP attached to a pod. When pod dies, service IP remains. Pods communicate with each other through service IP
- external service: accessible to the public
- internal service: accessible only by other pods
**ingress**: assigns a domain name to the service IP to be better looking for the public
**deployment**: abstraction over pods. Developer creates deployments, not pods, because one deployment of an app can have multiple replicas (**replicaset**) in many pods
**statefulset**: deployment for stateful applications like databases, to manage issues like consistency and concurrency. However, better practice to deploy a database outside the kubernetes cluster
**configmap**: store config
**secret**: store secret config
**volume**: permanent storage of data if pod dies

#### Architecture
**worker node**: Hosts the pods and performs all operations. Nodes are replicated for resilience. 3 processes are installed on a worker node:
- Container runtime (Docker)
- Kubelet: schedules containers
- Kube proxy: communication between services and pods
**master node**: Manages worker nodes. Also replicated. Needs less resources than worker nodes. 4 processes are intalled on a master node:
- API server: cluster gateway and gatekeeper for authentication. Single point of access to the cluster
- Scheduler: decides on which worker node your request will be run, depending on business of pods and resources required by your request. NOTE: it is actually kubelet that processes the request
- Controller manager: detects and recover dead pods
- Etcd: cluster data (pod state, etc. Not actual application data) as key-value store

#### Service Types
https://medium.com/google-cloud/kubernetes-nodeport-vs-loadbalancer-vs-ingress-when-should-i-use-what-922f010849e0
1. ClusterIP (default): Pods only accessible from within the cluster. Outside communicates through Ingress
    - NOTE: for debugging, access cluster through Kubernetes Proxy, using kubectl as authenticated user https://medium.com/google-cloud/kubernetes-nodeport-vs-loadbalancer-vs-ingress-when-should-i-use-what-922f010849e0
2. NodePort: Pods accessible from outside, through a fixed port. No Ingress, browser sends requests directly (less secure)
3. LoadBalancer: Pods accessible through cloud-provider's load balancer

#### Port Types:
- Container:
    - containerPort: pod's port exposed to the cluster (mostly informational - if not specified, pod will still expose a port to the cluster)
- Service:
    - port: port where Service is accessible by other pods
    - targetPort: must match containerPort in Container - port to forward a request to when Service receives a request 
    - nodePort (only if service type is NodePort): port exposed by the Node to the outside world. If blank, K8s will assign a random one.

### CONVERT DOCKER-COMPOSE TO KUBERNETES
https://kubernetes.io/docs/tasks/configure-pod-container/translate-compose-kubernetes/

# Common Errors
## NGINX
#### 502: Bad Gateway
Nginx is reacheable, host defined in nginx.conf exists, but nginx cannot forward requests to that host. Could be host existing but it's not the target one, or an error in the application server

## UWSGI
#### invalid request block size
You deployed UWSGI without NGINX and used socket:8080 instead of http:8080 in api.ini

### App Design
# Insert from UI
- choose table: suppliers, items, purchases
    > GET tables/: display all available resources
    > GET tables/<name:string>: display columns ( body: ALL)
- insert data in table columns
    > PUT supplier/<name:string> (fields in body)
    > PUT item/<name:string> (fields in body)
    > PUT purchase/<item_id:string> (fields in body)

# Insert by uploading a table
- choose table: suppliers, items, purchases > validate table
    > validation triggered internally by code when PUT
- upload table > each field is inserted in database
    > upload with PUT in for loop

# Deleting from UI
- same as query > then action: delete

# Query Resource from UI
- choose resource: supplier, item, purchases / all
    > GET or DELETE suppliers/
    > GET or DELETE items/
    > GET or DELETE purchases/
- choose columns to display / all
    > GET resources/<name:string>: display columns ( body: ALL VS QUERIABLE )
- choose filters / none
    - choose resource: supplier, item, purchase
    - choose column
    - choose operator: equals, greater/lower
        > GET or DELETE supplier?table=table?field=value
        > GET or DELETE item?table=table?field=value
        > GET or DELETE purchase?table=table?field=value

# LINKS
UPLOADING FILES: https://www.youtube.com/watch?v=6WruncSoCdI
BULK https://stackoverflow.com/questions/3659142/bulk-insert-with-sqlalchemy-orm
