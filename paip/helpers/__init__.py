from .config import Config
from .generate_command import generate_command
from .run_command import run_command
from .path_to_resource import path_to_resource

# Temporary hack to avoid raises
class Resource: pass

from .db import DB
from .general import *
from .language import *
from .vcf_munger import VcfMunger
from .sample import Sample

