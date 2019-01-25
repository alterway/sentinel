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
version: "2.1"

volumes:
  consul-data:
    driver: local

services:
  consul:
    image: consul
    command: agent -server -bootstrap-expect 1 -advertise 192.168.50.4 -domain alterway.fr -node=node1 -datacenter clusterdatacenter --client=0.0.0.0 -recursor 8.8.8.8 -ui -log-level INFO -encrypt be1StVCQqo2gPVss12zy4e==
    network_mode: host
    restart: always
    ports:
      - 8500
    environment:
      TERM: "xterm"
      SERVICE_8500_NAME: consul
    volumes:
      - consul-data:/consul/data/

  registrator:
    image: alterway/sentinel:'2.0.2
    command: --log-level=DEBUG discovery --target=127.0.0.1:8500 --backend=consul --orchestrator=swarm
    network_mode: host
    restart: always
    environment:
      TERM: "xterm"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

**USe sentinel command to launch discovery service :**
```sh
docker run -it --rm -v /tmp/config:/config alterway/sentinel:'2.0.2 \
    --log-level=DEBUG \
    discovery \
    --target=127.0.0.1:8500 \
    --backend=consul \
    --orchestrator=swarm
```

* `backend` : (default: consul), to configure the backend to register services, only consul for now.
* `orchestrator` : (default: swarm), to configure the cluster docker orchestrator, only swarm for now.
* `target`: (default: http://127.0.0.1:8500), the address to get consul catalog. You need to have an consul agent on all nodes because the address agent is the node cluster address to register services.
* `log-level`: Add this to have debug logs level.

**Use sentinel command to generate docker-compose files:**
You can use command `create_config` to generate docker-compose files with consul and sentinel services.
The files are writed in directory /config.
To run help command :

```sh
docker run -it --rm -v /tmp/config:/config alterway/sentinel:'2.0.2 --log-level=DEBUG create_config --help
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

## Contributors

- [Ophélie Mauger](https://github.com/omauger)
- [Etienne de Longeaux](https://github.com/alhassane)

## License

View [LICENSE](LICENSE) for the software contained in this image.