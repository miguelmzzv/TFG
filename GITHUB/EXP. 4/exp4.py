import os
import sys
import time
import subprocess

TRAFFIC_SCALE = 0.127
TRAFFIC_DURATION = 30
SERVER_START_DELAY = 0.2
TRACEROUTE_MAX_HOPS = 20
TRACEROUTE_TIMEOUT = 1
LINK_CAPACITY_MBPS = 100
TARGET_UTILIZATION_PERCENT = 110.0
MEASUREMENT_INTERVAL = 15
SAMPLE_INTERVAL = 1

ROUTERS = [
    "STTLng", "SNVAng", "LOSAng", "DNVRng", "KSCYng", "HSTNng",
    "IPLSng", "ATLAng", "CHINng", "WASHng", "NYCMng", "ATLAM5"
]


BACKBONE_LINKS = [
    {"a": ("STTLng", "eth0"), "b": ("SNVAng", "eth0")},
    {"a": ("STTLng", "eth1"), "b": ("DNVRng", "eth0")},
    {"a": ("SNVAng", "eth2"), "b": ("LOSAng", "eth0")},
    {"a": ("SNVAng", "eth1"), "b": ("DNVRng", "eth2")},
    {"a": ("LOSAng", "eth1"), "b": ("HSTNng", "eth0")},
    {"a": ("DNVRng", "eth1"), "b": ("KSCYng", "eth0")},
    {"a": ("KSCYng", "eth1"), "b": ("HSTNng", "eth1")},
    {"a": ("KSCYng", "eth3"), "b": ("IPLSng", "eth0")},
    {"a": ("HSTNng", "eth3"), "b": ("ATLAng", "eth2")},
    {"a": ("IPLSng", "eth1"), "b": ("CHINng", "eth0")},
    {"a": ("IPLSng", "eth2"), "b": ("ATLAng", "eth0")},
    {"a": ("ATLAng", "eth1"), "b": ("WASHng", "eth1")},
    {"a": ("ATLAng", "eth4"), "b": ("ATLAM5", "eth0")},
    {"a": ("CHINng", "eth1"), "b": ("NYCMng", "eth1")},
    {"a": ("WASHng", "eth0"), "b": ("NYCMng", "eth0")},
]

NODES = {
    "n1": {"ip": "10.0.0.20", "listen_ports": [5201, 5202, 5203, 5204, 5205, 5206, 5207, 5208, 5209, 5210, 5212]},
    "n2": {"ip": "10.0.3.20", "listen_ports": [5201, 5202, 5203, 5204, 5205, 5206, 5207, 5208, 5209, 5211, 5212]},
    "n3": {"ip": "10.0.8.20", "listen_ports": [5201, 5202, 5203, 5204, 5205, 5206, 5207, 5209, 5210, 5211, 5212]},
    "n4": {"ip": "10.0.13.20", "listen_ports": [5201, 5202, 5203, 5204, 5206, 5207, 5208, 5209, 5210, 5211, 5212]},
    "n5": {"ip": "10.0.18.20", "listen_ports": [5201, 5203, 5204, 5205, 5206, 5207, 5208, 5209, 5210, 5211, 5212]},
    "n6": {"ip": "10.0.26.20", "listen_ports": [5202, 5203, 5204, 5205, 5206, 5207, 5208, 5209, 5210, 5211, 5212]},
    "n7": {"ip": "10.0.24.20", "listen_ports": [5201, 5202, 5203, 5204, 5205, 5206, 5207, 5208, 5209, 5210, 5211]},
    "n8": {"ip": "10.0.22.20", "listen_ports": [5201, 5202, 5203, 5204, 5205, 5206, 5207, 5208, 5210, 5211, 5212]},
    "n9": {"ip": "10.0.20.20", "listen_ports": [5201, 5202, 5204, 5205, 5206, 5207, 5208, 5209, 5210, 5211, 5212]},
    "n10": {"ip": "10.0.16.20", "listen_ports": [5201, 5202, 5203, 5204, 5205, 5207, 5208, 5209, 5210, 5211, 5212]},
    "n11": {"ip": "10.0.10.20", "listen_ports": [5201, 5202, 5203, 5204, 5205, 5206, 5208, 5209, 5210, 5211, 5212]},
    "n12": {"ip": "10.0.6.20", "listen_ports": [5201, 5202, 5203, 5205, 5206, 5207, 5208, 5209, 5210, 5211, 5212]},
}


FLOWS = [
    {"src": "n1", "dst": "n6", "port": 5211, "rate": "0.111019M", "duration": 5},
    {"src": "n1", "dst": "n5", "port": 5211, "rate": "15.881547M", "duration": 5},
    {"src": "n1", "dst": "n9", "port": 5211, "rate": "22.512587M", "duration": 5},
    {"src": "n1", "dst": "n12", "port": 5211, "rate": "4.341176M", "duration": 5},
    {"src": "n1", "dst": "n4", "port": 5211, "rate": "11.302768M", "duration": 5},
    {"src": "n1", "dst": "n10", "port": 5211, "rate": "7.691184M", "duration": 5},
    {"src": "n1", "dst": "n11", "port": 5211, "rate": "2.260848M", "duration": 5},
    {"src": "n1", "dst": "n3", "port": 5211, "rate": "17.766373M", "duration": 5},
    {"src": "n1", "dst": "n8", "port": 5211, "rate": "24.845373M", "duration": 5},
    {"src": "n1", "dst": "n2", "port": 5211, "rate": "4.755005M", "duration": 5},
    {"src": "n1", "dst": "n7", "port": 5211, "rate": "10.517379M", "duration": 5},

    {"src": "n2", "dst": "n6", "port": 5210, "rate": "0.026667M", "duration": 5},
    {"src": "n2", "dst": "n5", "port": 5210, "rate": "1.041205M", "duration": 5},
    {"src": "n2", "dst": "n9", "port": 5210, "rate": "5.046067M", "duration": 5},
    {"src": "n2", "dst": "n12", "port": 5210, "rate": "10.406912M", "duration": 5},
    {"src": "n2", "dst": "n4", "port": 5210, "rate": "1.436683M", "duration": 5},
    {"src": "n2", "dst": "n10", "port": 5210, "rate": "3.861611M", "duration": 5},
    {"src": "n2", "dst": "n11", "port": 5210, "rate": "2.097072M", "duration": 5},
    {"src": "n2", "dst": "n3", "port": 5210, "rate": "2.000211M", "duration": 5},
    {"src": "n2", "dst": "n8", "port": 5210, "rate": "2.211461M", "duration": 5},
    {"src": "n2", "dst": "n1", "port": 5210, "rate": "3.297648M", "duration": 5},
    {"src": "n2", "dst": "n7", "port": 5210, "rate": "1.987707M", "duration": 5},

    {"src": "n3", "dst": "n6", "port": 5208, "rate": "0.339661M", "duration": 5},
    {"src": "n3", "dst": "n5", "port": 5208, "rate": "19.394589M", "duration": 5},
    {"src": "n3", "dst": "n9", "port": 5208, "rate": "89.723683M", "duration": 5},
    {"src": "n3", "dst": "n12", "port": 5208, "rate": "9.039381M", "duration": 5},
    {"src": "n3", "dst": "n4", "port": 5208, "rate": "9.030867M", "duration": 5},
    {"src": "n3", "dst": "n10", "port": 5208, "rate": "42.720251M", "duration": 5},
    {"src": "n3", "dst": "n11", "port": 5208, "rate": "13.570251M", "duration": 5},
    {"src": "n3", "dst": "n8", "port": 5208, "rate": "61.164419M", "duration": 5},
    {"src": "n3", "dst": "n2", "port": 5208, "rate": "2.311541M", "duration": 5},
    {"src": "n3", "dst": "n1", "port": 5208, "rate": "25.519453M", "duration": 5},
    {"src": "n3", "dst": "n7", "port": 5208, "rate": "55.726387M", "duration": 5},

    {"src": "n4", "dst": "n6", "port": 5205, "rate": "0.239043M", "duration": 5},
    {"src": "n4", "dst": "n5", "port": 5205, "rate": "2.956779M", "duration": 5},
    {"src": "n4", "dst": "n9", "port": 5205, "rate": "16.891501M", "duration": 5},
    {"src": "n4", "dst": "n12", "port": 5205, "rate": "3.693019M", "duration": 5},
    {"src": "n4", "dst": "n10", "port": 5205, "rate": "9.143904M", "duration": 5},
    {"src": "n4", "dst": "n11", "port": 5205, "rate": "7.130168M", "duration": 5},
    {"src": "n4", "dst": "n3", "port": 5205, "rate": "98.457928M", "duration": 5},
    {"src": "n4", "dst": "n8", "port": 5205, "rate": "7.265264M", "duration": 5},
    {"src": "n4", "dst": "n2", "port": 5205, "rate": "2.947376M", "duration": 5},
    {"src": "n4", "dst": "n1", "port": 5205, "rate": "2.237597M", "duration": 5},
    {"src": "n4", "dst": "n7", "port": 5205, "rate": "8.506651M", "duration": 5},

    {"src": "n5", "dst": "n6", "port": 5202, "rate": "0.445149M", "duration": 5},
    {"src": "n5", "dst": "n9", "port": 5202, "rate": "16.283117M", "duration": 5},
    {"src": "n5", "dst": "n12", "port": 5202, "rate": "5.169035M", "duration": 5},
    {"src": "n5", "dst": "n4", "port": 5202, "rate": "3.931403M", "duration": 5},
    {"src": "n5", "dst": "n10", "port": 5202, "rate": "27.351896M", "duration": 5},
    {"src": "n5", "dst": "n11", "port": 5202, "rate": "4.844035M", "duration": 5},
    {"src": "n5", "dst": "n3", "port": 5202, "rate": "18.231909M", "duration": 5},
    {"src": "n5", "dst": "n8", "port": 5202, "rate": "12.803955M", "duration": 5},
    {"src": "n5", "dst": "n2", "port": 5202, "rate": "1.421888M", "duration": 5},
    {"src": "n5", "dst": "n1", "port": 5202, "rate": "8.957483M", "duration": 5},
    {"src": "n5", "dst": "n7", "port": 5202, "rate": "51.748245M", "duration": 5},

    {"src": "n6", "dst": "n5", "port": 5201, "rate": "0.522208M", "duration": 5},
    {"src": "n6", "dst": "n9", "port": 5201, "rate": "1.641339M", "duration": 5},
    {"src": "n6", "dst": "n12", "port": 5201, "rate": "0.335728M", "duration": 5},
    {"src": "n6", "dst": "n4", "port": 5201, "rate": "0.413032M", "duration": 5},
    {"src": "n6", "dst": "n10", "port": 5201, "rate": "0.489875M", "duration": 5},
    {"src": "n6", "dst": "n11", "port": 5201, "rate": "0.365077M", "duration": 5},
    {"src": "n6", "dst": "n3", "port": 5201, "rate": "0.817869M", "duration": 5},
    {"src": "n6", "dst": "n8", "port": 5201, "rate": "0.452061M", "duration": 5},
    {"src": "n6", "dst": "n2", "port": 5201, "rate": "0.747405M", "duration": 5},
    {"src": "n6", "dst": "n1", "port": 5201, "rate": "0.388317M", "duration": 5},
    {"src": "n6", "dst": "n7", "port": 5201, "rate": "3.141640M", "duration": 5},

    {"src": "n7", "dst": "n6", "port": 5212, "rate": "11.219101M", "duration": 5},
    {"src": "n7", "dst": "n5", "port": 5212, "rate": "125.937728M", "duration": 5},
    {"src": "n7", "dst": "n9", "port": 5212, "rate": "66.541197M", "duration": 5},
    {"src": "n7", "dst": "n12", "port": 5212, "rate": "36.063421M", "duration": 5},
    {"src": "n7", "dst": "n4", "port": 5212, "rate": "15.439312M", "duration": 5},
    {"src": "n7", "dst": "n10", "port": 5212, "rate": "62.781813M", "duration": 5},
    {"src": "n7", "dst": "n11", "port": 5212, "rate": "32.642733M", "duration": 5},
    {"src": "n7", "dst": "n3", "port": 5212, "rate": "91.675627M", "duration": 5},
    {"src": "n7", "dst": "n8", "port": 5212, "rate": "133.661405M", "duration": 5},
    {"src": "n7", "dst": "n2", "port": 5212, "rate": "1.980576M", "duration": 5},
    {"src": "n7", "dst": "n1", "port": 5212, "rate": "29.760203M", "duration": 5},

    {"src": "n8", "dst": "n6", "port": 5209, "rate": "3.897640M", "duration": 5},
    {"src": "n8", "dst": "n5", "port": 5209, "rate": "40.887840M", "duration": 5},
    {"src": "n8", "dst": "n9", "port": 5209, "rate": "53.674288M", "duration": 5},
    {"src": "n8", "dst": "n12", "port": 5209, "rate": "16.345053M", "duration": 5},
    {"src": "n8", "dst": "n4", "port": 5209, "rate": "23.987787M", "duration": 5},
    {"src": "n8", "dst": "n10", "port": 5209, "rate": "83.325448M", "duration": 5},
    {"src": "n8", "dst": "n11", "port": 5209, "rate": "24.767283M", "duration": 5},
    {"src": "n8", "dst": "n3", "port": 5209, "rate": "71.022560M", "duration": 5},
    {"src": "n8", "dst": "n2", "port": 5209, "rate": "9.591352M", "duration": 5},
    {"src": "n8", "dst": "n1", "port": 5209, "rate": "21.934557M", "duration": 5},
    {"src": "n8", "dst": "n7", "port": 5209, "rate": "111.860741M", "duration": 5},

    {"src": "n9", "dst": "n6", "port": 5203, "rate": "3.793693M", "duration": 5},
    {"src": "n9", "dst": "n5", "port": 5203, "rate": "12.735325M", "duration": 5},
    {"src": "n9", "dst": "n12", "port": 5203, "rate": "13.738253M", "duration": 5},
    {"src": "n9", "dst": "n4", "port": 5203, "rate": "9.830336M", "duration": 5},
    {"src": "n9", "dst": "n10", "port": 5203, "rate": "26.359776M", "duration": 5},
    {"src": "n9", "dst": "n11", "port": 5203, "rate": "6.537749M", "duration": 5},
    {"src": "n9", "dst": "n3", "port": 5203, "rate": "27.775901M", "duration": 5},
    {"src": "n9", "dst": "n8", "port": 5203, "rate": "14.098339M", "duration": 5},
    {"src": "n9", "dst": "n2", "port": 5203, "rate": "1.816941M", "duration": 5},
    {"src": "n9", "dst": "n1", "port": 5203, "rate": "4.495256M", "duration": 5},
    {"src": "n9", "dst": "n7", "port": 5203, "rate": "10.647053M", "duration": 5},

    {"src": "n10", "dst": "n6", "port": 5206, "rate": "4.766925M", "duration": 5},
    {"src": "n10", "dst": "n5", "port": 5206, "rate": "9.254733M", "duration": 5},
    {"src": "n10", "dst": "n9", "port": 5206, "rate": "122.044576M", "duration": 5},
    {"src": "n10", "dst": "n12", "port": 5206, "rate": "21.378197M", "duration": 5},
    {"src": "n10", "dst": "n4", "port": 5206, "rate": "33.173784M", "duration": 5},
    {"src": "n10", "dst": "n11", "port": 5206, "rate": "9.890840M", "duration": 5},
    {"src": "n10", "dst": "n3", "port": 5206, "rate": "24.405043M", "duration": 5},
    {"src": "n10", "dst": "n8", "port": 5206, "rate": "40.616099M", "duration": 5},
    {"src": "n10", "dst": "n2", "port": 5206, "rate": "3.466387M", "duration": 5},
    {"src": "n10", "dst": "n1", "port": 5206, "rate": "13.892187M", "duration": 5},
    {"src": "n10", "dst": "n7", "port": 5206, "rate": "41.138093M", "duration": 5}, 

    {"src": "n11", "dst": "n6", "port": 5207, "rate": "0.420960M", "duration": 5},
    {"src": "n11", "dst": "n5", "port": 5207, "rate": "4.443563M", "duration": 5},
    {"src": "n11", "dst": "n9", "port": 5207, "rate": "26.972272M", "duration": 5},
    {"src": "n11", "dst": "n12", "port": 5207, "rate": "5.394304M", "duration": 5},
    {"src": "n11", "dst": "n4", "port": 5207, "rate": "5.476104M", "duration": 5},
    {"src": "n11", "dst": "n10", "port": 5207, "rate": "8.017757M", "duration": 5},
    {"src": "n11", "dst": "n3", "port": 5207, "rate": "8.673584M", "duration": 5},
    {"src": "n11", "dst": "n8", "port": 5207, "rate": "12.842411M", "duration": 5},
    {"src": "n11", "dst": "n2", "port": 5207, "rate": "1.223752M", "duration": 5},
    {"src": "n11", "dst": "n1", "port": 5207, "rate": "2.444272M", "duration": 5},
    {"src": "n11", "dst": "n7", "port": 5207, "rate": "12.048437M", "duration": 5},

    {"src": "n12", "dst": "n6", "port": 5204, "rate": "0.230805M", "duration": 5},
    {"src": "n12", "dst": "n5", "port": 5204, "rate": "2.341483M", "duration": 5},
    {"src": "n12", "dst": "n9", "port": 5204, "rate": "38.518189M", "duration": 5},
    {"src": "n12", "dst": "n4", "port": 5204, "rate": "8.408763M", "duration": 5},
    {"src": "n12", "dst": "n10", "port": 5204, "rate": "7.207741M", "duration": 5},
    {"src": "n12", "dst": "n11", "port": 5204, "rate": "3.948899M", "duration": 5},
    {"src": "n12", "dst": "n3", "port": 5204, "rate": "21.375568M", "duration": 5},
    {"src": "n12", "dst": "n8", "port": 5204, "rate": "5.723408M", "duration": 5},
    {"src": "n12", "dst": "n2", "port": 5204, "rate": "14.385464M", "duration": 5},
    {"src": "n12", "dst": "n1", "port": 5204, "rate": "10.609464M", "duration": 5},
    {"src": "n12", "dst": "n7", "port": 5204, "rate": "12.248861M", "duration": 5},
    
]


class Tee:
    """
    Env\u00eda simult\u00e1neamente la salida a la terminal y a un fichero.
    """

    def __init__(self, terminal, file):
        self.terminal = terminal
        self.file = file

    def write(self, message):
        self.terminal.write(message)
        self.file.write(message)

        self.terminal.flush()
        self.file.flush()

    def flush(self):
        self.terminal.flush()
        self.file.flush()



def parse_rate_to_mbps(rate):
    """
    Convierte una tasa de iperf3 a Mbps.

    Soporta valores terminados en K, M o G.
    Si no hay sufijo, se interpreta como Mbps.
    """
    rate_text = str(rate).strip().upper()

    if rate_text.endswith("K"):
        return float(rate_text[:-1]) / 1000

    if rate_text.endswith("M"):
        return float(rate_text[:-1])

    if rate_text.endswith("G"):
        return float(rate_text[:-1]) * 1000

    return float(rate_text)


def calculate_total_transmitted_traffic_mbps(flows, traffic_scale):
    """
    Calcula la carga total transmitida por la matriz de tráfico.

    Es la suma de las tasas ejecutadas de todos los flujos,
    es decir, tasa_original * TRAFFIC_SCALE.
    """
    total_mbps = 0.0

    for flow in flows:
        original_rate_mbps = parse_rate_to_mbps(flow["rate"])
        total_mbps += original_rate_mbps * traffic_scale

    return total_mbps



def read_interface_counters(session_path, routers):
    """Lee RX/TX bytes de todas las interfaces de los routers."""
    counters = {}

    for router in routers:
        full_cmd = [
            "vcmd",
            "-c", f"{session_path}/{router}",
            "--",
            "cat", "/proc/net/dev"
        ]

        result = subprocess.run(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"No se pudieron leer contadores de {router}: "
                f"{result.stderr.strip()}"
            )

        counters[router] = {}

        for line in result.stdout.splitlines():
            if ":" not in line:
                continue

            iface, values = line.split(":", 1)
            iface = iface.strip()

            if iface == "lo":
                continue

            fields = values.split()
            if len(fields) < 16:
                continue

            counters[router][iface] = {
                "rx_bytes": int(fields[0]),
                "tx_bytes": int(fields[8])
            }

    return counters


def calculate_link_loads(before, after, interval_seconds):
    """Calcula una muestra de carga direccional por enlace troncal en Mbps."""
    loads = []

    for link in BACKBONE_LINKS:
        router_a, iface_a = link["a"]
        router_b, iface_b = link["b"]

        try:
            a_before = before[router_a][iface_a]
            a_after = after[router_a][iface_a]
            b_before = before[router_b][iface_b]
            b_after = after[router_b][iface_b]
        except KeyError as error:
            raise RuntimeError(
                f"No se encontr\u00f3 la interfaz {error} al calcular "
                f"el enlace {router_a}-{router_b}"
            ) from error

        # A -> B: TX del extremo A y RX del extremo B.
        a_to_b_tx = max(0, a_after["tx_bytes"] - a_before["tx_bytes"])
        a_to_b_rx = max(0, b_after["rx_bytes"] - b_before["rx_bytes"])
        a_to_b_mbps = (
            ((a_to_b_tx + a_to_b_rx) / 2)
            * 8 / interval_seconds / 1_000_000
        )

        # B -> A: TX del extremo B y RX del extremo A.
        b_to_a_tx = max(0, b_after["tx_bytes"] - b_before["tx_bytes"])
        b_to_a_rx = max(0, a_after["rx_bytes"] - a_before["rx_bytes"])
        b_to_a_mbps = (
            ((b_to_a_tx + b_to_a_rx) / 2)
            * 8 / interval_seconds / 1_000_000
        )

        total_load_mbps = a_to_b_mbps + b_to_a_mbps

        loads.append({
            "router_a": router_a,
            "iface_a": iface_a,
            "router_b": router_b,
            "iface_b": iface_b,
            "a_to_b_mbps": a_to_b_mbps,
            "b_to_a_mbps": b_to_a_mbps,
            "total_load_mbps": total_load_mbps
        })

    return loads


def collect_link_load_samples(session_path, duration_seconds):
    """
    Mide la carga por enlace cada SAMPLE_INTERVAL segundos.

    Devuelve todas las muestras y el tiempo real total de medida.
    """
    samples = []
    previous_counters = read_interface_counters(session_path, ROUTERS)
    measurement_start = time.monotonic()
    previous_time = measurement_start

    while True:
        elapsed = time.monotonic() - measurement_start
        remaining = duration_seconds - elapsed

        if remaining <= 0:
            break

        time.sleep(min(SAMPLE_INTERVAL, remaining))

        current_time = time.monotonic()
        current_counters = read_interface_counters(session_path, ROUTERS)
        interval = current_time - previous_time

        sample_loads = calculate_link_loads(
            previous_counters,
            current_counters,
            interval
        )

        samples.append({
            "start_second": previous_time - measurement_start,
            "end_second": current_time - measurement_start,
            "interval": interval,
            "loads": sample_loads
        })

        previous_counters = current_counters
        previous_time = current_time

    actual_duration = time.monotonic() - measurement_start
    return samples, actual_duration


def summarize_link_load_samples(samples):
    """Calcula carga media y pico total para cada enlace."""
    summary = {}

    for sample in samples:
        interval = sample["interval"]

        for load in sample["loads"]:
            key = (
                load["router_a"],
                load["iface_a"],
                load["router_b"],
                load["iface_b"]
            )

            if key not in summary:
                summary[key] = {
                    "router_a": load["router_a"],
                    "iface_a": load["iface_a"],
                    "router_b": load["router_b"],
                    "iface_b": load["iface_b"],
                    "weighted_a_to_b": 0.0,
                    "weighted_b_to_a": 0.0,
                    "weighted_total": 0.0,
                    "total_time": 0.0,
                    "peak_total_mbps": 0.0,
                    "peak_a_to_b_mbps": 0.0,
                    "peak_b_to_a_mbps": 0.0,
                    "peak_start_second": 0.0,
                    "peak_end_second": 0.0
                }

            item = summary[key]
            item["weighted_a_to_b"] += load["a_to_b_mbps"] * interval
            item["weighted_b_to_a"] += load["b_to_a_mbps"] * interval
            item["weighted_total"] += load["total_load_mbps"] * interval
            item["total_time"] += interval

            if load["total_load_mbps"] > item["peak_total_mbps"]:
                item["peak_total_mbps"] = load["total_load_mbps"]
                item["peak_a_to_b_mbps"] = load["a_to_b_mbps"]
                item["peak_b_to_a_mbps"] = load["b_to_a_mbps"]
                item["peak_start_second"] = sample["start_second"]
                item["peak_end_second"] = sample["end_second"]

    results = []

    for item in summary.values():
        total_time = item["total_time"]

        results.append({
            "router_a": item["router_a"],
            "iface_a": item["iface_a"],
            "router_b": item["router_b"],
            "iface_b": item["iface_b"],
            "avg_a_to_b_mbps": item["weighted_a_to_b"] / total_time,
            "avg_b_to_a_mbps": item["weighted_b_to_a"] / total_time,
            "avg_total_mbps": item["weighted_total"] / total_time,
            "peak_total_mbps": item["peak_total_mbps"],
            "peak_a_to_b_mbps": item["peak_a_to_b_mbps"],
            "peak_b_to_a_mbps": item["peak_b_to_a_mbps"],
            "peak_start_second": item["peak_start_second"],
            "peak_end_second": item["peak_end_second"]
        })

    return results


def print_link_load_report(summary, actual_interval, total_transmitted_mbps):
    """Muestra la carga media y el pico observado de cada enlace troncal."""
    ordered = sorted(
        summary,
        key=lambda item: item["avg_total_mbps"],
        reverse=True
    )

    print()
    print("==========================================")
    print("CARGA MEDIDA EN LOS ENLACES TRONCALES")
    print("==========================================")
    print(f"Carga total transmitida: {total_transmitted_mbps:.3f} Mbps")
    print(f"Intervalo real medido: {actual_interval:.3f} segundos")
    print(f"Muestreo aproximado: cada {SAMPLE_INTERVAL} segundo(s)")
    print(f"Capacidad de referencia del enlace: {LINK_CAPACITY_MBPS} Mbps")
    print(
        "La carga total es la suma del tr\u00e1fico en ambos sentidos "
        "durante cada muestra."
    )
    print()

    for item in ordered:
        avg_util = item["avg_total_mbps"] / LINK_CAPACITY_MBPS * 100
        peak_util = item["peak_total_mbps"] / LINK_CAPACITY_MBPS * 100

        print(
            f"{item['router_a']}:{item['iface_a']} <-> "
            f"{item['router_b']}:{item['iface_b']}"
        )
        print(
            f"  Media {item['router_a']} -> {item['router_b']}: "
            f"{item['avg_a_to_b_mbps']:.3f} Mbps"
        )
        print(
            f"  Media {item['router_b']} -> {item['router_a']}: "
            f"{item['avg_b_to_a_mbps']:.3f} Mbps"
        )
        print(
            f"  Carga total media: {item['avg_total_mbps']:.3f} Mbps "
            f"| {avg_util:.2f}%"
        )
        print(
            f"  Pico total observado: {item['peak_total_mbps']:.3f} Mbps "
            f"| {peak_util:.2f}%"
        )
        print(
            f"  Ventana del pico: "
            f"{item['peak_start_second']:.2f}-"
            f"{item['peak_end_second']:.2f} s"
        )
        print()

    if ordered:
        busiest = ordered[0]
        max_load = busiest["avg_total_mbps"]
        max_util = max_load / LINK_CAPACITY_MBPS * 100
        suggested_scale = (
            TRAFFIC_SCALE * TARGET_UTILIZATION_PERCENT / max_util
            if max_util > 0
            else TRAFFIC_SCALE
        )

        print("------------------------------------------")
        print(
            "Enlace con mayor carga total media: "
            f"{busiest['router_a']} - {busiest['router_b']}"
        )
        print(f"Carga total media m\u00e1xima: {max_load:.3f} Mbps")
        print(f"Utilizaci\u00f3n media m\u00e1xima observada: {max_util:.2f}%")
        print(
            f"Factor sugerido para aproximarse al "
            f"{TARGET_UTILIZATION_PERCENT:.0f}% de carga ofrecida: "
            f"{suggested_scale:.6f}"
        )
        print("------------------------------------------")


def start_servers(session_path, nodes):
    for node, cfg in nodes.items():
        ports = cfg.get("listen_ports", [])

        if not ports:
            print(f"{node}: no tiene puertos para escuchar")
            continue

        for port in ports:
            print(f"Arrancando servidor en {node} puerto {port}")

            cmd = (
                f"nohup iperf3 -s -p {port} "
                f"> /tmp/iperf3_server_{node}_{port}.log 2>&1 &"
            )

            full_cmd = [
                "vcmd",
                "-c", f"{session_path}/{node}",
                "--",
                "bash", "-lc", cmd
            ]

            result = subprocess.run(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                print(f"Error arrancando {node}:{port}")

                if result.stdout:
                    print(result.stdout, end="")

                if result.stderr:
                    print(result.stderr, end="")

            time.sleep(SERVER_START_DELAY)


def run_clients(session_path, nodes, flows):
    procs = []

    print()
    print("==========================================")
    print("LANZAMIENTO DEL TR\u00c1FICO BASE")
    print("==========================================")
    print(f"Factor de escala: {TRAFFIC_SCALE}")
    print(f"Duraci\u00f3n de los flujos: {TRAFFIC_DURATION} segundos")
    print(f"N\u00famero de flujos: {len(flows)}")
    print()

    print(
        "La medici\u00f3n de enlaces comenzar\u00e1 inmediatamente "
        "despu\u00e9s de lanzar todos los flujos."
    )

    for flow_id, flow in enumerate(flows, start=1):
        src = flow["src"]
        dst = flow["dst"]
        dst_ip = nodes[dst]["ip"]
        port = flow["port"]

        original_rate_mbps = float(
            flow["rate"].replace("M", "")
        )

        scaled_rate_mbps = (
            original_rate_mbps * TRAFFIC_SCALE
        )

        rate = f"{scaled_rate_mbps:.6f}M"

        print(
            f"[FLUJO {flow_id:03d}] "
            f"{src} -> {dst} | "
            f"puerto={port} | "
            f"tasa_original={original_rate_mbps:.6f} Mbps | "
            f"tasa_ejecutada={scaled_rate_mbps:.6f} Mbps"
        )

        client_log = f"/tmp/client_{src}_{dst}_{port}.log"

        cmd = (
            f"echo '--- INICIO IPERF3 ---'; "
            f"iperf3 -u -c {dst_ip} "
            f"-p {port} "
            f"-b {rate} "
            f"-t {TRAFFIC_DURATION} "
            f"> {client_log} 2>&1 & "
            f"IPERF_PID=$!; "
            f"sleep 2; "
            f"echo '--- INICIO TRACEROUTE ---'; "
            f"traceroute -n -I "
            f"-m {TRACEROUTE_MAX_HOPS} "
            f"-w {TRACEROUTE_TIMEOUT} "
            f"{dst_ip}; "
            f"echo '--- FIN TRACEROUTE ---'; "
            f"wait $IPERF_PID; "
            f"IPERF_STATUS=$?; "
            f"echo '--- RESULTADO IPERF3 ---'; "
            f"cat {client_log}; "
            f"rm -f {client_log}; "
            f"exit $IPERF_STATUS"
        )

        full_cmd = [
            "vcmd",
            "-c", f"{session_path}/{src}",
            "--",
            "bash", "-lc", cmd
        ]

        process = subprocess.Popen(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        procs.append({
            "id": flow_id,
            "flow": flow,
            "original_rate_mbps": original_rate_mbps,
            "scaled_rate_mbps": scaled_rate_mbps,
            "process": process
        })

    print()
    print("Todos los flujos han sido lanzados.")

    print(
        f"Midiendo la carga de los enlaces durante "
        f"{MEASUREMENT_INTERVAL} segundos..."
    )
    load_samples, actual_interval = collect_link_load_samples(
        session_path,
        MEASUREMENT_INTERVAL
    )
    link_summary = summarize_link_load_samples(load_samples)
    total_transmitted_mbps = calculate_total_transmitted_traffic_mbps(
        flows,
        TRAFFIC_SCALE
    )

    print()
    print("Esperando a que terminen todos los flujos...")
    print()

    for item in procs:
        process = item["process"]
        flow = item["flow"]

        out, err = process.communicate()

        print()
        print("==========================================")
        print(
            f"RESULTADO FLUJO {item['id']:03d}: "
            f"{flow['src']} -> {flow['dst']}"
        )
        print("==========================================")
        print(f"Puerto: {flow['port']}")
        print(
            "Tasa original: "
            f"{item['original_rate_mbps']:.6f} Mbps"
        )
        print(
            "Tasa ejecutada: "
            f"{item['scaled_rate_mbps']:.6f} Mbps"
        )
        print(f"Duraci\u00f3n: {TRAFFIC_DURATION} segundos")
        print(f"C\u00f3digo de salida: {process.returncode}")
        print()

        if out:
            print(out, end="")

        if err:
            print()
            print("--- STDERR ---")
            print(err, end="")

        print()
        print(
            f"FIN FLUJO {item['id']:03d}: "
            f"{flow['src']} -> {flow['dst']}"
        )

    # El informe se muestra al final, despu\u00e9s del \u00faltimo resultado
    # de iperf3 y traceroute.
    print_link_load_report(
        link_summary,
        actual_interval,
        total_transmitted_mbps
    )


def stop_servers(session_path, nodes):
    for node in nodes:
        cmd = "pkill iperf3"

        full_cmd = [
            "vcmd",
            "-c", f"{session_path}/{node}",
            "--",
            "bash", "-lc", cmd
        ]

        result = subprocess.run(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            print(f"Procesos iperf3 cerrados en {node}")
        else:
            print(f"No hab\u00eda procesos iperf3 activos en {node}")


def run_all(session_path):
    print("==========================================")
    print("INICIO DE LA PRUEBA")
    print("==========================================")
    print(f"Sesi\u00f3n CORE: {session_path}")
    print(f"Capacidad de los enlaces: {LINK_CAPACITY_MBPS} Mbps")
    print(f"Factor de escala: {TRAFFIC_SCALE}")
    print(
        "Objetivo provisional: calcular la carga "
        "agregada por enlace"
    )
    print()

    try:
        print("Arrancando servidores iperf3...")
        start_servers(session_path, NODES)

        print()
        print("Esperando a que los servidores est\u00e9n preparados...")
        time.sleep(2)

        run_clients(session_path, NODES, FLOWS)

    finally:
        print()
        print("Cerrando servidores iperf3...")
        stop_servers(session_path, NODES)

    print()
    print("==========================================")
    print("FIN DE LA PRUEBA")
    print("==========================================")


if __name__ == "__main__":
    session_path = "/tmp/pycore.1"

    # Guarda resultados.txt en la misma carpeta que este script.
    script_directory = os.path.dirname(os.path.abspath(__file__))
    results_file = os.path.join(script_directory, "resultados.txt")

    # "w" borra los resultados de la ejecuci\u00f3n anterior.
    with open(results_file, "w", encoding="utf-8") as file:
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        sys.stdout = Tee(original_stdout, file)
        sys.stderr = Tee(original_stderr, file)

        try:
            print(f"Fichero de resultados: {results_file}")
            print()
            run_all(session_path)

        except KeyboardInterrupt:
            print("\nEjecuci\u00f3n interrumpida por el usuario.")

        except Exception as error:
            print(f"\nSe ha producido un error: {error}")

        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    print(f"\nResultados guardados en: {results_file}")
