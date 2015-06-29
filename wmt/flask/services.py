from .users import UsersService
from .names import NamesService
from .tags import TagsService
from .sims import SimsService
from .components import ComponentsService
from .models import ModelsService
from .parameters import ParametersService
from .files import FilesService


users = UsersService()
names = NamesService()
tags = TagsService()
sims = SimsService()
components = ComponentsService()
models = ModelsService()
parameters = ParametersService()
files = FilesService()
