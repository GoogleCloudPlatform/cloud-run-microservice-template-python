#!/usr/bin/env bash
##
# common.sh
# Provides utility functions commonly needed across Cloud Build pipelines.
#
# This is expected to be used from cloud-run-template.cloudbuild.yaml and 
# should be "forked" into an individual sample that does not provide the same
# environment variables and workspace.
#
# It is kept separate for two reasons:
# 1. Simplicity of cloudbuild.yaml files.
# 2. Easier evaluation of security implications in changes to get_idtoken().
#
# Usage
# If you do not need to fork this script, directly source it in your YAML file:
#
# ```
# . /testing/cloudbuild-templates/common.sh
# echo $(get_url) > _service_url
# ```
##

# Retrieve Cloud Run service URL -
# Cloud Run URLs are not deterministic.
get_url() {
    bid=$(test "$1" && echo "$1" || cat _short_id)
    gcloud run services describe ${_SERVICE_NAME}-${bid} \
        --format 'value(status.url)' \
        --region ${_DEPLOY_REGION} \
        --platform managed
}

# Retrieve Id token to make an aunthenticated request - 
# Impersonate service account, token-creator@, since
# Cloud Build does not natively mint identity tokens.
get_idtoken() {
    curl -X POST -H "content-type: application/json" \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -d "{\"audience\": \"$(get_url)\"}" \
    "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/token-creator@${PROJECT_ID}.iam.gserviceaccount.com:generateIdToken" | \
    python3 -c "import sys, json; print(json.load(sys.stdin)['token'])"
} 