from exceptions import NotImplemented
from utils.dependencies_injection import inject_param


class ServiceAdapter():

    def get_services(self):
        raise NotImplemented('Method get_services not implemented')

    def get_services_from_id(self):
        raise NotImplemented('Method get_services_from_id not implemented')

    @inject_param('logger')
    def _get_tags(self, labels, envs, internal_port, logger=None):
        tags = []
        keys = ["service_tags", "service_%s_tags" % internal_port]
        envs_dict = {}
        for env in envs:
            envs_dict[env.split('=')[0].lower()] = env.split('=')[1]
        logger.debug("envs : %s" % envs_dict)

        for key in keys:
            if key in labels:
                tags.extend(labels[key].split(','))
            else:
                logger.debug(": key %s not in %s" % (key, labels))

            if key in envs_dict:
                tags.extend(envs_dict[key].split(','))
            else:
                logger.debug(": key %s not in %s" % (key, envs_dict))

        logger.debug("Tags : %s" % list(set(tags)))

        return list(set(tags))

    @inject_param('logger')
    def _get_name_from_label_and_envs(self, labels, envs, internal_port, logger=None):
        keys = ['service_name', 'service_%s_name' % internal_port]
        envs_dict = {}
        for env in envs:
            envs_dict[env.split('=')[0].lower()] = env.split('=')[1]
        logger.debug("envs : %s" % envs_dict)

        for key in keys:
            if key in labels:
                return labels[key]

            if key in envs_dict:
                return envs_dict[key]

        return None
