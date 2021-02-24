from pycstruct import pycstruct


class _StringType:
    def __getitem__(self, length):
        return pycstruct.StringDef(length)


Utf8 = _StringType()


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


class BitfieldMeta(type):
    def __new__(cls, typename, bases, ns):
        if ns.get("_ROOT", False):
            return super().__new__(cls, typename, bases, ns)
        types = ns.get("__annotations__", {})
        byteorder = ns.get("BYTEORDER", "native")
        size = ns.get("SIZE", -1)

        cbitfield = pycstruct.BitfieldDef(byteorder=byteorder, size=size)
        for name, size in types.items():
            if not isinstance(size, int):
                raise TypeError("Bitfield only support integer for sizes")
            cbitfield.add(name, size)

        return cbitfield


class Bitfield(metaclass=BitfieldMeta):
    _ROOT = True
