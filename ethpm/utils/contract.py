import re

from typing import (
    Any,
    Dict,
    Generator,
    List,
    Tuple,
)

from eth_utils import (
    to_bytes,
    to_dict,
    encode_hex,
)

from solc import compile_files

from web3 import Web3

from ethpm import V2_PACKAGES_DIR
from ethpm.exceptions import (
    InsufficientAssetsError,
    ValidationError,
)


def validate_minimal_contract_factory_data(contract_data: Dict[str, str]) -> None:
    """
    Validate that contract data in a package contains at least an "abi" and
    "deployment_bytecode" necessary to generate a deployable contract factory.
    """
    if not all(key in contract_data.keys() for key in ("abi", "deployment_bytecode")):
        raise InsufficientAssetsError(
            "Minimum required contract data to generate a deployable "
            "contract factory (abi & deployment_bytecode) not found."
        )


CONTRACT_NAME_REGEX = re.compile("^[a-zA-Z][-a-zA-Z0-9_]{0,255}$")


def validate_contract_name(name: str) -> None:
    if not CONTRACT_NAME_REGEX.match(name):
        raise ValidationError("Contract name: {0} is not valid.".format(name))


def validate_w3_instance(w3: Web3) -> None:
    if w3 is None or not isinstance(w3, Web3):
        raise ValueError("Package does not have valid web3 instance.")


@to_dict
def generate_contract_factory_kwargs(
        contract_data: Dict[str, Any]) -> Generator[Tuple[str, Any], None, None]:
    """
    Build a dictionary of kwargs to be passed into contract factory.
    """
    if "abi" in contract_data:
        yield "abi", contract_data["abi"]
    if "bytecode" in contract_data:
        bytecode = to_bytes(text=contract_data["bytecode"]["bytecode"])
        yield "bytecode", encode_hex(bytecode)
    if "runtime_bytecode" in contract_data:
        runtime_bytecode = to_bytes(text=contract_data["runtime_bytecode"]["bytecode"])
        yield "bytecode_runtime", encode_hex(runtime_bytecode)


def compile_contracts(contract_name: str, alias: str, paths: List[str]) -> str:
    '''
    Compile multiple contracts to bytecode.
    '''
    bin_id = '{0}.sol:{0}'.format(contract_name)
    contract_paths = [
        str(V2_PACKAGES_DIR / alias / path[1:])
        for path in paths
    ]
    compiled_source = compile_files(contract_paths)
    bin_lookup = str(V2_PACKAGES_DIR / alias / bin_id)
    compiled_source_bin = compiled_source[bin_lookup]['bin']
    return compiled_source_bin
