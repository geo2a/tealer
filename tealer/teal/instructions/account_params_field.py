# pylint: disable=too-few-public-methods

# https://developer.algorand.org/docs/get-details/dapps/avm/teal/opcodes/#acct_params_get-f


class AccountParamsField:
    pass


class AcctBalance(AccountParamsField):
    def __str__(self) -> str:
        return "AcctBalance"


class AcctMinBalance(AccountParamsField):
    def __str__(self) -> str:
        return "AcctMinBalance"


class AcctAuthAddr(AccountParamsField):
    def __str__(self) -> str:
        return "AcctAuthAddr"
