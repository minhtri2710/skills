import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from beo_utils import load_json

class CommandAdapter:
    def __init__(self, root: Path):
        self.root = root
        self.registry_path = root / "skills" / "beo" / "reference" / "registry" / "command-contracts.json"
        if not self.registry_path.exists():
            self.registry_path = Path(__file__).resolve().parents[1] / "registry" / "command-contracts.json"
        
        data = load_json(self.registry_path, {})
        commands_list = data.get("commands", []) if isinstance(data, dict) else []
        self.contracts = {}
        for cmd in commands_list:
            if isinstance(cmd, dict) and "command_id" in cmd:
                self.contracts[cmd["command_id"]] = cmd

    def build_argv(self, command_id: str, owner: str, **kwargs) -> list[str]:
        """Build argv from command contract template + kwargs."""
        contract = self.contracts.get(command_id)
        if not contract:
            raise ValueError(f"Unknown contracted command: {command_id}")
        if owner not in contract.get("owner_allow", []):
            raise ValueError(f"{owner} is not allowed to run {command_id}")

        argv_template = list(contract.get("argv") or [])
        optional = contract.get("optional_argv") or []
        if optional:
            optional_placeholders = set(re.findall(r"\{([^{}]+)\}", " ".join(str(a) for a in optional)))
            if optional_placeholders <= set(kwargs):
                argv_template.extend(optional)

        used: set[str] = set()
        argv = []
        for arg in argv_template:
            formatted_arg = str(arg)
            for key, val in kwargs.items():
                placeholder = "{" + str(key) + "}"
                if placeholder in formatted_arg:
                    formatted_arg = formatted_arg.replace(placeholder, str(val))
                    used.add(str(key))
            unresolved = re.findall(r"\{([^{}]+)\}", formatted_arg)
            if unresolved:
                raise ValueError(f"Unresolved placeholder(s) for {command_id}: {', '.join(sorted(unresolved))}")
            argv.append(formatted_arg)

        unused = sorted(set(str(k) for k in kwargs) - used)
        if unused:
            raise ValueError(f"Unused kwarg(s) for {command_id}: {', '.join(unused)}")
        return argv

    def check_authority(self, command_id: str, owner: str) -> bool:
        """Check if owner is allowed to run this command."""
        contract = self.contracts.get(command_id)
        if not contract:
            return False
        return owner in contract.get("owner_allow", [])
