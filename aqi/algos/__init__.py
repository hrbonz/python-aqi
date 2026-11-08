import importlib

# algorithm families and the module holding their versions, each module has
# a ``VERSIONS`` dict (oldest first) and an ``AQI`` class, the latest version
FAMILIES = {
    "epa": "aqi.algos.epa",
    "mep": "aqi.algos.mep",
}


def _versions(family):
    return importlib.import_module(FAMILIES[family]).VERSIONS


def available_algos():
    """Return the names of all the algorithm versions, as ``family:version``
    strings, ordered by family and then from the oldest to the latest version.
    """
    return [
        f"{family}:{version}" for family in FAMILIES for version in _versions(family)
    ]


def get_algo(algo):
    """Instanciate an AQI algorithm class. If the algorithm is unknown or
    there is a problem during the import or instanciation, return None.

    :param algo: one of

        * a ``family:version`` string like ``'epa:2012'``
        * a family name like ``'epa'``, the latest version
        * a module canonical name like ``'aqi.algos.epa'``, the latest
          version of the module (this is how algorithms were always named)
    :type algo: str
    """
    family, sep, version = algo.partition(":")
    if family in FAMILIES:
        versions = _versions(family)
        if not sep:
            return versions[list(versions)[-1]]()
        if version in versions:
            return versions[version]()
        return None
    if sep:
        return None

    # a module path
    try:
        mod = importlib.import_module(algo)
    except (ImportError, ValueError):
        return None
    try:
        return mod.AQI()
    except AttributeError:
        return None


def list_algos():
    """Return a list of tuples with the name of each available algorithm
    version and its corresponding pollutants
    """
    return [(name, get_algo(name).list_pollutants()) for name in available_algos()]
