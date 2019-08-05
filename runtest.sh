#!/usr/bin/env bash

TEST_IMAGE_NAME='pypi-tests'

check_python_version() {
    python3 tools/check_python_version.py 3 6
}

gc() {
    IMAGE_NAME=$(@echo $(REGISTRY)/$(REPOSITORY):$(DEFAULT_TAG))
    docker rmi -f "${IMAGE_NAME}"
    docker rmi -f "${TEST_IMAGE_NAME}"
}

check_python_version

if [[ "$CI" -eq "0" ]];
then
    # make docker-build-test
    docker build -t ${TEST_IMAGE_NAME} -f Dockerfile.tests .
    docker run ${TEST_IMAGE_NAME}
    docker stop ${TEST_IMAGE_NAME}
    trap gc EXIT SIGINT
else
    # CI instance will be torn down anyway, don't need to waste time on gc
    docker run ${TEST_IMAGE_NAME}
fi
