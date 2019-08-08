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

run: build
	docker run -it \
       -v /var/run/docker.sock:/var/run/docker.sock \
       -v /tmp:/tmp \
	   usolc sh

test: test-ci

test-ci: build
	docker run -t \
       -v /var/run/docker.sock:/var/run/docker.sock \
	   -v $(PWD)/tests/coverage:/app/tests/coverage \
       -v /tmp:/tmp \
	   usolc sh -c "bin/run_tests"

clean:
	find . | egrep "^.*/(__pycache__|.*\.pyc|tests/coverage/htmlcov|tests/coverage/.coverage|app.tar)$$" | xargs rm -rf
	docker rmi --force usolc:latest

build:
	docker build -t usolc -f Usolc.dockerfile .

push:
	docker tag usolc qspprotocol/usolc:latest
	docker push qspprotocol/usolc:latest
