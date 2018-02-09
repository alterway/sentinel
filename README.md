# SENTINEL

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
    command:
    restart: always
    network_mode: host

  sentinel:
    container_name: sentinel
    image: hub.alterway.fr/sentinel
    restart: always
    network_mode: host
```

**Environment variables to configure sentinel :**
* `BACKEND` : (default: consul), to configure the backend to register services, only consul for now
* `ORCHESTRATOR` : (default: swarm), to configure the cluster docker orchestrator, only swarm for now
* `CONSUL_ADDRESS`: (default: http://127.0.0.1:8500), the address to get consul catalog. You need to have an consul agent on all nodes because the address agent is the node cluster address to register services.   

## Register a service by sentinel
If your service expose port on docker host, he will be registered by sentinel in consul except if it is a container with "network_mode: host"

* To choose a specific name for your service, use the label or environment variable :
`service_name`
* To add tags in consul for your service, use the label or environment variable : `service_tags` and seperate tags with comma.
* If your service expose several ports you can define names or tags with add internal port of service in labels or environment variables. For example, you have a service http, you can use `service_80_name` and `service_80_tags`.
* If your service expose several ports you don't want to register in consul, you have to add label or environment variable : `not_register` to your service. You can use `service_PORT_name` and `service_PORT_tags` to register service only for a port.
