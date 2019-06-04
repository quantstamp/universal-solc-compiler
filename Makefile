####################################################################################################
#                                                                                                  #
# (c) 2018 Quantstamp, Inc. All rights reserved.  This content shall not be used, copied,          #
# modified, redistributed, or otherwise disseminated except to the extent expressly authorized by  #
# Quantstamp for credentialed users. This content and its use are governed by the Quantstamp       #
# Demonstration License Terms at <https://s3.amazonaws.com/qsp-protocol-license/LICENSE.txt>.                                                    #
#                                                                                                  #
####################################################################################################
docs:
	markdown-pp ./.github/CONTRIBUTE.mdTemplate -o ./CONTRIBUTE.md
	mkdir -p .github/ISSUE_TEMPLATE
	markdown-pp ./.github/bug_report.mdTemplate -o ./.github/ISSUE_TEMPLATE/bug_report.md
	markdown-pp ./.github/pull_request_template.mdTemplate -o ./.github/pull_request_template.md
	curl https://raw.githubusercontent.com/quantstamp/opensource-doc-gen/master/CODE_OF_CONDUCT.md > .github/CODE_OF_CONDUCT.md
	curl https://raw.githubusercontent.com/quantstamp/opensource-doc-gen/master/github_template/feature_request.md > .github/ISSUE_TEMPLATE/feature_request.md

build:
	docker build -t usolc-node .

run: build
	docker run -it \
       -v /var/run/docker.sock:/var/run/docker.sock \
       -v /tmp:/tmp \
	   usolc-node sh

test-ci: 
	docker run -t \
       -v /var/run/docker.sock:/var/run/docker.sock \
	   -v $(PWD)/tests/coverage:/app/tests/coverage \
       -v /tmp:/tmp \
	   usolc-node sh -c "./run_tests"

clean:
	find . | egrep "^.*/(__pycache__|.*\.pyc|tests/coverage/htmlcov|tests/coverage/.coverage|app.tar)$$" | xargs rm -rf
	docker rmi --force usolc-node:latest
	docker rmi --force usolc-mythril-node:latest
	docker rmi --force usolc-securify-node:latest

build-entry:
	docker build -t usolc-node-entry -f Dockerfile_withEntry .

build-mythril:
	docker build -t usolc-mythril-node -f Dockerfile_mythril .

build-securify:
	docker build -t usolc-securify-node -f Dockerfile_securify .

run-mythril: build-mythril
	docker run -it \
        -v /tmp:/tmp \
        usolc-mythril-node sh

run-securify: build-securify
	docker run -it \
        -v /tmp:/tmp \
        usolc-securify-node sh

push-usolc-entry:
	docker tag usolc-node-entry qspprotocol/usolc-entry:experimental
	docker push qspprotocol/usolc-entry:experimental

push-securify:
	docker tag usolc-securify-node qspprotocol/securify-usolc:experimental
	docker push qspprotocol/securify-usolc:experimental

push-mythril:
	docker tag usolc-mythril-node qspprotocol/mythril-usolc:experimental
	docker push qspprotocol/mythril-usolc:experimental

publish-usolc-entry:
	docker tag usolc-node-entry qspprotocol/usolc-entry:develop
	docker tag usolc-node-entry qspprotocol/usolc-entry:latest
	docker push qspprotocol/usolc-entry:develop
	docker push qspprotocol/usolc-entry:latest

publish-securify:
	docker tag usolc-securify-node qspprotocol/securify-usolc:develop
	docker tag usolc-securify-node qspprotocol/securify-usolc:latest
	docker push qspprotocol/securify-usolc:develop
	docker push qspprotocol/securify-usolc:latest

publish-mythril:
	docker tag usolc-mythril-node qspprotocol/mythril-usolc:develop
	docker tag usolc-mythril-node qspprotocol/mythril-usolc:latest
	docker push qspprotocol/mythril-usolc:develop
	docker push qspprotocol/mythril-usolc:latest
