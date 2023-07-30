from typing import Any, Dict


def deep_merge(orig_dict: Dict[str, Any], new_dict: Dict[str, Any]) -> Dict[str, Any]:
    for key, val in new_dict.items():
        if isinstance(val, dict):
            tmp = deep_merge(orig_dict.get(key, {}), val)
            orig_dict[key] = tmp

        elif isinstance(val, list):
            orig_dict[key] = (orig_dict.get(key, []) + val)

        else:
            orig_dict[key] = new_dict[key]

    return orig_dict
