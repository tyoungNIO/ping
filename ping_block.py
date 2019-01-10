import subprocess
import time
from nio import Block, Signal
from nio.block.mixins.enrich.enrich_signals import EnrichSignals
from nio.properties import FloatProperty, StringProperty, \
                           VersionProperty


class Ping(EnrichSignals, Block):

    version = VersionProperty('0.1.0')
    hostname = StringProperty(title='Hostname', default='127.0.0.1')
    timeout = FloatProperty(
        title='Timeout (seconds)',
        default=3.0,
        advanced=True,
    )

    def process_signals(self, signals):
        outgoing_signals = []
        for signal in signals:
            command = 'ping -c 1 -W {} {}'.format(
                self.timeout(signal),
                self.hostname(signal),
            )
            start_time = time.monotonic()
            exit_code = subprocess.call(command, shell=True)
            stop_time = time.monotonic()
            round_trip = None
            if not exit_code:
                round_trip = stop_time - start_time
                round_trip = round(round_trip * 1000, 1)
            signal_dict = {
                'ping_response': not exit_code,
                'ping_time_ms': round_trip,
            }
            new_signal = self.get_output_signal(signal_dict, signal)
            outgoing_signals.append(new_signal)
        self.notify_signals(outgoing_signals)
