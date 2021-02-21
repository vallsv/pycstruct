from pycstruct import pycstruct


class StructMeta(type):
    def __new__(cls, typename, bases, ns):
        if ns.get("_ROOT", False):
            return super().__new__(cls, typename, bases, ns)
        types = ns.get("__annotations__", {})
        byteorder = ns.get("BYTEORDER", "native")
        alignment = ns.get("PACK", 1)

        cstruct = pycstruct.StructDef(default_byteorder=byteorder, alignment=alignment)
        for name, type in types.items():
            cstruct.add(type, name)

        return cstruct


class Struct(metaclass=StructMeta):
    _ROOT = True
