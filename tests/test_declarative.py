import unittest
import pycstruct
from pycstruct import declarative


class MyColor(declarative.Struct):
    PACK = 1
    r: "uint8"
    g: "uint8"
    b: "uint8"
    a: "uint8"


class MyStruct(declarative.Struct):
    BYTEORDER = "little"
    PACK = 1

    a: "uint8"
    b: "uint8"
    c: "uint16"
    d: "uint8"
    color: MyColor


class MyStructOfArrayOfColors(declarative.Struct):
    BYTEORDER = "little"
    PACK = 1

    colors: MyColor[10]


class TestDeclarative(unittest.TestCase):
    def test_type(self):
        self.assertIsInstance(MyStruct, pycstruct.StructDef)

    def test_struct(self):
        raw = b"\x01\x02\x03\x04"
        color = MyColor.instance(raw)
        self.assertEqual(color.r, 1)
        self.assertEqual(color.g, 2)
        self.assertEqual(color.b, 3)
        self.assertEqual(color.a, 4)

    def test_compound_struct(self):
        raw = b"\x00\x00\x00\x00\x00\x01\x02\x03\x04"
        compound = MyStruct.instance(raw)
        self.assertEqual(compound.color.a, 4)

    def test_array(self):
        raw = (b"\x10\x20\x30\x00" * 9) + b"\x40\x50\x60\x00"
        struct = MyStructOfArrayOfColors.instance(raw)
        self.assertEqual(struct.colors[0].r, 0x10)
        self.assertEqual(struct.colors[9].r, 0x40)

    def test_valid_enum(self):
        class EnumColor(declarative.Enum):
            red = 0
            green = 1
            blue = 2

        class Shape(declarative.Struct):
            background: EnumColor

        raw = b"\x01"
        e = Shape.instance(raw)
        self.assertEqual(e.background, "green")

    def test_invalid_enum(self):
        with self.assertRaises(TypeError):

            class EnumWithWrongValue(declarative.Enum):
                red = "red"
