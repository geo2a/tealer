from tealer.teal.instructions.account_params_field import (
    AccountParamsField,
    AcctBalance,
    AcctMinBalance,
    AcctAuthAddr,
)

ACCOUNT_PARAMS_FIELD_TXT_TO_OBJECT = {
    "AcctBalance": AcctBalance,
    "AcctMinBalance": AcctMinBalance,
    "AcctAuthAddr": AcctAuthAddr,
}


def parse_account_params_field(field: str) -> AccountParamsField:
    return ACCOUNT_PARAMS_FIELD_TXT_TO_OBJECT[field]()
