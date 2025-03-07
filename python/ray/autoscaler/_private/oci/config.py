import logging
import os
import stat
import copy



def boostrap_oci(config):
    # create a copy of the input config to modify
    config = copy.deepcopy(config)
    config["head_node"] = {}

    return config