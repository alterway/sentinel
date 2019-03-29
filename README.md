# SENTINEL 

An alternative to registrator

This service permit to discover public services in docker cluster and register it in a backend. The public services are the services who expose port in the docker host.

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

  sentinel:
    image: alterway/sentinel:2.0.2
    command: --log-level=DEBUG discovery --target=127.0.0.1:8500 --backend=consul --orchestrator=swarm
    network_mode: host
    restart: always
    environment:
      TERM: "xterm"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

# Complete example to create dynamic reverse proxy with service discovery

```yaml

version: "3"

services:
 consul:
   container_name: consul
   command: -server -bootstrap-expect 1 -domain acme.com -advertise 192.168.0.2 -node=node-1 -dc cluster -recursor 8.8.8.8 -ui-dir /ui -data-dir /data/consul -encrypt ca1S1TX2Q03gPv4d2o1yrg==
   image: consul
   restart: always
   network_mode: host

 nginx:
   container_name: nginx
   image: alterway/nginx:1.10-auth-request
   restart: always
   network_mode: host
   volumes:
     - /etc/nginx/
     - /storage/htaccess:/etc/nginx/htaccess
     - /storage/ssl:/etc/nginx/ssl

 consul-template:
   container_name: consul-template
   command: -consul=127.0.0.1:8500 -wait=5s -template="/etc/ctmpl/nginx.ctmpl:/etc/nginx/nginx.conf:docker kill -s HUP nginx"
   image: alterway/consul-template-nginx:0.12-dockerinside-1.11
   restart: always
   network_mode: host
   volumes_from:
     - nginx
   volumes:
     - /var/run/docker-sec/docker.sock:/var/run/docker.sock
   environment:
     DOMAIN: acme.com
     NGINX_SSL_CERT_PATH: /etc/nginx/ssl/cert.pem
     NGINX_SSL_KEY_PATH: /etc/nginx/ssl/key.pem
     WORKER_PROCESSES: 4
     WORKER_CONNECTIONS: 4096
   depends_on:
     - consul

 sentinel:
   container_name: 'sentinel'
   image: alterway/sentinel:2.0.2
   command: --log-level=DEBUG discovery --target=192.168.0.4:8500 --backend=consul --orchestrator=swarm
   restart: always
   network_mode: host
   volumes:
     - /var/run/docker.sock:/var/run/docker.sock
   depends_on:
     - consul

 keepalived:
   container_name: keepalived
   image: alterway/keepalived:dockerinside-latest
   network_mode: "host"
   restart: always
   cap_add:
     - NET_ADMIN
   environment:
     VIRTUAL_IP: 192.168.0.1
     VIRTUAL_ROUTER_ID: '51'
     INTERFACE:  'ens4'
     PRIORITY:   '99'
     PASSWORD:   'apassword'
     CONTAINERS_TO_CHECK: ''
     CHECK_FALL: '1'
     CHECK_RISE: '1'
     CHECK_CREATION: 'false'
     ENABLE_LB: 'true'
     VIRTUAL_IP_LB: 192.168.0.2
     REAL_IP: 192.168.0.4 192.168.0.5 192.168.0.6
     REAL_PORTS: '2376 80 443'
     LB_ALGO: 'lblcr'
     LB_KIND: 'DR'
   volumes:
    - /var/run/docker-sec/docker.sock:/var/run/docker.sock
   depends_on:
     - consul
```

In this case you should have 3 other nodes with IP addr : 192.168.0.5 192.168.0.6
You can point you dns on 192.168.0.1 IP


**Use sentinel command to launch discovery service :**

```bash
docker run -it --rm -v /tmp/config:/config alterway/sentinel:2.0.2 \
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

```bash
docker run -it --rm -v /tmp/config:/config alterway/sentinel:2.0.2 --log-level=DEBUG create_config --help
```

If you choose deployment-type swarmservices, you have to use command `docker stack deploy`to deploy, use `docker-compose` on each node if you choose compose.

## Register a service by sentinel
If your service expose port on docker host, he will be registered by sentinel in consul except if it is a container with "network_mode: host"

* To choose a specific name for your service, use the label or environment variable :
`service_name`
* To add tags in consul for your service, use the label or environment variable : `service_tags` and seperate tags with comma.
* If your service expose several ports you can define names or tags with add internal port of service in labels or environment variables. For example, you have a service http, you can use `service_80_name` and `service_80_tags`.
* If your service expose several ports you don't want to register in consul, you have to add label or environment variable : `not_register` to your service. You can use `service_PORT_name` and `service_PORT_tags` to register service only for a port.

## Known issues / remarks

- `-node`flag in consul must be equal to machine `hostname`.
   If not, then if you register a container (eg: docker run -d -p 80 -e SERVICE_80_NAME=front -e SERVICE_80_TAGS=http), service name won't be unregister when container will be deleted.

- Sometimes swarm api give node address 0.0.0.0 and the record for this node in consul is always in failed : `ERROR Failed to register service hello for node node3 : b'Invalid service address'`. You need to restart docker service on this node and all services will be synchronize and register.

- It's **very important** to use IP of the hostname in advertise addr. You may bad behavior using localhost or 127.0.0.1

- Container must be deployed by `docker-compose` or `docker run` command, not by `docker stack deploy ...` 


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
- [Herve Leclerc](https://github.com/herveleclerc)

## License

View [LICENSE](LICENSE) for the software contained in this image.