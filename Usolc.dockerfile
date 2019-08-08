####################################################################################################
#                                                                                                  #
# (c) 2018 Quantstamp, Inc. All rights reserved.  This content shall not be used, copied,          #
# modified, redistributed, or otherwise disseminated except to the extent expressly authorized by  #
# Quantstamp for credentialed users. This content and its use are governed by the Quantstamp       #
# Demonstration License Terms at <https://s3.amazonaws.com/qsp-protocol-license/LICENSE.txt>.                                                    #
#                                                                                                  #
####################################################################################################

FROM docker:dind
# for "Docker-in-Docker" support

# the following steps are based on https://hub.docker.com/r/frolvlad/alpine-python3/
RUN apk add --no-cache python3 && \
  python3 -m ensurepip && \
  rm -r /usr/lib/python*/ensurepip && \
  pip3 install --upgrade pip setuptools && \
  if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
  if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
  rm -r /root/.cache

RUN apk add --no-cache libtool

RUN mkdir /usolc
WORKDIR /usolc

COPY . .

# Install pip requirements for usolc
RUN pip3 install -r requirements.txt

# Running the solc download
RUN ./bin/solc_download

ENV PATH="/usolc/bin:${PATH}"

ENTRYPOINT ["/usolc/bin/solc"]
