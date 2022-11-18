call kubectl delete --all deployments
call kubectl delete --all services
call kubectl delete --all pods
call kubectl apply -f postgres/service.yaml
call kubectl apply -f minio/service.yaml
if %1==1 (
    call docker rmi docker.registry.me:4001/ting-api
    call docker build ./api -t docker.registry.me:4001/ting-api
)
call kubectl apply -f api/deployment.yaml
if %2==1 (
    call docker rmi docker.registry.me:4001/nginx
    call docker build ./nginx -t docker.registry.me:4001/nginx
)
if %3==1 (
    call kubectl apply -f nginx/deployment.yaml
)
call kubectl get deployments
cmd /k