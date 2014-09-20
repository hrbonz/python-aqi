# -*- coding: utf-8 -*-
import pkgutil


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

def list_algos():
    """Return a list of available algorithms with corresponding
    pollutant
    """
    _algos = []
    package = __import__('aqi.algos', fromlist=['aqi.algos'])
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
        if ispkg is False and modname != 'base':
            algo_pack = __import__('aqi.algos.' + modname, fromlist=['aqi.algos.' + modname])
            _aqi = algo_pack.AQI()
            _algos.append((modname, _aqi.list_pollutants()))
    return _algos
