from .config import Config

# Temporary hack to avoid raises
class Resource: pass

from .path_to_resource import path_to_resource
from .db import DB
from .general import *
from .language import *
from .vcf_munger import VcfMunger
from .run_command import run_command

