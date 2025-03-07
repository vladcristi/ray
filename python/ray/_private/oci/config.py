import logging
import os
import stat

from ray.autoscaler._private_oci.utils import OCIClient


def boostrap_oci(config):
    
    # create vpc
    _get_or_create_vpc(config)

    # create 
