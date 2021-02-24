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


class EnumMeta(type):
    def __new__(cls, typename, bases, ns):
        if ns.get("_ROOT", False):
            return super().__new__(cls, typename, bases, ns)

        cenum = pycstruct.EnumDef()
        for name, value in ns.items():
            if name.startswith("__"):
                continue
            if not isinstance(value, int):
                raise TypeError("Only integer are supported for enums")
            cenum.add(name, value)

        return cenum


class Enum(metaclass=EnumMeta):
    _ROOT = True
