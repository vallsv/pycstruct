import timeit
import pycstruct
import numpy
import pprint


c_code = """

struct integers {
    int i0;
    int i1;
    int i2;
    int i3;
    int i4;
    int i5;
    int i6;
    int i7;
    int i8;
    int i9;
    int i10;
    int i11;
    int i12;
    int i13;
    int i14;
    int i15;
};

"""

_TYPE = {
    "int8": "i1",
    "uint8": "u1",
    "bool8": None,
    "int16": "i2",
    "uint16": "u2",
    "bool16": None,
    "float16": "f2",
    "int32": "i4",
    "uint32": "u4",
    "bool32": None,
    "float32": "f4",
    "int64": "i8",
    "uint64": "u8",
    "bool64": None,
    "float64": "f8",
}

_BYTEORDER = {
    "native": {"format": "="},
    "little": {"format": "<"},
    "big": {"format": ">"},
}

def to_dtype(struct) -> numpy.dtype:
    if isinstance(struct, pycstruct.pycstruct.BasicTypeDef):
        dtype = _TYPE[struct.type]
        if dtype is None:
            raise NotImplementedError(
                'Basic type "%s" is not implemented as dtype' % struct.type
            )
        byteorder = _BYTEORDER[struct.byteorder]["format"]
        dtype = byteorder + dtype
    elif isinstance(struct, pycstruct.pycstruct.StringDef):
        dtype = ("S", struct.length)
    elif isinstance(struct, pycstruct.pycstruct.StructDef):
        names = []
        formats = []
        offsets = []

        offset = 0
        for name, field in struct._StructDef__fields.items():
            datatype = field.type
            length = field.length

            if struct._StructDef__union:
                raise NotImplementedError("Union with dtype not implemented")

            if name.startswith("__pad"):
                pass
            else:
                if length > 1:
                    dtype = (to_dtype(datatype), length)
                else:
                    dtype = to_dtype(datatype)
                names.append(name)
                formats.append(dtype)
                offsets.append(offset)

            if not struct._StructDef__union:
                offset += datatype.size() * length

        dtype_def = {
            "names": names,
            "formats": formats,
            "offsets": offsets,
            "itemsize": struct.size(),
        }
        dtype = numpy.dtype(dtype_def)
    return dtype

DATA = b"1234" * 16


class TestPycstructDict:

    name = "dict"
    color = 'red'

    def __init__(self, nb=0):
        self.nb = nb
        struct_t = pycstruct.parse_str(c_code)["integers"]
        self.struct_t = struct_t

    def deserialize(self):
        self.decoded = self.struct_t.deserialize(DATA)

    def read(self):
        for n in range(self.nb):
            self.decoded["i%d" % n]

class TestPycstructInst:

    name = "instance"
    color = 'blue'

    def __init__(self, nb=0):
        self.nb = nb
        struct_t = pycstruct.parse_str(c_code)["integers"]
        self.struct_t = struct_t

    def deserialize(self):
        self.decoded = self.struct_t.instance(DATA)

    def read(self):
        for n in range(self.nb):
            getattr(self.decoded, "i%d" % n)

class TestPycstructNumpy:

    name = "numpy"
    color = 'green'

    def __init__(self, nb=0):
        self.nb = nb
        struct_t = pycstruct.parse_str(c_code)["integers"]
        self.struct_t = struct_t
        self.dtype = to_dtype(struct_t)

    def deserialize(self):
        self.decoded = numpy.frombuffer(DATA, dtype=self.dtype)[0]

    def read(self):
        for n in range(self.nb):
            self.decoded["i%d" % n]


testcases = [TestPycstructDict, TestPycstructInst, TestPycstructNumpy]
#testcases = [TestPycstructInst]


def collect_data(testcases):
    result = {}
    for testcase in testcases:
        test = testcase()
        v = timeit.repeat(test.deserialize, number=1, repeat=10)
        result[f"{testcase.name}_deserialize"] = numpy.min(v)
        result[f"{testcase.name}_read"] = []

        for i in range(16):
            test = testcase(nb=i)
            test.deserialize()
            v = timeit.repeat(test.read, number=1, repeat=30)
            result[f"{testcase.name}_read"].append(numpy.min(v))
    return result

def plot_result(result, testcases):
    from matplotlib import pyplot

    ax = pyplot.subplot(1, 1, 1)
    ax.set_ylabel("time")
    ax.set_xlabel("Percent of the structure read")

    for testcase in testcases:
        pos = 100 * numpy.arange(16) / 16
        value = [result[f"{testcase.name}_deserialize"]] * 16
        ax.plot(pos, value, linestyle="--", color=testcase.color, label=f"{testcase.name} deserialize")
        value = numpy.array(result[f"{testcase.name}_read"]) + result[f"{testcase.name}_deserialize"]
        ax.plot(pos, value, linestyle="-", color=testcase.color, label=f"{testcase.name} deserialize+read")

    pyplot.legend()
    pyplot.show()


result = collect_data(testcases)
pprint.pprint(result)
plot_result(result, testcases)
