from random import randint
from enum import Enum
from collections import namedtuple


class InvalidImmediateException(Exception):
    """
    This exception is generated by Immediates for invalid values. It contains the message for the reason.
    """
    pass


class Immediate(object):
    """
    Immediate values are stored in this container, which safeguards them. An Immediate is configured for a bit width and
    can be signed or unsigned. Finally, there are immediates in RISC-V which are aligned to instruction address
    granularity, so that an immediate can be configured to be aligned to 16-bit boundaries (lsb = 0).

    :param bits: bit width of the immediate
    :type bits: int
    :param signed: Signedness of the immediate
    :type signed: bool
    :param lsb0: Set to True if this immediate is aligned to 16-bit boundaries
    :type lsb0: bool
    """
    def __init__(self, *, bits: int, signed: bool = False, lsb0: bool = False):
        self.bits = bits
        self.signed = signed
        self.lsb0 = lsb0
        self.value = 0
        self.tcmask = 1 << (self.bits - 1) # mask used for two's complement
        self.mask = (1 << self.bits) - 1

    def max(self) -> int:
        """
        Get the maximum value this immediate can have

        :return: Maximum value of this immediate
        """
        if self.signed:
            v = (1 << (self.bits - 1)) - 1
        else:
            v = (1 << self.bits) - 1
        if self.lsb0:
            v = v - (v % 2)
        return v

    def min(self) -> int:
        """
        Get the minimum value this immediate can have

        :return: Minimum value of this immediate
        """
        if self.signed:
            return -(1 << (self.bits - 1))
        else:
            return 0

    def exception(self, msg: str) -> InvalidImmediateException:
        # Generate exception
        message = "Immediate(bits={}, signed={}, lsb0={}) {}".format(self.bits, self.signed, self.lsb0, msg)
        return InvalidImmediateException(message)

    def set(self, value: int):
        """
        Set the immediate to a value. This function checks if the value is valid and will raise an
        :class:`InvalidImmediateException` if it doesn't.

        :param value: Value to set the immediate to
        :type value: int

        :raises InvalidImmediateException: value does not match immediate
        """
        if not isinstance(value, int):
            raise self.exception("{} is not an integer".format(value))
        if self.lsb0 and self.value % 2 == 1:
            raise self.exception("{} not power of two".format(value))
        if not self.signed and value < 0:
            raise self.exception("{} cannot be negative".format(value))
        if value < self.min() or value > self.max():
            raise self.exception("{} not in allowed range {}-{}".format(value, self.min(), self.max()))

        self.value = value

    def set_from_bits(self, value: int):
        """
        Set the immediate value from machine code bits. Those are not sign extended, so it will take care of the
        proper handling.

        :param value: Value to set the immediate to
        :type value: int
        """
        if self.signed:
            value = -(value & self.tcmask) + (value & ~self.tcmask)
        self.set(value)

    def randomize(self):
        """
        Randomize this immediate to a legal value
        """
        self.value = randint(self.min(), self.max())
        if self.lsb0:
            self.value = self.value - (self.value % 2)

    def __int__(self):
        """Convert to int"""
        return self.value.__int__()

    def unsigned(self):
        return self.value & self.mask

    def __str__(self):
        """Convert to string"""
        return self.value.__str__()

    def __repr__(self):
        return "Immediate(bits={}, signed={}, lsb0={}, value={:x})".format(self.bits, self.signed, self.lsb0, self.value)

    def __format__(self, format_spec):
        """Apply format spec"""
        return self.value.__format__(format_spec)

    def __lshift__(self, shamt):
        bits = self.bits + shamt
        new = Immediate(bits=bits, signed=self.signed, lsb0=self.lsb0)
        new.set(self.value << shamt)
        return new

    def __eq__(self, other):
        return self.value == other.value


class Register(object):
    def __init__(self, bits: int):
        self.bits = bits
        self.immutable = False
        self.value = 0
        self.format = "{{:0{}x}}".format(int(bits/4))
        self.mask = (1 << bits) - 1

    def set_immutable(self, s: bool):
        self.immutable = s

    def randomize(self):
        if not self.immutable:
            self.value = randint(0, 1 << self.bits - 1)

    def set(self, value):
        if isinstance(value, (Register, Immediate)):
            value = value.value
        if not self.immutable:
            self.value = value
        if (self.value >> (self.bits - 1)) & 1 != 0:
            self.value |= ~self.mask
        else:
            self.value &= self.mask

    def __int__(self):
        return self.value

    def unsigned(self):
        return self.value & self.mask

    def __str__(self):
        return self.format.format(self.value & self.mask)

    def __add__(self, other):
        new = Register(self.bits)
        new.set(self.value + int(other))
        return new

    def __sub__(self, other):
        new = Register(self.bits)
        new.set(self.value - int(other))
        return new

    # todo: doesn't work
    def __cmp__(self, other):
        print("cmp")
        return self.bits != other.bits or self.value != other.value

    def __and__(self, other):
        new = Register(self.bits)
        if isinstance(other, int):
            new.set(self.value & other)
        elif isinstance(other, (Register, Immediate)):
            new.set(self.value & other.value)
        else:
            raise TypeError("unsupported operand type for Register &: {}".format(other.__class__))
        return new

    def __or__(self, other):
        new = Register(self.bits)
        if isinstance(other, int):
            new.set(self.value | other)
        elif isinstance(other, (Register, Immediate)):
            new.set(self.value | other.value)
        else:
            raise TypeError("unsupported operand type for Register |: {}".format(other.__class__))
        return new

    def __lt__(self, other):
        return self.value < int(other)

    def __xor__(self, other):
        new = Register(self.bits)
        if isinstance(other, int):
            new.set(self.value ^ other)
        elif isinstance(other, (Register, Immediate)):
            new.set(self.value ^ other.value)
        else:
            raise TypeError("unsupported operand type for Register ^: {}".format(other.__class__))
        return new

    def __lshift__(self, other):
        new = Register(self.bits)
        if isinstance(other, int):
            new.set(self.value << other)
        elif isinstance(other, (Register, Immediate)):
            new.set(self.value << other.value)
        else:
            raise TypeError("unsupported operand type for Register <<: {}".format(other.__class__))
        return new

    def __rshift__(self, other):
        new = Register(self.bits)
        if isinstance(other, int):
            new.set(self.value >> other)
        elif isinstance(other, (Register, Immediate)):
            new.set(self.value >> other.value)
        else:
            raise TypeError("unsupported operand type for Register <<: {}".format(other.__class__))
        return new


class RegisterFile(object):
    def __init__(self, num: int, bits: int, immutable: list = {}):
        self.num = num
        self.bits = bits
        self.regs = []
        self.regs_updates = []
        for i in range(num):
            self.regs.append(Register(bits))

        for r in immutable.items():
            self.regs[r[0]].set(r[1])
            self.regs[r[0]].set_immutable(True)

    def randomize(self):
        for i in range(self.num):
            self.regs[i].randomize()

    def __setitem__(self, key, value):
        if not self.regs[key].immutable:
            reg = Register(self.bits)
            reg.set(value)
            self.regs_updates.append(TraceIntegerRegister(key, reg))

    def __getitem__(self, item):
        return self.regs[item]

    def commit(self):
        for t in self.regs_updates:
            self.regs[t.id].set(t.value)
        self.regs_updates.clear()

    def changes(self) -> list:
        return self.regs_updates.copy()

    def __str__(self):
        return "{}".format([str(r) for r in self.regs])


class Trace(object):
    pass


class TracePC(Trace):
    def __init__(self, pc):
        self.pc = pc

    def __str__(self):
        return "pc = {}".format(self.pc_update)


class TraceRegister(Trace):
    def __init__(self, id, value):
        self.id = id
        self.value = int(value)

    def __str__(self):
        return "{} = {}".format(self.id, self.value)


class TraceIntegerRegister(TraceRegister):
    def __str__(self):
        return "x{} = {:08x}".format(self.id, self.value)


class TraceMemory(Trace):
    GRANULARITY = Enum('granularity', ['BYTE', 'HALFWORD', 'WORD'])

    def __init__(self, gran: GRANULARITY, addr: int, data: int):
        self.gran = gran
        self.addr = addr
        self.data = data

    def __str__(self):
        if self.gran == TraceMemory.GRANULARITY.BYTE:
            data = "{:02x}".format(self.data & 0xFF)
        elif self.gran == TraceMemory.GRANULARITY.HALFWORD:
            data = "{:04x}".format(self.data & 0xFFFF)
        else:
            data = "{:08x}".format(self.data)
        return "mem[{}] = {}".format(self.addr, data)


RVFISignals = namedtuple("RVFISignals", ["valid", "order", "insn",
                                         "rs1_addr", "rs1_rdata", "rs2_addr", "rs2_rdata", "rd_addr", "rd_wdata",
                                         "pc_rdata", "pc_wdata"])
RVFISignals.__new__.__defaults__ = (None,) * len(RVFISignals._fields)
