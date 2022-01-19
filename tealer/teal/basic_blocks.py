from typing import List, Optional, TYPE_CHECKING

from tealer.teal.instructions.instructions import Instruction

if TYPE_CHECKING:
    from tealer.teal.teal import Teal


class BasicBlock:
    def __init__(self) -> None:
        self._instructions: List[Instruction] = []
        self._prev: List[BasicBlock] = []
        self._next: List[BasicBlock] = []
        self._idx: int = 0
        self._teal: Optional["Teal"] = None

    def add_instruction(self, instruction: Instruction) -> None:
        self._instructions.append(instruction)

    @property
    def instructions(self) -> List[Instruction]:
        return self._instructions

    @property
    def entry_instr(self) -> Instruction:
        return self._instructions[0]

    @property
    def exit_instr(self) -> Instruction:
        return self._instructions[-1]

    def add_prev(self, p: "BasicBlock") -> None:
        self._prev.append(p)

    def add_next(self, n: "BasicBlock") -> None:
        self._next.append(n)

    @property
    def prev(self) -> List["BasicBlock"]:
        return self._prev

    @property
    def next(self) -> List["BasicBlock"]:
        return self._next

    @property
    def idx(self) -> int:
        return self._idx

    @idx.setter
    def idx(self, i: int) -> None:
        self._idx = i

    @property
    def cost(self) -> int:
        """cost of executing all instructions in this basic block"""
        return sum(ins.cost for ins in self.instructions)

    @property
    def teal(self) -> Optional["Teal"]:
        """Teal instance of the contract this basic block belongs to."""
        return self._teal

    @teal.setter
    def teal(self, teal_instance: "Teal") -> None:
        self._teal = teal_instance

    def __str__(self) -> str:
        ret = ""
        for ins in self._instructions:
            ret += f"{ins.line}: {ins}\n"
        return ret
