ARG from=alpine:latest
FROM ${from} as build

#
#  Install build tools
#
RUN apk update
RUN apk add git gcc make

#
#  Create build directory
#
RUN mkdir -p /usr/local/src/repositories
WORKDIR /usr/local/src/repositories

#
#  Shallow clone the FreeRADIUS source
#
ARG source=https://github.com/FreeRADIUS/freeradius-server.git
ARG release=v3.2.x

RUN git clone --depth 1 --single-branch --branch ${release} ${source}
WORKDIR freeradius-server

#
#  Install build dependencies
#
RUN apk add libc-dev talloc-dev
RUN apk add openssl openssl-dev
RUN apk add linux-headers
RUN apk add pcre-dev libidn-dev krb5-dev samba-dev curl-dev json-c-dev
RUN apk add openldap-dev
RUN apk add postgresql-dev

#
#  Build the server
#
RUN ./configure --with-raddbdir=/etc/freeradius/3.0 --enable-reproducible-builds
RUN make -j4
RUN make install

#
#  Clean environment and run the server
#
FROM ${from}
COPY --from=build /usr /usr
COPY --from=build /etc /etc

#
# These are needed for the server to start
#
RUN apk update \
    && apk add talloc libressl pcre libwbclient tzdata \
    && apk add libcurl json-c libldap hiredis sqlite-dev
RUN apk add postgresql-dev

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 1812/udp 1813/udp
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

