"""Finds the module that defines a creature and builds it (model, texture, glow mask, animations)."""
import importlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MODULES = sorted(f[:-3] for f in os.listdir(HERE) if f.startswith("w") and f.endswith(".py"))


def find(mid):
    for m in MODULES:
        mod = importlib.import_module(m)
        if hasattr(mod, mid):
            return getattr(mod, mid)
    return None


def build(mid, seed=None):
    import zlib
    from common import finish
    fn = find(mid)
    if fn is None:
        return None
    return finish(fn(), zlib.crc32(mid.encode()) if seed is None else seed)


def available():
    out = []
    for m in MODULES:
        mod = importlib.import_module(m)
        out += [n for n in dir(mod) if not n.startswith("_") and callable(getattr(mod, n)) and getattr(getattr(mod, n), "__module__", "") == m]
    return out
