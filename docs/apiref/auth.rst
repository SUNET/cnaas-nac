Authentication API
==================

The API is used to manage devices, interfaces and other objects used
by CNaaS NAC. All requests in the examples belove are using 'curl'.


Authorization
--------------

Authorization is done using JWT tokens. The token must be included in
the authorization header which is sent together with the request.

CURL example:

::

   curl -k -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJxbGci0iJFUzI1NiJ9.eyJpYXQiOjE2MDgwMzYzMTQsIm5iZiI6MTYwODAzNjMxNCwianRpIjoiZWJlNTg1YjItMjE4ZS00YWNkLWE4ZmMtOTVlYTcwYzllMmE3Iiwic3ViIjoia3Jpc3RvZmVyQHN1bmV0LnNlIiwiZnJlc2giOmzhbHNlLCJ0eXBlIjoiYWNjZXNzIn0.FNZ71ogsssRRCKoS-bcK82wehz7ZAodVtuCTNawyTKvkL_3GGM3rbTXbUlkAJbLTuzXa0R1qhLgH-C80OZy7Ag" "https://nac.example.com:1443/api/v1.0/auth"


In the example above, the header is built using the parameter '-H'
followed by the string "Authorization: Bearer <Token>".


Show clients
------------

A list of all clients can be retreived from the API using the /auth
endpoint:

::

   curl -k -H "Authorization: Bearer <Token>" "https://nac.example.com:1443/api/v1.0/auth"


The command above should result in a list of _all_ clients being sent
back. In the example below we only have one active client:

::

   {
     "status": "success",
     "data": [
       {
	 "username": "de:ad:be:ef:00:aa",
	 "active": true,
	 "vlan": "TEST",
	 "nas_identifier": "ca:fe:ba:be:00:aa",
	 "nas_port_id": "Ethernet1",
	 "nas_ip_address": "172.10.1.2",
	 "calling_station_id": "DE-AD-BE-EF-00-AA",
	 "called_station_id": "CA-FE-BA-BE-00-AA",
	 "comment": "A comment",
	 "reason": "User accepted",
	 "authdate": "2020-12-11 09:47:46.039862"
	}
      ]
    }


We can also display information about a single client by appending its username, like this:

::

   curl -k -H "Authorization: Bearer <Token>" "https://nac.example.com:1443/api/v1.0/auth/de:ad:be:ef:00:aa"


Add client
----------

Clients can be added using the POST method. The following attributes are supported:

+ username, required. Must always be present.
+ password, optional. If not present it will be set to the username.
+ vlan, optional. For example "TEST".
+ comment, optional. Any string.
+ nas_identifier, optional. A MAC address.
+ nas_port_id, optional. Interface, for example Ethernet1.
+ calling_station_id, optional. Typically a MAC address.
+ called_station_id, optional.  Typically a MAC address.

CURL example:

::

   curl -k -H "Authorization: Bearer <Token>" -H "Content-Type: application/json" -d '{"username": "foo", "password": "bar", "vlan": "TEST", "nas_identifier": "nas_1", "nas_port_id": "Ethernet1", "nas_ip_address": "1.2.3.4", "comment": "Test"}' "https://localhost:1443/api/v1.0/auth"


Sort and filter
---------------

Further, it is possible to sort and retreive a subset of clients based
on a match criteria using any or all of the parameters sort and filter.

Sort can be done in ascending or descending order with the parameter
'?sort=username' or '?sort=-username'.

Sort can be applied to the following fields:

+ username
+ vlan
+ reason
+ comment

CURL examples:

Sort by VLAN in ascending order:
::

   curl -k -H "Authorization: Bearer <Token>" "https://nac.example.com:1443/api/v1.0/auth?sort=vlan"

Sort by VLAN in descending order (notice the '-' character):

::

   curl -k -H "Authorization: Bearer <Token>" "https://nac.example.com:1443/api/v1.0/auth?sort=-vlan"


Same thing applies for filter. We can find all clients that contains the string "de:ad" using the parameter filter:

::

   curl -k -H "Authorization: Bearer <Token>" "https://nac.example.com:1443/api/v1.0/auth?filter[username]=de:ad"

The following fields can be filtered:

+ username
+ vlan
+ nasip
+ nasport
+ reason
+ comment


Modify clients
--------------

We can update and remove clients using the PUT and DELETE methods. The fields vlan, comment, enabled and bounce can be set then using the PUT method.

For example, to update the VLAN for a client using CURL, we can do like this:

::

   curl -k -H "Authorization: Bearer <Token>" -H "Content-Type: application/json" -X PUT -d '{"vlan": "TEST2}' "https://nac.example.com:1443/api/v1.0/auth/de:ad:be:ef:aa:00"


To disable a client, wen simply replace the VLAN with enabled:

::

   curl -k -H "Authorization: Bearer <Token>" -H "Content-Type: application/json" -X PUT -d '{"enabled": false}' "https://nac.example.com:1443/api/v1.0/auth/de:ad:be:ef:aa:00"

Bounce will trigger a port flap, which basically is to shut down the
port and make it available again. The bounce command will use the port
and NAS information we have about the client to figure out which port
we should bounce:

::

   curl -k -H "Authorization: Bearer <Token>" -H "Content-Type: application/json" -X PUT -d '{"bounce": true}' "https://nac.example.com:1443/api/v1.0/auth/de:ad:be:ef:aa:00"

Remove clients
--------------

And finally we can remove a client using delete:

::

   curl -k -H "Authorization: Bearer <Token>" -X DELETE  "https://nac.example.com:1443/api/v1.0/auth/de:ad:be:ef:aa:00"
