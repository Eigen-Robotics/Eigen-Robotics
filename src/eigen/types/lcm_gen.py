#!/usr/bin/env python3
"""
Lightweight LCM -> Python generator (stdlib only)

- Parses .lcm with optional `package ...;` and multiple structs
- Emits one Python file per struct
- Output style is close to lcm's Python emitter, including:
  - __slots__
  - __typenames__
  - __dimensions__ with shapes like [3], ["num_ranges"], [4]
  - encode/decode with single struct.pack for fixed primitive arrays
  - size-field-driven variable arrays
  - fingerprint + hash

CLI
---
python3 lcm_gen.py --py-out gen_py defs/*.lcm
    => creates package dirs from .lcm packages

python3 lcm_gen.py --py-out gen_py --no-package-dirs defs/*.lcm
    => writes all .py into gen_py, but generated imports become relative
       (from .Msg import Msg) so everything works from a flat package
"""

import argparse
import dataclasses
import enum
import io
import os
import pathlib
import re
import struct as pystruct
import token
import tokenize
from typing import List, Optional, Union, Dict, Tuple


# -----------------------------------------------------------------------------
# LCM model
# -----------------------------------------------------------------------------

PrimitiveType = enum.Enum(
    "PrimitiveType",
    " ".join(
        [
            "boolean",
            "byte",
            "double",
            "float",
            "int8_t",
            "int16_t",
            "int32_t",
            "int64_t",
            "string",
        ]
    ),
)
PrimitiveType.__str__ = lambda self: self.name

# add this helper near the top (after PRIM_TO_FMT)
PRIM_TO_CODE = {
    PrimitiveType.boolean: "b",
    PrimitiveType.byte: "B",
    PrimitiveType.int8_t: "b",
    PrimitiveType.int16_t: "h",
    PrimitiveType.int32_t: "i",
    PrimitiveType.int64_t: "q",
    PrimitiveType.float: "f",
    PrimitiveType.double: "d",
}


@dataclasses.dataclass(frozen=True)
class UserType:
    package: Optional[str]
    name: str

    def __str__(self):
        return f"{self.package}.{self.name}" if self.package else self.name


@dataclasses.dataclass(frozen=True)
class StructField:
    name: str
    typ: Union[PrimitiveType, UserType]
    array_dims: List[Union[int, str]] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class StructConstant:
    name: str
    typ: PrimitiveType
    value: Union[int, float]
    value_str: str


@dataclasses.dataclass(frozen=True)
class Struct:
    typ: UserType
    fields: List[StructField] = dataclasses.field(default_factory=list)
    constants: List[StructConstant] = dataclasses.field(default_factory=list)


# -----------------------------------------------------------------------------
# Parser (same as before, but supports multiple structs per file)
# -----------------------------------------------------------------------------

class Parser:
    @staticmethod
    def parse(*, filename) -> List[Struct]:
        return Parser(filename=filename)._root()

    def __init__(self, *, filename):
        self._filename = filename
        self._structs: List[Struct] = []
        self._package: Optional[str] = None

        data = pathlib.Path(filename).read_text(encoding="utf-8")
        data = self._remove_c_comments(data)
        data = self._remove_cpp_comments(data)

        bytes_io = io.BytesIO(data.encode("utf-8"))
        self._tokens = list(tokenize.tokenize(bytes_io.readline))
        self._i = 0
        self._consume(token.ENCODING)

    @staticmethod
    def _remove_c_comments(data: str) -> str:
        while True:
            m = re.search(r"/\*.*?\*/", data, flags=re.DOTALL)
            if not m:
                break
            replacement = "".join(ch if ch == "\n" else " " for ch in m.group())
            start, end = m.span()
            data = data[:start] + replacement + data[end:]
        return data

    @staticmethod
    def _remove_cpp_comments(data: str) -> str:
        return re.sub(r"//.*$", "", data, flags=re.MULTILINE)

    def _current_type(self):
        return self._tokens[self._i][0]

    def _current_value(self):
        return self._tokens[self._i][1]

    def _syntax_error_details(self):
        return (self._filename, self._tokens[self._i][2][0], None, None)

    def _expect(self, expected_type, expected_value=None):
        actual_value = self._current_value()
        actual_type = self._current_type()
        if expected_value is not None and actual_value != expected_value:
            raise SyntaxError(
                f"Expected '{expected_value}' but got '{actual_value}'",
                self._syntax_error_details(),
            )
        if actual_type != expected_type:
            raise SyntaxError(
                f"Expected {token.tok_name[expected_type]} but got {token.tok_name[actual_type]} ('{actual_value}')",
                self._syntax_error_details(),
            )

    def _advance(self):
        self._i += 1
        while self._current_type() in (token.NEWLINE, token.NL):
            self._i += 1

    def _consume(self, token_type, token_value=None):
        result = self._current_value()
        self._expect(token_type, token_value)
        if token_type != token.ENDMARKER:
            self._advance()
        return result

    def _root(self) -> List[Struct]:
        if self._current_type() == token.NAME and self._current_value() == "package":
            self._package = self._package_decl()

        while self._current_type() == token.NAME and self._current_value() == "struct":
            self._struct_decl()

        self._consume(token.ENDMARKER)
        return self._structs

    def _package_decl(self) -> str:
        self._consume(token.NAME, "package")
        parts = [self._consume(token.NAME)]
        while self._current_value() == ".":
            self._consume(token.OP, ".")
            parts.append(self._consume(token.NAME))
        pkg = ".".join(parts)
        self._consume(token.OP, ";")
        return pkg

    def _struct_decl(self):
        self._consume(token.NAME, "struct")
        name = self._consume(token.NAME)
        current_struct = Struct(typ=UserType(package=self._package, name=name))
        self._consume(token.OP, "{")

        while self._current_type() == token.NAME:
            if self._current_value() == "const":
                self._const_statement(current_struct)
            else:
                self._field_statement(current_struct)

        self._consume(token.OP, "}")
        self._structs.append(current_struct)

    def _const_statement(self, current_struct: Struct):
        self._consume(token.NAME, "const")
        typ_str = self._consume(token.NAME)
        try:
            typ = PrimitiveType[typ_str]
        except KeyError:
            self._i -= 1
            raise SyntaxError(
                f"Expected primitive type for const but got '{typ_str}'",
                self._syntax_error_details(),
            )
        self._const_definition(typ, current_struct)
        while self._current_value() == ",":
            self._consume(token.OP, ",")
            self._const_definition(typ, current_struct)
        self._consume(token.OP, ";")

    def _const_definition(self, typ: PrimitiveType, current_struct: Struct):
        name = self._consume(token.NAME)
        self._consume(token.OP, "=")
        sign = ""
        if self._current_value() in ["+", "-"]:
            sign = self._consume(token.OP)
        val_str = sign + self._consume(token.NUMBER)
        try:
            val = float(val_str) if typ in (PrimitiveType.float, PrimitiveType.double) else int(val_str)
        except ValueError:
            raise SyntaxError(f"Invalid const value {val_str}", self._syntax_error_details())
        current_struct.constants.append(
            StructConstant(name=name, typ=typ, value=val, value_str=val_str)
        )

    def _field_statement(self, current_struct: Struct):
        typ = self._qualified_identifier()
        name = self._consume(token.NAME)
        dims = []
        while self._current_value() == "[":
            self._consume(token.OP, "[")
            if self._current_type() == token.NAME:
                dim = self._consume(token.NAME)
            else:
                dim = int(self._consume(token.NUMBER))
            self._consume(token.OP, "]")
            dims.append(dim)
        self._consume(token.OP, ";")
        current_struct.fields.append(StructField(name=name, typ=typ, array_dims=dims))

    def _qualified_identifier(self):
        name1 = self._consume(token.NAME)
        try:
            return PrimitiveType[name1]
        except KeyError:
            pass
        if self._current_value() == ".":
            self._consume(token.OP, ".")
            name2 = self._consume(token.NAME)
            return UserType(package=name1, name=name2)
        return UserType(package=self._package, name=name1)


# -----------------------------------------------------------------------------
# Python emitter (LCM-style)
# -----------------------------------------------------------------------------

LCM_PY_HEADER = '''"""LCM type definitions
This file automatically generated by lcm.
DO NOT MODIFY BY HAND!!!!
"""


from io import BytesIO
import struct
'''

# match your example more closely: boolean -> >b
PRIM_TO_FMT = {
    PrimitiveType.boolean: (">b", 1),
    PrimitiveType.byte: (">B", 1),
    PrimitiveType.int8_t: (">b", 1),
    PrimitiveType.int16_t: (">h", 2),
    PrimitiveType.int32_t: (">i", 4),
    PrimitiveType.int64_t: (">q", 8),
    PrimitiveType.float: (">f", 4),
    PrimitiveType.double: (">d", 8),
    PrimitiveType.string: (None, None),
}


def _primitive_default(typ: PrimitiveType):
    if typ in (PrimitiveType.double, PrimitiveType.float):
        return "0.0"
    if typ == PrimitiveType.string:
        return "\"\""
    if typ == PrimitiveType.boolean:
        return "False"
    return "0"


class LcmPythonGen:
    def __init__(self, struct: Struct, *, no_package_dirs: bool = False):
        self.struct = struct
        # if True, we should emit relative imports for user types, e.g. `from .Foo import Foo`
        # regardless of what the .lcm file's `package` said.
        self.no_package_dirs = no_package_dirs

    def _compute_base_hash(self) -> int:
        data = []
        for f in self.struct.fields:
            data.append(f.name)
            if isinstance(f.typ, PrimitiveType):
                data.append(f.typ.name)
            data.append(len(f.array_dims))
            for dim in f.array_dims:
                data.append(1 if isinstance(dim, str) else 0)
                data.append(str(dim))
        chars = bytearray()
        for x in data:
            if isinstance(x, int):
                chars.append(x % 256)
            else:
                chars.append(len(x) % 256)
                chars.extend(ord(ch) for ch in x)
        value = 0x12345678
        for (c,) in pystruct.iter_unpack("<b", chars):
            value = ((value << 8) ^ (value >> 55)) + c
            value %= 2**64
            if value >= 2**63:
                value -= 2**64
        value %= 2**64
        return value

    def generate(self) -> str:
        cls_name = self.struct.typ.name
        base_hash = self._compute_base_hash()

        # imports: controlled by self.no_package_dirs
        imports: List[str] = []
        for f in self.struct.fields:
            if isinstance(f.typ, UserType):
                if self.no_package_dirs:
                    # flat output → relative import
                    imports.append(f"from .{f.typ.name} import {f.typ.name}")
                else:
                    if f.typ.package:
                        imports.append(f"from {f.typ.package}.{f.typ.name} import {f.typ.name}")
                    else:
                        imports.append(f"import {f.typ.name}")
        imports = sorted(set(imports))

        # build __typenames__ and __dimensions__
        typenames = []
        dimensions = []
        for f in self.struct.fields:
            if isinstance(f.typ, PrimitiveType):
                typenames.append(f.typ.name)
            else:
                if f.typ.package and not self.no_package_dirs:
                    typenames.append(f"{f.typ.package}.{f.typ.name}")
                else:
                    # in no-package-dirs mode, just use the bare name
                    typenames.append(f.typ.name)
            if not f.array_dims:
                dimensions.append(None)
            else:
                dim_list = []
                for d in f.array_dims:
                    if isinstance(d, int):
                        dim_list.append(d)
                    else:
                        dim_list.append(d)
                dimensions.append(dim_list)

        lines: List[str] = []
        lines.append(LCM_PY_HEADER)
        for imp in imports:
            lines.append(f"{imp}\n")
        if imports:
            lines.append("\n")

        lines.append(f"class {cls_name}(object):\n\n")
        slots = [f.name for f in self.struct.fields]
        lines.append(f"    __slots__ = {slots!r}\n\n")
        lines.append(f"    __typenames__ = {typenames!r}\n\n")
        dim_repr_parts = []
        for d in dimensions:
            if d is None:
                dim_repr_parts.append("None")
            else:
                inner_parts = []
                for x in d:
                    if isinstance(x, int):
                        inner_parts.append(str(x))
                    else:
                        inner_parts.append(repr(x))
                dim_repr_parts.append(f"[{', '.join(inner_parts)}]")
        lines.append(f"    __dimensions__ = [{', '.join(dim_repr_parts)}]\n\n")

        # __init__
        lines.append("    def __init__(self):\n")
        if self.struct.fields:
            for f in self.struct.fields:
                if not f.array_dims:
                    if isinstance(f.typ, PrimitiveType):
                        lines.append(f"        self.{f.name} = {_primitive_default(f.typ)}\n")
                        lines.append(f"        \"\"\" LCM Type: {f.typ.name} \"\"\"\n")
                    else:
                        lines.append(f"        self.{f.name} = {f.typ.name}()\n")
                        lines.append(f"        \"\"\" LCM Type: {f.typ.name} \"\"\"\n")
                else:
                    first_dim = f.array_dims[0]
                    if isinstance(f.typ, PrimitiveType) and isinstance(first_dim, int):
                        default = _primitive_default(f.typ)
                        lines.append(
                            f"        self.{f.name} = [ {default} for dim0 in range({first_dim}) ]\n"
                        )
                        lines.append(
                            f"        \"\"\" LCM Type: {f.typ.name}[{first_dim}] \"\"\"\n"
                        )
                    else:
                        lines.append(f"        self.{f.name} = []\n")
                        if isinstance(first_dim, str):
                            lines.append(
                                f"        \"\"\" LCM Type: {self._field_type_str(f)}[{first_dim}] \"\"\"\n"
                            )
                        else:
                            lines.append(
                                f"        \"\"\" LCM Type: {self._field_type_str(f)}[{first_dim}] \"\"\"\n"
                            )
        else:
            lines.append("        pass\n")

        # encode
        lines.append(
            "\n    def encode(self):\n"
            "        buf = BytesIO()\n"
            f"        buf.write({cls_name}._get_packed_fingerprint())\n"
            "        self._encode_one(buf)\n"
            "        return buf.getvalue()\n"
        )

        # _encode_one
        lines.append("\n    def _encode_one(self, buf):\n")
        if self.struct.fields:
            for f in self.struct.fields:
                lines.extend(self._emit_encode_field(f))
        else:
            lines.append("        pass\n")

        # decode + _decode_one
        lines.append(
            "\n    @staticmethod\n"
            "    def decode(data: bytes):\n"
            "        if hasattr(data, 'read'):\n"
            "            buf = data\n"
            "        else:\n"
            "            buf = BytesIO(data)\n"
            f"        if buf.read(8) != {cls_name}._get_packed_fingerprint():\n"
            "            raise ValueError(\"Decode error\")\n"
            f"        return {cls_name}._decode_one(buf)\n"
        )

        lines.append(
            "\n    @staticmethod\n"
            "    def _decode_one(buf):\n"
            f"        self = {cls_name}()\n"
        )
        if self.struct.fields:
            for f in self.struct.fields:
                lines.extend(self._emit_decode_field(f))
        lines.append("        return self\n")

        # hash
        lines.append(
            "\n    @staticmethod\n"
            "    def _get_hash_recursive(parents):\n"
            f"        if {cls_name} in parents: return 0\n"
            f"        newparents = parents + [{cls_name}]\n"
            f"        tmphash = ({base_hash:#018x}"
        )
        for f in self.struct.fields:
            if isinstance(f.typ, UserType):
                lines.append(f" + {f.typ.name}._get_hash_recursive(newparents)")
        lines.append(") & 0xffffffffffffffff\n")
        lines.append(
            "        tmphash  = (((tmphash<<1)&0xffffffffffffffff) + (tmphash>>63)) & 0xffffffffffffffff\n"
            "        return tmphash\n"
        )

        lines.append("    _packed_fingerprint = None\n\n")
        lines.append(
            "    @staticmethod\n"
            f"    def _get_packed_fingerprint():\n"
            f"        if {cls_name}._packed_fingerprint is None:\n"
            f"            {cls_name}._packed_fingerprint = struct.pack(\">Q\", {cls_name}._get_hash_recursive([]))\n"
            f"        return {cls_name}._packed_fingerprint\n"
        )
        lines.append(
            "\n    def get_hash(self):\n"
            f"        return struct.unpack(\">Q\", {cls_name}._get_packed_fingerprint())[0]\n"
        )

        return "".join(lines)

    def _field_type_str(self, f: StructField) -> str:
        if isinstance(f.typ, PrimitiveType):
            return f.typ.name
        if f.typ.package and not self.no_package_dirs:
            return f"{f.typ.package}.{f.typ.name}"
        return f.typ.name

    # ---------------- encoders -----------------

    def _emit_encode_field(self, f: StructField) -> List[str]:
        lines: List[str] = []
        if f.array_dims:
            first_dim = f.array_dims[0]
            if isinstance(f.typ, PrimitiveType) and isinstance(first_dim, int):
                code = PRIM_TO_CODE[f.typ]
                lines.append(
                    f"        buf.write(struct.pack('>{first_dim}{code}', *self.{f.name}[:{first_dim}]))\n"
                )
                return lines
            if isinstance(f.typ, PrimitiveType) and isinstance(first_dim, str):
                code = PRIM_TO_CODE[f.typ]
                lines.append(
                    f"        buf.write(struct.pack('>%s{code}' % self.{first_dim}, *self.{f.name}[:self.{first_dim}]))\n"
                )
                return lines
            if isinstance(first_dim, str):
                lines.append(f"        for _x in self.{f.name}:\n")
            else:
                lines.append(f"        for _x in self.{f.name}:\n")
            if isinstance(f.typ, PrimitiveType):
                fmt, _ = PRIM_TO_FMT[f.typ]
                lines.append(f"            buf.write(struct.pack('{fmt}', _x))\n")
            else:
                lines.append(f"            assert _x._get_packed_fingerprint() == {f.typ.name}._get_packed_fingerprint()\n")
                lines.append("            _x._encode_one(buf)\n")
            return lines

        if isinstance(f.typ, PrimitiveType):
            if f.typ == PrimitiveType.string:
                lines.append(f"        __{f.name}_encoded = self.{f.name}.encode('utf-8')\n")
                lines.append(f"        buf.write(struct.pack('>I', len(__{f.name}_encoded)+1))\n")
                lines.append(f"        buf.write(__{f.name}_encoded)\n")
                lines.append("        buf.write(b\"\\0\")\n")
            else:
                fmt, _ = PRIM_TO_FMT[f.typ]
                lines.append(f"        buf.write(struct.pack('{fmt}', self.{f.name}))\n")
        else:
            lines.append(f"        assert self.{f.name}._get_packed_fingerprint() == {f.typ.name}._get_packed_fingerprint()\n")
            lines.append(f"        self.{f.name}._encode_one(buf)\n")
        return lines

    # ---------------- decoders -----------------

    def _emit_decode_field(self, f: StructField) -> List[str]:
        lines: List[str] = []
        if f.array_dims:
            first_dim = f.array_dims[0]
            if isinstance(f.typ, PrimitiveType) and isinstance(first_dim, int):
                code = PRIM_TO_CODE[f.typ]
                size = PRIM_TO_FMT[f.typ][1]
                total_bytes = first_dim * size
                lines.append(
                    f"        self.{f.name} = struct.unpack('>{first_dim}{code}', buf.read({total_bytes}))\n"
                )
                return lines
            if isinstance(f.typ, PrimitiveType) and isinstance(first_dim, str):
                code = PRIM_TO_CODE[f.typ]
                size = PRIM_TO_FMT[f.typ][1]
                lines.append(
                    f"        self.{f.name} = struct.unpack('>%s{code}' % self.{first_dim}, buf.read(self.{first_dim} * {size}))\n"
                )
                return lines

            if isinstance(first_dim, str):
                lines.append(f"        self.{f.name} = []\n")
                lines.append(f"        for _ in range(self.{first_dim}):\n")
            else:
                lines.append(f"        self.{f.name} = []\n")
                lines.append(f"        for _ in range({first_dim}):\n")
            if isinstance(f.typ, PrimitiveType):
                fmt, size = PRIM_TO_FMT[f.typ]
                lines.append(f"            _v = struct.unpack('{fmt}', buf.read({size}))[0]\n")
                lines.append(f"            self.{f.name}.append(_v)\n")
            else:
                lines.append(f"            _v = {f.typ.name}._decode_one(buf)\n")
                lines.append(f"            self.{f.name}.append(_v)\n")
            return lines

        if isinstance(f.typ, PrimitiveType):
            if f.typ == PrimitiveType.string:
                lines.append("        __len = struct.unpack('>I', buf.read(4))[0]\n")
                lines.append(f"        self.{f.name} = buf.read(__len)[:-1].decode('utf-8', 'replace')\n")
            else:
                fmt, size = PRIM_TO_FMT[f.typ]
                lines.append(f"        self.{f.name} = struct.unpack('{fmt}', buf.read({size}))[0]\n")
        else:
            lines.append(f"        self.{f.name} = {f.typ.name}._decode_one(buf)\n")
        return lines


# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LCM -> Python generator (LCM-style)")
    parser.add_argument("src", nargs="+", help="*.lcm source files")
    parser.add_argument("--py-out", required=True, type=pathlib.Path, help="output dir")
    parser.add_argument(
        "--no-package-dirs",
        action="store_true",
        help="do NOT create subfolders from LCM package; write all files into --py-out AND make imports relative",
    )
    args = parser.parse_args()

    real_cwd = os.environ.get("BUILD_WORKING_DIRECTORY")
    if real_cwd:
        os.chdir(real_cwd)

    args.py_out.mkdir(parents=True, exist_ok=True)

    # package path -> list of message names (for init)
    package_to_msgs: Dict[Tuple[str, ...], List[str]] = {}

    for src in args.src:
        structs = Parser.parse(filename=src)
        for st in structs:
            gen = LcmPythonGen(st, no_package_dirs=args.no_package_dirs)
            content = gen.generate()

            if args.no_package_dirs:
                out_dir = args.py_out
                pkg_key: Tuple[str, ...] = ()
                out_dir.mkdir(parents=True, exist_ok=True)
            else:
                out_dir = args.py_out
                if st.typ.package:
                    parts = st.typ.package.split(".")
                    pkg_key = tuple(parts)
                    for part in parts:
                        out_dir = out_dir / part
                        out_dir.mkdir(parents=True, exist_ok=True)
                else:
                    pkg_key = ()
                    out_dir.mkdir(parents=True, exist_ok=True)

            package_to_msgs.setdefault(pkg_key, []).append(st.typ.name)

            out_path = out_dir / f"{st.typ.name}.py"
            out_path.write_text(content, encoding="utf-8")

    # write __init__.py
    if args.no_package_dirs:
        msgs = sorted(package_to_msgs.get((), []))
        init_lines = []
        for msg in msgs:
            init_lines.append(f"from .{msg} import {msg}\n")
        if msgs:
            init_lines.append("\n__all__ = [\n")
            for msg in msgs:
                init_lines.append(f"    '{msg}',\n")
            init_lines.append("]\n")
        (args.py_out / "__init__.py").write_text("".join(init_lines), encoding="utf-8")
    else:
        for pkg_parts, msgs in package_to_msgs.items():
            dir_path = args.py_out
            for part in pkg_parts:
                dir_path = dir_path / part
            dir_path.mkdir(parents=True, exist_ok=True)
            init_path = dir_path / "__init__.py"
            msgs_sorted = sorted(msgs)
            lines = []
            for msg in msgs_sorted:
                lines.append(f"from .{msg} import {msg}\n")
            if msgs_sorted:
                lines.append("\n__all__ = [\n")
                for msg in msgs_sorted:
                    lines.append(f"    '{msg}',\n")
                lines.append("]\n")
            init_path.write_text("".join(lines), encoding="utf-8")
        (args.py_out / "__init__.py").touch(exist_ok=True)


if __name__ == "__main__":
    main()
