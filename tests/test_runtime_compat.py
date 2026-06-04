import ast
import builtins
from pathlib import Path

import src.core.setcore as setcore


ROOT = Path(__file__).resolve().parents[1]


def test_setcore_installs_raw_input_alias_for_python3_modules():
    assert setcore.raw_input is input
    assert builtins.raw_input is input


def test_harvester_uses_socketserver_alias_for_ssl_server():
    tree = ast.parse((ROOT / "src/webattack/harvester/harvester.py").read_text())

    imported_socketserver_aliases = {
        alias.asname
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
        if alias.name == "socketserver"
    }
    assert "socketserver" not in _attribute_roots(tree, "BaseServer")
    assert "ss" in imported_socketserver_aliases
    assert "ss" in _attribute_roots(tree, "BaseServer")


def test_harvester_uses_html_escape_directly():
    tree = ast.parse((ROOT / "src/webattack/harvester/harvester.py").read_text())

    cgi_escape_imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "cgi"
        and any(alias.name == "escape" for alias in node.names)
    ]
    html_escape_imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "html"
        and any(alias.name == "escape" for alias in node.names)
    ]

    assert cgi_escape_imports == []
    assert html_escape_imports


def test_setcore_user_messages_reference_pycryptodome():
    source = (ROOT / "src/core/setcore.py").read_text()

    assert "python-pycrypto" not in source
    assert "pycryptodome" in source


def _attribute_roots(tree, attribute_name):
    return {
        node.value.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and node.attr == attribute_name
        and isinstance(node.value, ast.Name)
    }
