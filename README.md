# SENTINEL [![pipeline status](https://git.alterway.fr/CAAS/sentinel/badges/master/pipeline.svg)](https://git.alterway.fr/CAAS/sentinel/commits/master) [![coverage report](https://git.alterway.fr/CAAS/sentinel/badges/master/coverage.svg)](https://git.alterway.fr/CAAS/sentinel/commits/master)

This service permit to discover public services in docker cluster and register it in a backend. The public services are the services who expose port in the docker host

**Compatibility with orchestrators :**
* swarm

**Compatibility with backends :**
* consul

## Deploy sentinel

Sentinel has to be deployed as a container on all nodes of a docker cluster.
He need to have access to the docker socket of the node and to the consul. You can use sentinel with consul, consul-template and a reverse-proxy to configure dynamically the reverse-proxy by a template given to consul-template and generate by services informations found in consul backend.

**Docker-compose example :**
```yaml
version: "3"

services:
  consul:
    container_name: consul
    image: consul
    command: agent -server -bootstrap-expect 1 -domain vagrant.dev --advertise 192.168.50.4 -node=node1 -datacenter cluster --client=0.0.0.0 -recursor 8.8.8.8 -ui
    restart: always
    network_mode: host
    volumes:
      - consul-data:/consul/data

  sentinel:
    container_name: sentinel
    image: alterway/sentinel
    restart: always
    network_mode: host
    volumes:
    - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
    - consul
```

**Environment variables to configure sentinel :**
* `BACKEND` : (default: consul), to configure the backend to register services, only consul for now.
* `ORCHESTRATOR` : (default: swarm), to configure the cluster docker orchestrator, only swarm for now.
* `CONSUL_ADDRESS`: (default: http://127.0.0.1:8500), the address to get consul catalog. You need to have an consul agent on all nodes because the address agent is the node cluster address to register services.
* `DEBUG`: Add this to have debug logs level.

**Use sentinel command to generate docker-compose files:**
You can use command `create_config` to generate docker-compose files with consul and sentinel services.
The files are writed in directory /config.
To run help command :
```
docker run -it --rm -v /tmp/config:/config alterway/sentinel create_config --help
```
If you choose deployment-type swarmservices, you have to use command `docker stack deploy`to deploy, use `docker-compose` on each node if you choose compose.

## Register a service by sentinel
If your service expose port on docker host, he will be registered by sentinel in consul except if it is a container with "network_mode: host"

* To choose a specific name for your service, use the label or environment variable :
`service_name`
* To add tags in consul for your service, use the label or environment variable : `service_tags` and seperate tags with comma.
* If your service expose several ports you can define names or tags with add internal port of service in labels or environment variables. For example, you have a service http, you can use `service_80_name` and `service_80_tags`.
* If your service expose several ports you don't want to register in consul, you have to add label or environment variable : `not_register` to your service. You can use `service_PORT_name` and `service_PORT_tags` to register service only for a port.

## Known issues
Sometimes swarm api give node address 0.0.0.0 and the record for this node in consul is always in failed : `ERROR Failed to register service hello for node node3 : b'Invalid service address'`. You need to restart docker service on this node and all services will be synchronize and register.

## Contributing
* Pull requests are welcome!
* Use developer stack to start the service as developer on your local machine:
  * You need to have `vagrant > 2.0`
  * You need to have an NFS adapter to mount files on vagrant VM : `sudo apt-get install nfs-common nfs-kernel-server`
  * You need to have `ansible > 2.0`
  * Start stack : `make startstackdev`
  * You must have a [consul ui](http://192.168.50.4:8500/ui)
  * you need to rebuild and up sentinel inside vagrant VM to aply changement in code
  * you have to write unit tests in "tests" directory of project
  * to run tests : `make quality`
