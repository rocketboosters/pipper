from pipper import versioning


def test_make_s3_key():
    """Should convert package name and version to an associated S3 key."""
    name = "fake-package"
    version = "1.2.3-alpha.1+2-tests"
    key = versioning.make_s3_key(name, version)
    remote = versioning.RemoteVersion("FAKE", key)

    assert key.endswith(".pipper"), "Expected a pipper file key."
    assert key.find(f"/{name}/"), "Expected the package name as a folder."
    assert name == remote.package_name
    assert version == remote.version
    assert key.endswith(f"{remote.safe_version}.pipper"), """
        Expected the key to end with the safe version as the file name.
        """


def test_to_remote_version():
    """Should convert the package information into a RemoteVersion object."""
    name = "fake-package"
    version = "1.2.3"
    bucket = "FAKE"
    remote = versioning.to_remote_version(name, version, bucket)
    assert version == remote.version
    assert remote.safe_version == "v1-2-3"
    assert name == remote.package_name
    assert f"pipper/{name}/v1-2-3.pipper" == remote.key
    assert remote.filename == "v1-2-3.pipper"
    assert remote == remote, "Should be equal to itself when compared"


def test_remote_sorting():
    """Should sort remote packages correctly according to version."""
    remotes = [
        versioning.to_remote_version("f", "1.0.1", "FAKE"),
        versioning.to_remote_version("a", "0.1.0", "FAKE"),
        versioning.to_remote_version("c", "0.1.1-alpha.2+1-tests", "FAKE"),
        versioning.to_remote_version("d", "0.1.1-alpha.2+2-tests", "FAKE"),
        versioning.to_remote_version("e", "0.1.1-alpha.2", "FAKE"),
        versioning.to_remote_version("b", "0.1.1-alpha.1", "FAKE"),
    ]
    result = sorted(remotes)
    comparison = sorted(remotes, key=lambda r: r.package_name)
    assert comparison == result, """
        Expected the RemoteVersions to be sorted by version such that their
        package names are sorted alphabetically.
        """
