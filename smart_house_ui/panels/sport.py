import datetime
import random
import io
from collections import OrderedDict

import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, DateFormatter, drange, date2num
from numpy import arange
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.metrics import Metrics
from kivy.core.image import Image as CoreImage
import requests
from requests.exceptions import RequestException

from smart_house_ui.db import get_weights, add_weight

YAXIS_WIDTH = 34
XAXIS_MIN_POS = -20

SHOW_LAST_DAYS_COUNT = 30


def px_to_inches(x):
            return x / Metrics.dpi


class SportWidget(Widget):
    last_weight = None

    def __init__(self, *args, **kwargs):
        super(SportWidget, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.update_data, timeout=1)
        Clock.schedule_interval(self.update_data, timeout=10)
        Clock.schedule_once(self.set_graph, timeout=1)

    def set_state_error(self):
        self.ids['total_distance'].text = '--/--'

    def update_data(self, instance):
        try:
            response = requests.get(
                'http://127.0.0.1:10100/sensors/endomondo/read',
                timeout=(0.05, 0.1),
            )
        except RequestException as ex:
            self.set_state_error()
            return

        data = response.json()

        if data['status'] != 'ok':
            self.set_state_error()
            return

        data = data['data']
        self.ids['total_distance'].text = 'Total Distance: %s km' % (
            round(data['total_distance'], 2)
        )

    def set_graph(self, *args):
        texture = self.generate_weight_graph_texture()
        self.ids['weight_graph'].size = texture.size
        self.ids['weight_graph'].parent.size = texture.size

        scatter_layout = self.ids['weight_graph'].parent.parent
        scatter_layout.size = texture.size
        self.pos_changed(scatter_layout, [float('-inf'), scatter_layout.y])

        self.ids['weight_graph'].texture = texture

        self.ids['graph_vertical_axis'].size = texture.size
        self.ids['graph_vertical_axis'].texture = texture

        self.ids['weight_graph'].parent.parent.bind(pos=self.pos_changed)

    def pos_changed(self, instance, pos):
        if pos[0] > XAXIS_MIN_POS:
            instance.x = XAXIS_MIN_POS

        max_pos = -instance.width + self.width + XAXIS_MIN_POS
        if pos[0] < max_pos:
            instance.x = max_pos

    def generate_weight_graph_texture(self):
        start_dt = datetime.datetime.now() - datetime.timedelta(days=SHOW_LAST_DAYS_COUNT)
        measurements = get_weights(start_dt)

        if measurements:
            self.last_weight = measurements[-1].value

        one_day = datetime.timedelta(days=1)
        dates = list(drange(
            start_dt.date() + one_day,
            datetime.date.today() + one_day,
            one_day,
        ))

        graph_points = OrderedDict((d, None) for d in dates)

        for item in measurements:
            graph_points[date2num(item.dt.date())] = item.value

        fig, ax = plt.subplots()

        ax.plot_date(
            dates,
            list(graph_points.values()),
            '-o',
            alpha=1,
            mfc='white',
            color='w',
            ms=6,
            lw=3,
        )

        # Set graph appearance
        ax.set_xlim(dates[0] - 1, dates[-1] + 1)
        ax.set_ylim(75, 95)
        ax.xaxis.set_major_locator(DayLocator(interval=5))
        ax.xaxis.set_major_formatter(DateFormatter('%m-%d'))
        ax.xaxis.set_minor_locator(DayLocator())

        ax.fmt_xdata = DateFormatter('%m-%d')
        fig.autofmt_xdate()

        fig.set_size_inches(
            px_to_inches(len(dates) * 15),
            px_to_inches(self.ids['weight_graph'].height),
        )
        plt.grid(True, color='w')

        plt.rc('font', size=10)

        ax.spines['top'].set_linewidth(0)
        ax.spines['right'].set_linewidth(0)
        ax.spines['left'].set_color('w')
        ax.spines['bottom'].set_color('w')
        ax.tick_params(colors='w', width=1, which='both')

        # Print graph to memory and create kivy texture.
        buf = io.BytesIO()
        plt.savefig(buf, format='png', transparent=True, bbox_inches='tight')
        buf.seek(0)
        return CoreImage(buf, ext='png').texture

    def save_weight_value(self, value):
        add_weight(value)
        self.set_graph()
