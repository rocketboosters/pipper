import semver


def explode(version_prefix: str) -> tuple:
    """
    Breaks apart a semantic version or partial semantic version string into
    its constituent elements and returns them as a tuple of strings. Any
    missing elements will be returned as empty strings.

    :param version_prefix:
        A semantic version or part of a semantic version, which can include
        wildcard characters.
    """
    sections: list[str] = []
    remainder = version_prefix.rstrip(".")
    for separator in ("+", "-"):
        parts = remainder.split(separator, 1)
        remainder = parts[0]
        section = parts[1] if len(parts) == 2 else ""
        sections.insert(0, section)

    parts = remainder.split(".")
    parts.extend(["", ""])
    sections = parts[:3] + sections

    return tuple(sections)


def serialize(version: str) -> str:
    """
    Converts the specified semantic version into a URL/filesystem safe
    version. If the version argument is not a valid semantic version a
    ValueError will be raised.
    """
    try:
        semver.VersionInfo.parse(version)
    except ValueError as error:
        raise ValueError(f'Invalid semantic version "{version}"') from error

    return serialize_prefix(version)


def serialize_prefix(version_prefix: str) -> str:
    """
    Serializes the specified prefix into a URL/filesystem safe version that
    can be used as a filename to store the versioned bundle.

    :param version_prefix:
        A partial or complete semantic version to be converted into its
        URL/filesystem equivalent.
    """
    if version_prefix.startswith("v"):
        return version_prefix

    sections = [part.replace(".", "_") for part in explode(version_prefix)]
    prefix = "-".join([section for section in sections[:3] if section])
    if sections[3]:
        prefix += f"__pre_{sections[3]}"
    if sections[4]:
        prefix += f"__build_{sections[4]}"

    return f"v{prefix}" if prefix else ""


def deserialize_prefix(safe_version_prefix: str) -> str:
    """
    Deserializes the specified prefix from a URL/filesystem safe version into
    its standard semantic version equivalent.

    :param safe_version_prefix:
        A partial or complete URL/filesystem safe version prefix to convert
        into a standard semantic version prefix.
    """
    if not safe_version_prefix.startswith("v"):
        return safe_version_prefix

    searches = [
        ("__build_", "split"),
        ("__pre_", "split"),
        ("-", "rsplit"),
        ("-", "rsplit"),
    ]

    sections: list[str] = []
    remainder = safe_version_prefix.strip("v").rstrip("_")
    for separator, operator in searches:
        parts = getattr(remainder, operator)(separator, 1)
        remainder = parts[0]
        section = parts[1] if len(parts) == 2 else ""
        sections.insert(0, section.replace("_", "."))
    sections.insert(0, remainder)

    prefix = ".".join([section for section in sections[:3] if section])
    if sections[3]:
        prefix += f"-{sections[3]}"
    if sections[4]:
        prefix += f"+{sections[4]}"

    return prefix


def deserialize(safe_version: str) -> str:
    """
    Converts the specified URL/filesystem safe version into a standard semantic
    version. If the converted output is not a valid semantic version a
    ValueError will be raised.
    """
    result = deserialize_prefix(safe_version)

    try:
        semver.VersionInfo.parse(result)
    except ValueError as error:
        raise ValueError(f'Invalid semantic version "{result}"') from error

    return result
