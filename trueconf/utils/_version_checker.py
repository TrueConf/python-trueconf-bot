from dataclasses import dataclass
from importlib import metadata
from packaging.specifiers import SpecifierSet
from packaging.version import Version


@dataclass(frozen=True)
class CompatibilityRule:
    server_spec: SpecifierSet
    library_spec: SpecifierSet | None
    message: str
    install_hint: str | None = None


class _VersionChecker:
    PACKAGE_NAME = "python-trueconf-bot"

    RULES: tuple[CompatibilityRule, ...] = (
        CompatibilityRule(
            server_spec=SpecifierSet("<5.5.0"),
            library_spec=None,
            message="Chatbots are not supported (server version 5.5.0+ required).",
        ),
    )

    @classmethod
    def check(cls, server_version: str) -> None:
        parsed_server_version = Version(server_version)
        library_version = Version(metadata.version(cls.PACKAGE_NAME))

        rule = cls._find_rule(parsed_server_version)
        if rule is None:
            return

        if rule.library_spec is None:
            raise RuntimeError(
                f"Error: Server version {server_version} is too old. "
                f"{rule.message}"
            )

        if library_version not in rule.library_spec:
            hint = f"\nRun: {rule.install_hint}" if rule.install_hint else ""
            raise RuntimeError(
                f"\n[!] Server version {server_version} is incompatible with "
                f"installed library version {library_version}.\n"
                f"{rule.message}{hint}"
            )

    @classmethod
    def _find_rule(cls, server_version: Version) -> CompatibilityRule | None:
        for rule in cls.RULES:
            if server_version in rule.server_spec:
                return rule
        return None