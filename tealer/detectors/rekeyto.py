from collections import defaultdict
from copy import copy
from pathlib import Path
from typing import Dict, Set, List

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import Gtxn, Return, Int
from tealer.teal.instructions.transaction_field import RekeyTo


class Result:
    def __init__(self, filename: Path, bbs: List[BasicBlock], path_initial: List[BasicBlock]):
        self.filename = filename
        self.bbs = bbs
        self.paths = [path_initial]

    def add_path(self, path: List[BasicBlock]) -> None:
        self.paths.append(path)

    @property
    def all_bbs_in_paths(self) -> List[BasicBlock]:
        return [p for sublist in self.paths for p in sublist]


class MissingRekeyTo(AbstractDetector):

    NAME = "rekeyTo"
    DESCRIPTION = "Detect paths with a missing RekeyTo check"
    TYPE = DetectorType.STATEFULLGROUP

    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_TITLE = "Can Rekey Contract"
    WIKI_DESCRIPTION = "Detect paths with a missing RekeyTo check"
    WIKI_EXPLOIT_SCENARIO = """
Rekeying is an Algorand feature which enables an account holder to give authorization of their account to different address, whereby users can maintain a single static public address while updating the key controlling the assets.
Rekeying is done by using *rekey-to* transaction which is a payment transaction with `rekey-to` parameter set to new authorized address.

if a stateless contract, approves a payment transaction without checking the `rekey-to` parameter then one can set the authorization address to the contract account and withdraw funds directly bypassing all the checks.

Attacker creates a payment transaction using the contract with `rekey-to` set to their address. After rekeying, attacker transfer's the assets using their private key bypassing the conditions defined in the contract.
"""

    WIKI_RECOMMENDATION = """
Add a check in the contract code verifying that `RekeyTo` property of any transaction is set to `ZeroAddress`.
"""

    def check_rekey_to(  # pylint: disable=too-many-arguments
        self,
        bb: BasicBlock,
        group_tx: Dict[int, Set[BasicBlock]],
        idx_fitlered: Set[int],
        current_path: List[BasicBlock],
        all_results: Dict[str, Result],
    ) -> None:
        # check for loops
        if bb in current_path:
            return

        current_path = current_path + [bb]

        group_tx = copy(group_tx)
        for ins in bb.instructions:
            if isinstance(ins, Gtxn):
                if ins.idx not in idx_fitlered:
                    assert ins.bb
                    group_tx[ins.idx].add(ins.bb)

                if isinstance(ins.field, RekeyTo):
                    del group_tx[ins.idx]
                    idx_fitlered = set(idx_fitlered)
                    idx_fitlered.add(ins.idx)

            if isinstance(ins, Return) and group_tx:
                if len(ins.prev) == 1:
                    prev = ins.prev[0]
                    if isinstance(prev, Int) and prev.value == 0:
                        return

                for idx, bbs in group_tx.items():
                    bbs_list = sorted(bbs, key=lambda x: x.instructions[0].line)
                    filename = Path(f"rekeyto_tx_{idx}.dot")

                    if idx not in all_results:
                        all_results[str(idx)] = Result(filename, bbs_list + [bb], current_path)
                    else:
                        all_results[str(idx)].add_path(current_path)

        for next_bb in bb.next:
            self.check_rekey_to(next_bb, group_tx, idx_fitlered, current_path, all_results)

    def detect(self) -> List[str]:

        all_results: Dict[str, Result] = {}
        self.check_rekey_to(self.teal.bbs[0], defaultdict(set), set(), [], all_results)

        all_results_txt: List[str] = []
        for idx, res in all_results.items():
            description = f"Potential lack of RekeyTo check on transaction {idx}\n"
            description += f"\tFix the paths in {res.filename}\n"
            description += (
                "\tOr ensure it is used with stateless contracts that check for ReKeyTo\n"
            )
            all_results_txt.append(description)
            self.teal.bbs_to_dot(res.filename, res.all_bbs_in_paths)

        return all_results_txt
