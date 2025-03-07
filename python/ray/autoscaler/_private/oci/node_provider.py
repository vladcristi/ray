import sys
import time
from oci.config import validate_config
from collections import OrderedDict, defaultdict
from typing import Any, Dict, List
import oci.config
import oci
import ray
import copy
from ray.autoscaler._private.oci.utils import create_instance_with_network
from ray.autoscaler._private.oci.config import boostrap_oci
from ray.autoscaler.node_provider import NodeProvider


from ray.autoscaler._private.constants import (
    AUTOSCALER_NODE_START_WAIT_S,
    AUTOSCALER_NODE_TERMINATE_WAIT_S,
    MAX_PARALLEL_SHUTDOWN_WORKERS,
)

from ray.autoscaler.tags import (
    TAG_RAY_CLUSTER_NAME,
    TAG_RAY_LAUNCH_CONFIG,
    TAG_RAY_NODE_KIND,
    TAG_RAY_NODE_NAME,
    TAG_RAY_NODE_STATUS,
    TAG_RAY_USER_NODE_TYPE,
)


# instance status
PROVISIONING = "Provisioning"
RUNNING = "Running"
STARTING = "Starting"
STOPPING = "Stopping"
STOPPED = "Stopped"
TERMINATING = "Terminating"
TERMINATED = "Terminated"


class OCINodeProvider(NodeProvider):

    def __init__(self, provider_config, cluster_name):
        NodeProvider.__init__(self, provider_config, cluster_name)
        self.config = {
            "user": provider_config["user_ocid"],
            "key_file": provider_config["full_path_to_private_key"],
            "fingerprint": provider_config["fingerprint"],
            "tenancy": provider_config["tenancy_ocid"],
            "region": provider_config["oci_region"]
        }

    def non_terminated_nodes(self, tag_filters):
        non_terminated_instances = []
        return non_terminated_instances

    def is_running(self, node_id: str) -> bool:
        return False

    def is_terminated(self, node_id: str) -> bool:
        return False

    def create_node(self, node_config, tags, count):
        filter_tags = [
            {
                "Key": TAG_RAY_CLUSTER_NAME,
                "Value": self.cluster_name,
            },
            {"Key": TAG_RAY_NODE_KIND, "Value": tags[TAG_RAY_NODE_KIND]},
            {"Key": TAG_RAY_USER_NODE_TYPE, "Value": tags[TAG_RAY_USER_NODE_TYPE]},
            {"Key": TAG_RAY_LAUNCH_CONFIG, "Value": tags[TAG_RAY_LAUNCH_CONFIG]},
            {"Key": TAG_RAY_NODE_NAME, "Value": tags[TAG_RAY_NODE_NAME]},
        ]
        core_client = oci.core.ComputeClient(self.config)
        created_nodes_dict = []

        filter_tags.append(
            {"Key": TAG_RAY_NODE_STATUS, "Value": tags[TAG_RAY_NODE_STATUS]}
        )
        while count > 0:
            instance = create_instance_with_network(
                instance_type=node_config["InstanceType"],
                compartment_id=node_config["CompartmentId"],
                cidr_block=node_config["CidrBlock"]
                # tags=filter_tags,
            )
            created_nodes_dict.append(instance)

        return created_nodes_dict
    
    def terminate_nodes(self, node_ids: List[str]) -> None:
        if not node_ids:
            return
        
    @staticmethod
    def bootstrap_config(cluster_config):
        return boostrap_oci(cluster_config)