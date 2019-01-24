"""Define Discovery DTO object"""
import re
from ddd_domain_driven_design.application.dto.generalisation.dto import DTO


class DiscoveryCommand(DTO):
    """Discovery DTO object"""

    backend = str, {"immutable": True}
    orchestrator = str, {"immutable": True}
    address = str, {"immutable": True, "coerce": lambda value: re.sub('/^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):[0-9]+$/g', '', value)}
    level = str, {"immutable": True}

