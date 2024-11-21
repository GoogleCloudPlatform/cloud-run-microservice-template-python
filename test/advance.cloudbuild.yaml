# Copyright 2021 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

steps:
  - id: "Install Invoke and Pip"
    name: $_PYTHON_VERSION
    entrypoint: python
    args: ["-m", "pip", "install", "invoke", "-U", "pip", "--user"]

  - id: "Setup virtualenv"
    name: $_PYTHON_VERSION
    entrypoint: python
    args: ["-m", "invoke", "setup-virtualenv"]

  - id: "Lint"
    name: $_PYTHON_VERSION
    entrypoint: python
    args: ["-m", "invoke", "lint"]

  - id: "Run Unit Tests"
    name: $_PYTHON_VERSION
    entrypoint: python
    args: ["-m", "invoke", "test"]

  # Setup resources for system tests
  - id: "Build Container Image"
    name: "gcr.io/k8s-skaffold/pack"
    entrypoint: pack
    args:
      - build
      - "$_GCR_HOSTNAME/$PROJECT_ID/$_REPOSITORY/$REPO_NAME/$_SERVICE_NAME:$COMMIT_SHA" # Tag docker image with git commit SHA
      - "--builder=gcr.io/buildpacks/builder:latest"
      - "--path=."

  - id: "Push Container Image"
    name: "gcr.io/cloud-builders/docker:latest"
    entrypoint: /bin/bash
    timeout: 60s
    args:
      - "-c"
      - |
        while ! docker push "$_GCR_HOSTNAME/$PROJECT_ID/$_REPOSITORY/$REPO_NAME/$_SERVICE_NAME:$COMMIT_SHA"; do
          sleep 2
        done

  - id: "Deploy to Cloud Run"
    name: "gcr.io/cloud-builders/gcloud:latest"
    entrypoint: /bin/bash
    args:
      - "-c"
      - |
        gcloud run deploy ${_SERVICE_NAME}-$BUILD_ID \
          --image $_GCR_HOSTNAME/$PROJECT_ID/$_REPOSITORY/$REPO_NAME/$_SERVICE_NAME:$COMMIT_SHA \
          --region ${_DEPLOY_REGION} \
          --no-allow-unauthenticated

  - id: "Retrieve Service URL"
    name: "gcr.io/cloud-builders/gcloud:latest"
    entrypoint: /bin/bash
    args:
      - "-c"
      - |
        source /workspace/test/common.sh
        echo $(get_url ${BUILD_ID}) > _service_url
        echo $(get_idtoken) > _id_token
    env:
      - "_SERVICE_NAME=${_SERVICE_NAME}"
      - "_DEPLOY_REGION=${_DEPLOY_REGION}"
      - "PROJECT_ID=${PROJECT_ID}"

  - id: "Run System Tests"
    name: "${_PYTHON_VERSION}"
    entrypoint: /bin/bash
    args:
      - "-c"
      - |
        export BASE_URL=$(cat _service_url)
        export ID_TOKEN=$(cat _id_token)
        python -m invoke system-test

  # Clean up system test resources

  - id: "Delete image and service"
    name: "gcr.io/cloud-builders/gcloud"
    entrypoint: "/bin/bash"
    args:
      - "-c"
      - |
        gcloud artifacts docker images delete $_GCR_HOSTNAME/$PROJECT_ID/$_REPOSITORY/$REPO_NAME/$_SERVICE_NAME:$COMMIT_SHA --quiet
        gcloud run services delete ${_SERVICE_NAME}-$BUILD_ID \
          --region ${_DEPLOY_REGION} --quiet

options:
  dynamic_substitutions: true
  substitution_option: "ALLOW_LOOSE"

substitutions:
  _GCR_HOSTNAME: us-central1-docker.pkg.dev
  _SERVICE_NAME: microservice-template
  _DEPLOY_REGION: us-central1
  _PYTHON_VERSION: python:3.12-slim # matches .python-version
  _REPOSITORY: samples
