import inspect
import os

networks = ["Net1.inp", "Net3.inp", "Adjumani_network_simplified2.inp", "Net3fixed.inp"]
path_to_examples = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
networks = [os.path.join(path_to_examples, x) for x in networks]
