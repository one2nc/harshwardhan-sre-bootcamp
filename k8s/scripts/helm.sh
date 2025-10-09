
#ESO
helm repo add external-secrets https://charts.external-secrets.io
helm upgrade --install external-secrets \
   external-secrets/external-secrets \
    -n eso-ns \
    --create-namespace \
    --set installCRDs=true \
    --set global.nodeSelector.type=dependent_services

#Vault
helm repo add hashicorp https://helm.releases.hashicorp.com
helm upgrade --install vault hashicorp/vault -n vault-ns \
    --create-namespace \
    --set injector.enabled=false \
    --set server.nodeSelector.type=dependent_services

kubectl apply -f ./pv-hack.yaml

kubectl create cm -n vault-ns setup-script --from-file=vault_setup.sh

kubectl apply -f ./job.yaml
