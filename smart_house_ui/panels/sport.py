import datetime
import random
import io
from PIL import Image

import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange
from numpy import arange
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.metrics import Metrics
from kivy.uix.stencilview import StencilView
import requests
from requests.exceptions import RequestException

YAXIS_WIDTH = 34
XAXIS_MIN_POS = -20


class SportWidget(Widget):
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
        date1 = datetime.datetime(2000, 2, 1)
        date2 = datetime.datetime(2000, 4, 1)
        delta = datetime.timedelta(days=1)
        dates = list(drange(date1, date2, delta))

        fig, ax = plt.subplots()
        points = [None]*5 + [random.randint(85, 90) for x in dates[5:]]

        ax.plot_date(
            dates,
            points,
            '-o',
            alpha=1,
            mfc='white',
            color='w',
            ms=6,
            lw=3,
        )

        '''for x, y in zip(dates, points):
            if not y:
                continue
            ax.annotate(y, xy=(x, y), xytext=(0, 3), ha='center',
                textcoords='offset points', fontsize=7, color='#eeeeee')
                '''

        ax.set_xlim(dates[0] - 1, dates[-1] + 1)
        ax.set_ylim(75, 95)

        ax.xaxis.set_major_locator(DayLocator(arange(0, len(dates), 5)))
        ax.xaxis.set_minor_locator(DayLocator())
        ax.xaxis.set_major_formatter(DateFormatter('%m-%d'))

        ax.fmt_xdata = DateFormatter('%m-%d')
        fig.autofmt_xdate()

        def px_to_inches(x):
            return x / Metrics.dpi

        fig.set_size_inches(px_to_inches(len(dates)*15), px_to_inches(self.ids['weight_graph'].height))
        plt.grid(True, color='w')

        plt.rc('font', size=10)

        ax.spines['top'].set_linewidth(0)
        ax.spines['right'].set_linewidth(0)
        ax.spines['left'].set_color('w')
        ax.spines['bottom'].set_color('w')
        ax.tick_params(colors='w', width=1, which='both')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', transparent=True, bbox_inches='tight')
        buf.seek(0)
        from kivy.core.image import Image as CoreImage
        return CoreImage(buf, ext='png').texture
