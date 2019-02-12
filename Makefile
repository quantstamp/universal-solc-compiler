####################################################################################################
#                                                                                                  #
# (c) 2018 Quantstamp, Inc. All rights reserved.  This content shall not be used, copied,          #
# modified, redistributed, or otherwise disseminated except to the extent expressly authorized by  #
# Quantstamp for credentialed users. This content and its use are governed by the Quantstamp       #
# Demonstration License Terms at <https://s3.amazonaws.com/qsp-protocol-license/LICENSE.txt>.                                                    #
#                                                                                                  #
####################################################################################################

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

run-mythril: build-mythril
	docker run -it \
        -v /tmp:/tmp \
        usolc-mythril-node sh

push-mythril: 
	docker tag usolc-mythril-node qspprotocol/mythril-usolc-0.5.3:latest
	docker push qspprotocol/mythril-usolc-0.5.3:latest

build-securify:
	docker build -t usolc-securify-node -f Dockerfile_securify .

run-securify: build-securify
	docker run -it \
        -v /tmp:/tmp \
        usolc-securify-node sh

push-securify:
	docker tag usolc-securify-node qspprotocol/securify-usolc-0.5.3:latest
	docker push qspprotocol/securify-usolc-0.5.3:latest

