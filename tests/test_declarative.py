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
