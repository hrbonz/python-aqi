# -*- coding: utf-8 -*-


def get_algo(algo):
    """Instanciate an AQI algorithm class. If there is a problem during
    the import or instanciation, return None.

    :param algo: algorithm module canonical name
    :type algo: str
    """
    try:
        mod = __import__(algo, fromlist=[algo])
    except ImportError:
        return None

    return mod.AQI()
