export VAULT_ADDR="http://vault.vault-ns.svc.cluster.local:8200"
API_SERVER="https://kubernetes.default.svc"
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
CA_CERT="/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
NAMESPACE="vault-ns"
SECRET_NAME="vault-secrets"
FILE_PATH="/tmp/vault_keys.json"  # Path to the JSON file
POSTGRES_DB=mydb
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
DB_URL=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@db-service:5432/$POSTGRES_DB

apk update;apk add jq curl

# Wait for Vault to return HTTP 200
echo "Waiting for Vault to return HTTP 200..."
max_attempts=60
attempt=1
wait_interval=5

while [ $attempt -le $max_attempts ]; do
    echo "Attempt $attempt/$max_attempts: Checking Vault health..."
    
    # Get HTTP status code using curl
    response=$(curl -s -o /dev/null -w "%{http_code}" "$VAULT_ADDR/v1/sys/health" 2>/dev/null)
    
    if [ "$response" = "501" ]; then
        echo "✅ Vault returned HTTP 501! Proceeding with initialization..."
        break
    else
        echo "⏳ Vault returned status $response, waiting..."
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ Timeout: Vault did not return HTTP 200 within $(($max_attempts * $wait_interval)) seconds"
        echo "Last response code: $response"
        exit 1
    fi
    
    echo "Waiting $wait_interval seconds before next attempt..."
    sleep $wait_interval
    attempt=$((attempt + 1))
done


vault operator init -n 1 -t 1 -format=json > $FILE_PATH

unseal_key=$(jq -r .unseal_keys_b64[0] $FILE_PATH )
root_token=$(jq -r .root_token $FILE_PATH )

FILE_CONTENT=$(cat "${FILE_PATH}")


SECRET_DATA=$(cat <<EOF
{
  "apiVersion": "v1",
  "kind": "Secret",
  "metadata": {
    "name": "${SECRET_NAME}"
  },
  "data": {
    "tokens": "$(echo -n "${FILE_CONTENT}" | base64 | tr -d '[:space:]')"
  }
}
EOF
)

echo $SECRET_DATA
echo $FILE_CONTENT
# Use curl to create the Secret
curl -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  --cacert ${CA_CERT} \
  -d "${SECRET_DATA}" \
  "${API_SERVER}/api/v1/namespaces/${NAMESPACE}/secrets"


ROOT_TOKEN_DATA=$(cat <<EOF
{
  "apiVersion": "v1",
  "kind": "Secret",
  "metadata": {
    "name": "vault-token"
  },
  "data": {
    "token": "$(echo -n "${root_token}" | base64 )"
  }
}
EOF
)
# Secret with root token
curl -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  --cacert ${CA_CERT} \
  -d "${ROOT_TOKEN_DATA}" \
  "${API_SERVER}/api/v1/namespaces/${NAMESPACE}/secrets"

vault operator unseal $unseal_key

vault login $root_token

vault secrets enable -path=secret kv-v2

vault kv put secret/db_details DB_URL=$DB_URL POSTGRES_DB=$POSTGRES_DB POSTGRES_USER=$POSTGRES_USER POSTGRES_PASSWORD=$POSTGRES_PASSWORD

vault operator unseal $unseal_key

