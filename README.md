[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)

# CNaaS NAC Campus Network-as-a-Service - Network Admission Control

Software to automate management of a campus network(LAN). This is an
open source software developed as part of SUNETs managed service.

CNaaS NAC provides a way for clients to authenticate themselves using
IEEE 802.1X with MAB as a fallback mechanism.

Features:
- Automatic registration of MAB clients.
- Periodic cleanup of inactive clients.
- Replication between primary and secondary server.
- Active Directory integration.
- API which can be used for all sorts of integrations.
- Fancy web UI written in React.

## Components:

![CNaaS component architecture](nac-components-20201209.png?raw=true)
