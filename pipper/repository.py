import copy

from pipper import environment
from pipper.environment import Environment


def explode_credentials(credentials: list | None = None) -> dict:
    """..."""
    if not credentials or not len(credentials) > 2:
        return {}

    return {
        "access_key_id": credentials[0],
        "secret_access_key": credentials[1],
        "session_token": credentials[2] if len(credentials) > 1 else None,
    }


def add(env: Environment) -> dict:
    """..."""
    configs = environment.load_repositories()
    name = env.args.get("repository_profile_name")
    copy_from = env.args.get("repository_name")
    profile = env.args.get("aws_profile")
    credentials = explode_credentials(env.args.get("aws_credentials"))
    bucket = env.args.get("bucket")
    root_prefix = env.args.get("root_prefix")
    is_default = env.args.get("default")

    if name in configs["repositories"]:
        raise ValueError(
            f'The "{name}" repository configuration already exists. '
            "To make changes to an existing configuration use the modify "
            "repository action."
        )

    if copy_from and copy_from in configs["repositories"]:
        repo = copy.deepcopy(configs["repositories"][copy_from])
    else:
        repo = {
            "bucket": bucket,
            "profile": profile,
            "root_prefix": root_prefix or "pipper",
            "access_key_id": credentials.get("access_key_id"),
            "secret_access_key": credentials[1] if credentials else None,
            "session_token": credentials[2] if credentials else None,
        }

    configs["repositories"][name] = repo
    configs["default"] = name if is_default else configs["default"]

    result = environment.save_repositories(configs)

    print(f'[ADDED]: Created new "{name}" repository configuration')
    return result


def modify(env: Environment):
    """..."""
    configs = environment.load_repositories()
    name = env.args.get("repository_profile_name")
    existing = configs["repositories"].get(name)

    if not existing:
        raise ValueError(
            f'The "{name}" repository configuration does not exist. '
            "Use the add repository action instead to add this configuration"
        )

    copy_from = env.args.get("repository_name")
    profile = env.args.get("aws_profile")
    credentials = explode_credentials(env.args.get("aws_credentials"))
    bucket = env.args.get("bucket")
    root_prefix = env.args.get("root_prefix")
    is_default = env.args.get("default")

    if copy_from and copy_from in configs["repository"]:
        modified = copy.deepcopy(configs["repositories"][copy_from])
    else:
        creds = credentials or existing
        modified = {
            "bucket": bucket or existing["bucket"],
            "root_prefix": root_prefix or existing["root_prefix"] or "pipper",
            "profile": profile or existing["profile"],
            "access_key_id": creds["access_key_id"],
            "secret_access_key": creds["secret_access_key"],
            "session_token": creds["session_token"],
        }

    configs["repositories"][name] = modified
    configs["default"] = name if is_default else configs["default"]

    result = environment.save_repositories(configs)

    print(f'[MODIFIED]: "{name}" repository configuration changed')
    return result


def remove(env: Environment):
    """..."""
    name = env.args.get("repository_profile_name")
    configs = environment.load_repositories()

    if name in configs["repositories"]:
        repos = configs["repositories"]
        del repos[name]

        if configs["default"] == name:
            configs["default"] = None

        environment.save_repositories(configs)

    print(f'[REMOVED]: "{name}" configuration has been removed')
    return None


def repo_exists(env: Environment) -> bool:
    """..."""
    name = env.args.get("repository_profile_name")
    configs = environment.load_repositories()
    exists = name in configs["repositories"]

    if exists:
        print(f"[YES]: {name} does exist")
    else:
        print(f"[NO]: {name} does not exist")

    return exists


def list_repos():
    """..."""
    configs = environment.load_repositories()

    for name in configs["repositories"]:
        print(f"  * {name}")

    if configs["default"]:
        print("Default configuration is: {}".format(configs["default"]))


def run(env: Environment):
    """..."""
    action = env.args.get("repository_action")
    if action == "add":
        return add(env)
    elif action == "modify" or action == "remove":
        return modify(env)
    elif action == "list":
        return list_repos()
    elif action == "exists":
        return repo_exists(env)

    raise ValueError(f'Unknown repository action "{action}"')
