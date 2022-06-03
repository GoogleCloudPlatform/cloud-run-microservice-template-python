#!/usr/bin/env bash
# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
    -d "{\"audience\": \"$(cat _service_url)\"}" \
    "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/token-creator@${PROJECT_ID}.iam.gserviceaccount.com:generateIdToken" | \
    python3 -c "import sys, json; print(json.load(sys.stdin)['token'])"
} 
