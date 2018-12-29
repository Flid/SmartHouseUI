import pyximport  # isort: skip

pyximport.install()  # isort: skip

from .panels import WeatherWidget, LightControlWidget, SidebarWidget  # noqa
from .controls import ImageButton, TimeLabel  # noqa
