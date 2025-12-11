"""
Mobile Development Tools Integration

Provides integration configurations for mobile development tools:
- Warp: Modern terminal for teams
- Shellfish: SSH client for iOS
- Working Copy: Git client for iOS
- Pyto: Python IDE for iOS
- a]Shell: Terminal for iOS
- iSH: Alpine Linux shell for iOS
"""

import os
import json
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Mobile/desktop platforms."""
    IOS = "ios"
    IPADOS = "ipados"
    MACOS = "macos"
    ANDROID = "android"
    LINUX = "linux"
    WINDOWS = "windows"
    CROSS_PLATFORM = "cross-platform"


@dataclass
class MobileToolConfig:
    """Configuration for a mobile development tool."""
    name: str
    platform: list[Platform]
    app_store_url: Optional[str]
    website_url: str
    description: str
    capabilities: list[str]
    config_format: str  # json, plist, ssh_config, etc.
    default_config: dict = field(default_factory=dict)


# Supported mobile development tools
MOBILE_TOOLS: dict[str, MobileToolConfig] = {
    "warp": MobileToolConfig(
        name="Warp Terminal",
        platform=[Platform.MACOS, Platform.LINUX],
        app_store_url=None,
        website_url="https://www.warp.dev",
        description="Modern GPU-accelerated terminal with AI features",
        capabilities=["terminal", "ssh", "ai-assist", "team-collaboration"],
        config_format="yaml",
        default_config={
            "theme": "dark",
            "font_size": 14,
            "cursor_style": "block",
            "scrollback_lines": 10000,
            "enable_ai": True,
        },
    ),
    "shellfish": MobileToolConfig(
        name="Shellfish",
        platform=[Platform.IOS, Platform.IPADOS],
        app_store_url="https://apps.apple.com/app/shellfish-ssh/id1336634154",
        website_url="https://secureshellfish.app",
        description="Professional SSH client for iOS with file management",
        capabilities=["ssh", "sftp", "mosh", "port-forwarding", "files-integration"],
        config_format="ssh_config",
        default_config={
            "ServerAliveInterval": 60,
            "ServerAliveCountMax": 3,
            "StrictHostKeyChecking": "ask",
            "AddKeysToAgent": "yes",
        },
    ),
    "working-copy": MobileToolConfig(
        name="Working Copy",
        platform=[Platform.IOS, Platform.IPADOS],
        app_store_url="https://apps.apple.com/app/working-copy-git-client/id896694807",
        website_url="https://workingcopy.app",
        description="Full-featured Git client for iOS",
        capabilities=["git", "github", "gitlab", "bitbucket", "code-editing", "preview"],
        config_format="plist",
        default_config={
            "default_branch": "main",
            "auto_fetch": True,
            "show_line_numbers": True,
            "syntax_highlighting": True,
            "dark_mode": "system",
        },
    ),
    "pyto": MobileToolConfig(
        name="Pyto",
        platform=[Platform.IOS, Platform.IPADOS],
        app_store_url="https://apps.apple.com/app/pyto-python-3/id1436650069",
        website_url="https://pyto.app",
        description="Python 3 IDE for iOS with full library support",
        capabilities=["python", "pip", "jupyter", "numpy", "pandas", "matplotlib", "shortcuts"],
        config_format="json",
        default_config={
            "python_version": "3.11",
            "auto_complete": True,
            "line_numbers": True,
            "tab_size": 4,
            "use_spaces": True,
            "theme": "one-dark",
        },
    ),
    "a-shell": MobileToolConfig(
        name="a-Shell",
        platform=[Platform.IOS, Platform.IPADOS],
        app_store_url="https://apps.apple.com/app/a-shell/id1473805438",
        website_url="https://holzschu.github.io/a-Shell_iOS/",
        description="Unix shell for iOS with many command-line tools",
        capabilities=["shell", "python", "lua", "tex", "git", "ssh", "vim", "clang"],
        config_format="shell",
        default_config={
            "TERM": "xterm-256color",
            "EDITOR": "vim",
            "PAGER": "less",
        },
    ),
    "ish": MobileToolConfig(
        name="iSH",
        platform=[Platform.IOS, Platform.IPADOS],
        app_store_url="https://apps.apple.com/app/ish-shell/id1436902243",
        website_url="https://ish.app",
        description="Alpine Linux shell for iOS",
        capabilities=["linux", "alpine", "apk", "shell", "ssh"],
        config_format="shell",
        default_config={
            "TERM": "xterm",
            "SHELL": "/bin/ash",
        },
    ),
    "blink-shell": MobileToolConfig(
        name="Blink Shell",
        platform=[Platform.IOS, Platform.IPADOS],
        app_store_url="https://apps.apple.com/app/blink-shell-mosh-ssh/id1594898306",
        website_url="https://blink.sh",
        description="Professional SSH and Mosh terminal",
        capabilities=["ssh", "mosh", "terminal", "code-server", "files"],
        config_format="ssh_config",
        default_config={
            "ServerAliveInterval": 60,
            "Mosh": True,
            "SyncKeys": True,
        },
    ),
    "termius": MobileToolConfig(
        name="Termius",
        platform=[Platform.IOS, Platform.IPADOS, Platform.MACOS, Platform.ANDROID, Platform.LINUX, Platform.WINDOWS],
        app_store_url="https://apps.apple.com/app/termius-ssh-client/id549039908",
        website_url="https://termius.com",
        description="Cross-platform SSH client with team features",
        capabilities=["ssh", "sftp", "port-forwarding", "team-sync", "snippets"],
        config_format="json",
        default_config={
            "theme": "dark",
            "font_size": 14,
            "bell": False,
            "scrollback": 10000,
        },
    ),
}


class MobileDevIntegration:
    """
    Integration manager for mobile development tools.

    Provides configuration generation and connection helpers.
    """

    def __init__(self):
        self.tools = MOBILE_TOOLS

    def get_tool(self, tool_name: str) -> Optional[MobileToolConfig]:
        """Get a tool configuration by name."""
        return self.tools.get(tool_name.lower().replace(" ", "-"))

    def list_tools(
        self,
        platform: Optional[Platform] = None,
        capability: Optional[str] = None,
    ) -> list[MobileToolConfig]:
        """
        List available tools with optional filtering.

        Args:
            platform: Filter by platform
            capability: Filter by capability

        Returns:
            List of matching tools
        """
        tools = []
        for tool in self.tools.values():
            if platform and platform not in tool.platform:
                continue
            if capability and capability not in tool.capabilities:
                continue
            tools.append(tool)
        return tools

    def generate_ssh_config(
        self,
        host_alias: str,
        hostname: str,
        user: str,
        port: int = 22,
        identity_file: Optional[str] = None,
        extra_options: Optional[dict] = None,
    ) -> str:
        """
        Generate SSH config entry for mobile SSH clients.

        Args:
            host_alias: Alias for the host
            hostname: Actual hostname or IP
            user: SSH username
            port: SSH port
            identity_file: Path to identity file
            extra_options: Additional SSH options

        Returns:
            SSH config block as string
        """
        config_lines = [
            f"Host {host_alias}",
            f"    HostName {hostname}",
            f"    User {user}",
            f"    Port {port}",
        ]

        if identity_file:
            config_lines.append(f"    IdentityFile {identity_file}")

        # Add sensible defaults for mobile
        config_lines.extend([
            "    ServerAliveInterval 60",
            "    ServerAliveCountMax 3",
            "    TCPKeepAlive yes",
            "    StrictHostKeyChecking ask",
        ])

        if extra_options:
            for key, value in extra_options.items():
                config_lines.append(f"    {key} {value}")

        return "\n".join(config_lines)

    def generate_working_copy_remote(
        self,
        repo_url: str,
        name: Optional[str] = None,
        branch: str = "main",
    ) -> dict:
        """
        Generate Working Copy repository configuration.

        Args:
            repo_url: Git repository URL
            name: Display name for the repo
            branch: Default branch

        Returns:
            Configuration dict for Working Copy
        """
        # Parse repo URL to get name if not provided
        if not name:
            name = repo_url.split("/")[-1].replace(".git", "")

        return {
            "name": name,
            "remote_url": repo_url,
            "default_branch": branch,
            "fetch_on_open": True,
            "push_on_commit": False,
        }

    def generate_pyto_requirements(
        self,
        packages: list[str],
        include_common: bool = True,
    ) -> str:
        """
        Generate requirements.txt for Pyto.

        Args:
            packages: List of packages to include
            include_common: Include commonly used packages

        Returns:
            Requirements.txt content
        """
        common_packages = [
            "requests",
            "httpx",
            "pydantic",
            "python-dotenv",
        ]

        if include_common:
            all_packages = list(set(common_packages + packages))
        else:
            all_packages = packages

        return "\n".join(sorted(all_packages))

    def generate_a_shell_profile(
        self,
        aliases: Optional[dict] = None,
        env_vars: Optional[dict] = None,
        startup_commands: Optional[list] = None,
    ) -> str:
        """
        Generate shell profile for a-Shell or iSH.

        Args:
            aliases: Shell aliases
            env_vars: Environment variables
            startup_commands: Commands to run at startup

        Returns:
            Shell profile content
        """
        lines = [
            "# BlackRoad shell profile",
            "",
            "# Environment variables",
            'export TERM="xterm-256color"',
            'export EDITOR="vim"',
            'export PAGER="less"',
            'export LANG="en_US.UTF-8"',
        ]

        if env_vars:
            for key, value in env_vars.items():
                lines.append(f'export {key}="{value}"')

        lines.extend(["", "# Aliases"])

        default_aliases = {
            "ll": "ls -la",
            "la": "ls -A",
            "l": "ls -CF",
            "..": "cd ..",
            "...": "cd ../..",
            "grep": "grep --color=auto",
        }

        if aliases:
            default_aliases.update(aliases)

        for alias, command in default_aliases.items():
            lines.append(f'alias {alias}="{command}"')

        if startup_commands:
            lines.extend(["", "# Startup commands"])
            lines.extend(startup_commands)

        return "\n".join(lines)

    def generate_warp_workflow(
        self,
        name: str,
        commands: list[str],
        description: Optional[str] = None,
    ) -> dict:
        """
        Generate a Warp workflow configuration.

        Args:
            name: Workflow name
            commands: List of commands
            description: Workflow description

        Returns:
            Workflow configuration dict
        """
        return {
            "name": name,
            "description": description or f"Workflow: {name}",
            "commands": [
                {"command": cmd, "name": cmd.split()[0]}
                for cmd in commands
            ],
        }

    def get_connection_urls(self, hostname: str, port: int = 22) -> dict:
        """
        Generate connection URLs for various mobile tools.

        Args:
            hostname: Server hostname
            port: SSH port

        Returns:
            Dict of tool names to connection URLs
        """
        return {
            "shellfish": f"ssh://{hostname}:{port}",
            "termius": f"ssh://{hostname}:{port}",
            "blink": f"ssh://{hostname}:{port}",
            "working_copy_ssh": f"ssh://{hostname}:{port}",
        }

    def generate_mosh_command(
        self,
        hostname: str,
        user: str,
        port: int = 22,
    ) -> str:
        """
        Generate Mosh connection command for mobile terminals.

        Args:
            hostname: Server hostname
            user: SSH username
            port: SSH port

        Returns:
            Mosh command string
        """
        return f"mosh --ssh='ssh -p {port}' {user}@{hostname}"


def generate_mobile_deploy_config(
    api_url: str,
    api_key: Optional[str] = None,
) -> dict:
    """
    Generate configuration for mobile app deployment access.

    Args:
        api_url: API base URL
        api_key: Optional API key

    Returns:
        Configuration dict for mobile apps
    """
    config = {
        "api": {
            "base_url": api_url,
            "version": "v1",
            "timeout": 30,
        },
        "endpoints": {
            "health": "/health",
            "agents": "/v1/agents",
            "packs": "/v1/packs",
        },
        "mobile": {
            "offline_mode": True,
            "cache_ttl": 300,
            "sync_on_wifi_only": False,
        },
    }

    if api_key:
        config["api"]["headers"] = {
            "Authorization": f"Bearer {api_key}",
        }

    return config
