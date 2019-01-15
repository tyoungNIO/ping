import subprocess
import time
from nio import Block
from nio.block.mixins.enrich.enrich_signals import EnrichSignals
from nio.properties import FloatProperty, StringProperty, \
                           VersionProperty


class Ping(EnrichSignals, Block):

    version = VersionProperty('0.1.0')
    hostname = StringProperty(title='Hostname', default='127.0.0.1')
    timeout = FloatProperty(
        title='Timeout (seconds)',
        default=0.0,
        advanced=True,
    )

    def process_signals(self, signals):
        outgoing_signals = []
        for signal in signals:
            timeout = self.timeout(signal)
            if timeout > 0:
                timeout_str = "-W {} ".format(timeout)
            else:
                timeout_str = ""
            command = 'ping -c 1 {timeout_str}{host}'.format(
                timeout_str=timeout_str,
                host=self.hostname(signal),
            )
            start_time = time.monotonic()
            exit_code = subprocess.call(
                command, shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
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
