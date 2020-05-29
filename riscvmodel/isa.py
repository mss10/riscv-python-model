from .insn import *
from .variant import RV64I,Extensions


@isa("lui", 0x37)
class InstructionLUI(InstructionUType):
    """
    The Load Upper Immediate (LUI) instruction loads the given immediate (unsigned 20 bit) to the upper 20 bit
    of the destination register. The lower bits are set to zero in the destination register. This instruction
    can be used to efficiently form constants, as a sequence of LUI and ORI for example.
    """
    def execute(self, model: State):
        model.intreg[self.rd] = (self.imm << 12)


@isa("auipc", 0x17)
class InstructionAUIPC(InstructionUType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.pc + (self.imm << 12)


@isa("jal", 0x6F)
class InstructionJAL(InstructionJType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.pc + 4
        model.pc = self.imm


@isa("jalr", 0x67, 0)
class InstructionJALR(InstructionIType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.pc + 4
        model.pc = model.intreg[self.rs1] + self.imm


@isa("beq", 0x63, 0)
class InstructionBEQ(InstructionBType):
    def execute(self, model: State):
        # todo: problem with __cmp__
        if model.intreg[self.rs1].value == model.intreg[self.rs2].value:
            model.pc = model.pc + self.imm


@isa("bne", 0x63, 1)
class InstructionBNE(InstructionBType):
    def execute(self, model: State):
        if model.intreg[self.rs1].value != model.intreg[self.rs2].value:
            model.pc = model.pc + self.imm


@isa("blt", 0x63, 4)
class InstructionBLT(InstructionBType):
    def execute(self, model: State):
        if model.intreg[self.rs1].value < model.intreg[self.rs2].value:
            model.pc = model.pc + self.imm


@isa("bge", 0x63, 5)
class InstructionBGE(InstructionBType):
    def execute(self, model: State):
        if model.intreg[self.rs1].value >= model.intreg[self.rs2].value:
            model.pc = model.pc + self.imm


@isa("bltu", 0x63, 6)
class InstructionBLTU(InstructionBType):
    def execute(self, model: State):
        if model.intreg[self.rs1].unsigned() < model.intreg[self.rs2].unsigned():
            model.pc = model.pc + self.imm


@isa("bgeu", 0x63, 7)
class InstructionBGEU(InstructionBType):
    def execute(self, model: State):
        if model.intreg[self.rs1].unsigned() >= model.intreg[self.rs2].unsigned():
            model.pc = model.pc + self.imm


@isa("lb", 0x03, 0)
class InstructionLB(InstructionILType):
    def execute(self, model: State):
        data = model.lb((model.intreg[self.rs1] + self.imm).unsigned())
        if (data >> 7) & 0x1:
            data |= 0xFFFFFF00
        model.intreg[self.rd] = data

@isa("lh", 0x03, 1)
class InstructionLH(InstructionILType):
    def execute(self, model: State):
        data = model.lh((model.intreg[self.rs1] + self.imm).unsigned())
        if (data >> 15) & 0x1:
            data |= 0xFFFF0000
        model.intreg[self.rd] = data


@isa("lw", 0x03, 2)
class InstructionLW(InstructionILType):
    def execute(self, model: State):
        data = model.lw((model.intreg[self.rs1] + self.imm).unsigned())
        model.intreg[self.rd] = data


@isa("lbu", 0x03, 4)
class InstructionLBU(InstructionILType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.lb((model.intreg[self.rs1] + self.imm).unsigned())


@isa("lhu", 0x03, 5)
class InstructionLHU(InstructionILType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.lh((model.intreg[self.rs1] + self.imm).unsigned())


@isa("sb", 0x23, 0)
class InstructionSB(InstructionSType):
    def execute(self, model: State):
        model.sb((model.intreg[self.rs1] + self.imm).unsigned(), model.intreg[self.rs2])


@isa("sh", 0x23, 1)
class InstructionSH(InstructionSType):
    def execute(self, model: State):
        model.sh((model.intreg[self.rs1] + self.imm).unsigned(), model.intreg[self.rs2])


@isa("sw", 0x23, 2)
class InstructionSW(InstructionSType):
    def execute(self, model: State):
        model.sw((model.intreg[self.rs1] + self.imm).unsigned(), model.intreg[self.rs2])


@isa("addi", 0x13, 0)
class InstructionADDI(InstructionIType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] + self.imm


@isa("slti", 0x13, 2)
class InstructionSLTI(InstructionIType):
    def execute(self, model: State):
        if model.intreg[self.rs1] < self.imm:
            model.intreg[self.rd] = 1
        else:
            model.intreg[self.rd] = 0


@isa("sltiu", 0x13, 3)
class InstructionSLTIU(InstructionIType):
    def execute(self, model: State):
        if model.intreg[self.rs1].unsigned() < int(self.imm):
            model.intreg[self.rd] = 1
        else:
            model.intreg[self.rd] = 0


@isa("xori", 0x13, 4)
class InstructionXORI(InstructionIType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] ^ self.imm


@isa("ori", 0x13, 6)
class InstructionORI(InstructionIType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] | self.imm


@isa("andi", 0x13, 7)
class InstructionANDI(InstructionIType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] & self.imm


@isa("slli", 0x13, 1, 0x00)
class InstructionSLLI(InstructionISType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] << self.shamt


@isa("srli", 0x13, 5, 0x00)
class InstructionSRLI(InstructionISType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1].unsigned() >> int(self.shamt)


@isa("srai", 0x13, 5, 0x20)
class InstructionSRAI(InstructionISType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] >> self.shamt


@isa("add", 0x33, 0, 0x00)
class InstructionADD(InstructionRType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] + model.intreg[self.rs2]


@isa("sub", 0x33, 0, 0x20)
class InstructionSUB(InstructionRType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] - model.intreg[self.rs2]


@isa("sll", 0x33, 1, 0x00)
class InstructionSLL(InstructionRType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] << (model.intreg[self.rs2] & 0x1f)


@isa("slt", 0x33, 2, 0x00)
class InstructionSLT(InstructionRType):
    def execute(self, model: State):
        if model.intreg[self.rs1] < model.intreg[self.rs2]:
            model.intreg[self.rd] = 1
        else:
            model.intreg[self.rd] = 0


@isa("sltu", 0x33, 3, 0x00)
class InstructionSLTU(InstructionRType):
    def execute(self, state: State):
        if state.intreg[self.rs1].unsigned() < state.intreg[self.rs2].unsigned():
            state.intreg[self.rd] = 1
        else:
            state.intreg[self.rd] = 0


@isa("xor", 0x33, 4, 0x00)
class InstructionXOR(InstructionRType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] ^ model.intreg[self.rs2]


@isa("srl", 0x33, 5, 0x00)
class InstructionSRL(InstructionRType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] >> model.intreg[self.rs2]


@isa("sra", 0x33, 5, 0x20)
class InstructionSRA(InstructionRType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] >> model.intreg[self.rs2]


@isa("or", 0x33, 6, 0x00)
class InstructionOR(InstructionRType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] | model.intreg[self.rs2]


@isa("and", 0x33, 7, 0x00)
class InstructionAND(InstructionRType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] & model.intreg[self.rs2]


@isa("fence", 0xF, 0, 0x00)
class InstructionFENCE(Instruction):
    pass


@isa("fence.i", 0xF, 1, 0x00)
class InstructionFENCEI(Instruction):
    pass


@isa("ecall", 0x73, 0)
class InstructionECALL(InstructionIType):
    def execute(self, model: State):
        pass


@isa("ebreak", 0x73, 0)
class InstructionEBREAK(Instruction):
    def execute(self, model: State):
        pass


@isa("csrrw", 0x73, 1)
class InstructionCSRRW(InstructionIType):
    def execute(self, model: State):
        pass


@isa("csrrs", 0x73, 2)
class InstructionCSRRS(InstructionIType):
    def execute(self, model: State):
        pass


@isa("csrrc", 0x73, 3)
class InstructionCSRRC(Instruction):
    pass


@isa("csrrwi", 0x73, 5)
class InstructionCSRRWI(Instruction):
    pass


@isa("csrrsi", 0x73, 6)
class InstructionCSRRSI(Instruction):
    pass


@isa("csrrci", 0x73, 7)
class InstructionCSRRCI(Instruction):
    pass


@isa("lwu", 0x3, 6, variant=RV64I)
class InstructionLWU(InstructionIType):
    pass


@isa("ld", 0x3, 3, variant=RV64I)
class InstructionLD(InstructionIType):
    pass


@isa("sd", 0x23, 3, variant=RV64I)
class InstructionSD(InstructionISType):
    pass


@isa_pseudo()
class InstructionNOP(InstructionADDI):
    def __init__(self):
        super().__init__(0, 0, 0)


@isaC("c.addi", 1, funct3=0)
class InstructionCADDI(InstructionCIType):
    def expand(self):
        #addi rd, rd, nzimm[5:0]
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rd] + self.imm
        # x[rd] = x[rd] + sext(imm)

@isaC("c.addiw", 1, funct3=1, Variant=RV64I) #RV64C-only
class InstructionCADDI(InstructionCIType):
    def expand(self):
        #addi rd, rd, nzimm[5:0]
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rd] + self.imm
        # x[rd] = sext((x[rd] + sext(imm))[31:0])


@isaC("c.andi", 1, funct3=4)
class InstructionCANDI(InstructionCBType):
    def expand(self):
        pass


@isaC("c.swsp", 2, funct3=6)
class InstructionCSWSP(InstructionCSSType):
    def expand(self):
        #sw rs2,offset[7:2](x2)
        pass

    def decode(self, machinecode: int):
        self.rs = (machinecode >> 2) & 0x1f
        imm12to9 = (machinecode >> 9) & 0xf
        imm8to7 = (machinecode >> 7) & 0x3
        self.imm.set_from_bits((imm8to7 << 4) | imm12to9)
        #M[x[2] + uimm][31:0] = x[rs2]

    def execute(self, model: State):
        pass

@isaC("c.li", 1, funct3=2)
class InstructionCLI(InstructionCIType):
    def expand(self):
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = self.imm


@isaC("c.mv", 2, funct4=8)
class InstructionCMV(InstructionCRType):
    def expand(self):
        #
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs]

#########################################################################
#########################################################################
#########################################################################
@isaC("c.nop", 1, funct3=0)
class InstructionCNOP(InstructionCIType):
    def expand(self):
        #addi x0, x0, 0
        pass

    def execute(self, model: State):
        #None
        pass

@isaC("c.lui", 1, funct3=3)
class InstructionCLI(InstructionCIType):
    def expand(self):
        #lui rd,nzuimm[17:12]
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = (self.imm << 12)
        #x[rd] = sext(imm[17:12] << 12)

@isaC("c.addi16sp", 1, funct3=3)
class InstructionCLI(InstructionCIType):
    def expand(self):
        #addi x2,x2, nzimm[9:4]
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = self.intreg[self.rd] + self.imm
        #x[2] = x[2] + sext(imm)

@isaC("c.srli", 1, funct3=4)
class InstructionCSRLI(InstructionCBType):
    def expand(self):
        #srli rd’,rd’,64
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = self.intreg[self.rd] >> self.imm
        #x[8+rd’] = x[8+rd’] >>u uimm

@isaC("c.srai", 1, funct3=4)
class InstructionCSRAI(InstructionCBType):
    def expand(self):
        # srai rd’,rd’,shamt[5:0]
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = self.intreg[self.rd] >> self.imm
        # x[8+rd’] = x[8+rd’] >>s uimm

@isaC("c.ebreak", 2, funct4=4)
class InstructionCEBREAK(InstructionCRType):
    """
    Cause control to be transferred back to the debugging environment.
    C.EBREAK shares the opcode with the C.ADD instruction, but with rd and rs2
    both zero, thus can also use the CR format.
    """
    def expand(self):
        #ebreak
        pass

    def execute(self, model: State):
        #model.intreg[self.rd] = model.intreg[self.rs]
        #RaiseException(Breakpoint)
        pass

@isaC("c.addi4spn", 0, funct3=0) # RV32C/RV64C-only instruction 
class InstructionCADDI4SPN(InstructionCIWType):
    def expand(self):
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = self.intreg[self.rd] + self.imm
        #x[8+rd’] = x[2] + uimm
        #addi x2,x2,nzimm[9:4]

@isaC("c.slli", 2, funct3=2) # RV32C/RV64C-only instruction 
class InstructionCSSLI(InstructionCIType):
    def expand(self):
        #slli rd,rd,shamt[5:0]
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = self.intreg[self.rd] << self.imm
        #x[rd] = x[rd] << uimm

@isaC("c.add", 2, funct4=4)
class InstructionCADD(InstructionCRType):
    def expand(self):
        # add rd,rd,rs2
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = self.intreg[self.rd] + self.intreg[self.rs2]
        # x[rd] = x[rd] + x[rs2]


@isaC("c.sd", 0, funct3=7, variant=RV64I) #RV64C/RV128C-only instr
class InstructionCSD(InstructionCSType):
    def expand(self):
        # sd rs2’, offset[7:3](rs1’)
        pass

    def decode(self, machinecode: int):
        self.rs = (machinecode >> 2) & 0x1f
        imm12to9 = (machinecode >> 8) & 0xf
        imm8to7 = (machinecode >> 7) & 0x3
        self.imm.set_from_bits((imm8to7 << 4) | imm12to9)
        # M[x[8+rs1’] + uimm][63:0] = x[8+rs2’]

    def execute(self, model: State):
        pass

@isaC("c.sdsp", 2, funct3=7, variant=RV64I) #RV64C/RV128C-only instruction 
class InstructionCSDSP(InstructionCSSType):
    def expand(self):
        pass

    def decode(self, machinecode: int):
        self.rs = (machinecode >> 2) & 0x1f
        imm12to9 = (machinecode >> 8) & 0xf
        imm8to7 = (machinecode >> 7) & 0x3
        self.imm.set_from_bits((imm8to7 << 4) | imm12to9)
        # M[x[2] + uimm][63:0] = x[rs2]
        # sd rs2,offset[8:3](x2)

    def execute(self, model: State):
        pass

@isaC("c.j", 1, funct3=5)
class InstructionCJ(InstructionCJType):
    def expand(self):
        #jal x0,offset[11:1]
        pass

    def execute(self, model: State):
        model.pc += self.imm
        # pc += sext(offset)

@isaC("c.beqz", 1, funct3=6)
class InstructionCBEQZ(InstructionCBType):
    def expand(self):
        # beq rs1’,x0,offset[8:1]
        pass

    def execute(self, model: State):
        #if (x[8+rs1’] == 0) pc += sext(offset)

        #if(model.intreg[self.rs] == 0):
        #self.pc += self.intreg[rs]
        pass

@isaC("c.bnez", 1, funct3=7)
class InstructionCBNEZ(InstructionCBType):
    def expand(self):
        # bne rs1’,x0,offset[8:1]
        pass

    def execute(self, model: State):
        #if (x[8+rs1’] != 0) pc += sext(offset)

        #if(model.intreg[self.rs] != 0):
        #self.pc += self.intreg[rs]
        pass

@isaC("c.jal", 1, funct3=1, variant=RV32I) #RV32C-only
class InstructionCJAL(InstructionCJType):
    def expand(self):
        #jal x1, offset[11:1]
        pass

    def execute(self, model: State):
        #model.intreg[self.rd] = self.pc+2
        #model.pc += self.imm
        # x[1] = pc+2; pc += sext(offset)
        pass

@isaC("c.jr", 2, funct4=4)
class InstructionCJR(InstructionCRType):
    def expand(self):
        #jalr x0,rs1,0
        pass

    def execute(self, model: State):
        #model.intreg[self.rd] = model.intreg[self.rd] + self.imm
        model.pc = model.intreg[self.rs]
        # pc = x[rs1]

@isaC("c.jalr", 2, funct4=4)
class InstructionCJALR(InstructionCRType):
    def expand(self):
        # jalr x1,rs1,0
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = model.pc + 2
        model.pc = model.intreg[self.rs1]
        #t = self.pc + 2
        #model.intreg[1] = t
        # t = pc+2; pc = x[rs1]; x[1] = t
        pass


@isaC("c.lw", 0, funct3=2)
class InstructionCLW(InstructionCLType):
    def expand(self):
        # lw rd’,offset[6:2](rs1’)
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = self.intreg[self.rd] + self.imm
        # x[8+rd’] = sext(M[x[8+rs1’] + uimm][31:0])


@isaC("c.ld", 0, funct3=3, variant=RV64I) # RV64C/RV128C-only
class InstructionCLI(InstructionCLType):
    def expand(self):
        # ld rd’, offset[7:3](rs1’)
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = self.intreg[self.rd] + self.imm
        # x[8+rd’] = M[x[8+rs1’] + uimm][63:0]


@isaC("c.and", 1, funct6=35)
class InstructionCAND(InstructionCAType):
    def expand(self):
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = self.intreg[self.rd] & self.intreg[self.rs2]
        # x[8+rd’] = x[8+rd’] & x[8+rs2’]
        # and rd’,rd’,rs2’

@isaC("c.or", 1, funct6=35)
class InstructionCOR(InstructionCAType):
    def expand(self):
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = self.intreg[self.rd] | self.intreg[self.rs2]
        # x[8+rd’] = x[8+rd’] | x[8+rs2’]
        # or rd’,rd’,rs2’

@isaC("c.xor", 1, funct6=35)
class InstructionCXOR(InstructionCAType):
    def expand(self):
        # xor rd’,rd’,rs2’
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = self.rd ^ self.rs2
        # x[8+rd’] = x[8+rd’] ^ x[8+rs2’]


@isaC("c.sub", 1, funct6=35)
class InstructionCSUB(InstructionCAType):
    def expand(self):
        #sub rd’,rd’,rs2’
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = self.intreg[self.rd] - self.intreg[self.rs2]
        #x[8+rd’] = x[8+rd’] - x[8+rs2’]


@isaC("c.addw", 1, funct6=39, variant=RV64C) # RV64C/RV128C-only instruction t
class InstructionCADDW(InstructionCAType):
    def expand(self):
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = self.imm
        #x[8+rd’] = sext((x[8+rd’] + x[8+rs2’])[31:0])
        #addw rd’,rd’,rs2’


@isaC("c.subw", 1, funct6=39)
class InstructionCSUBW(InstructionCAType):
    def expand(self):
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = self.intreg[self.rd] - self.intreg[self.rs2]
        #x[8+rd’] = sext((x[8+rd’] - x[8+rs2’])[31:0])
        #subw rd’,rd’,rs2’
#####################################################################
@isaC("c.sw", 0, funct3=6)
class InstructionCSW(InstructionCSType):
    def expand(self):
        #sw rs2’,offset[6:2](rs1’)
        pass

    def execute(self, model: State):
        #model.intreg[self.rd] = self.intreg[self.rs2]
        # M[x[8+rs1’] + uimm][31:0] = x[8+rs2’]
        self.rs2 = (machinecode >> 2) & 0x1f
        self.rs1 = (machinecode >> 7) & 0x1f
        imm12to9 = (machinecode >> 8) & 0xf
        imm8to7 = (machinecode >> 7) & 0x3
        self.imm.set_from_bits((imm8to7 << 4) | imm12to9)

@isaC("c.lwsp", 2, funct3=2)
class InstructionCLWSP(InstructionCIType):
    def expand(self):
        #lw rd,offset[7:2](x2)
        pass

    def execute(self, model: State):
        #self.rs2 = (machinecode >> 2) & 0x1f
        #self.rs1 = (machinecode >> 7) & 0x1f
        #imm12 = (machinecode >> 12) & 0x1
        #imm7to6 = (machinecode >> 2) & 0x1f
        #imm4to2 = (machinecode >> 4) & 0x1f
        #self.imm.set_from_bits((imm12 << 7) | (imm7to6 << 5) | (imm4to2))

        #model.intreg[self.rd] = self.imm
        # x[rd] = sext(M[x[2] + uimm][31:0])
        pass


@isaC("c.ldsp", 2, funct3=3, Variant=RV64I) #RV64C/RV128C-only instruction
class InstructionCLDSP(InstructionCIType):
    def expand(self):
        #ld rd,offset[8:3](x2)
        pass

    def execute(self, model: State):
        #x[rd] = M[x[2] + uimm][63:0]
        model.intreg[self.rd] = self.imm
        pass