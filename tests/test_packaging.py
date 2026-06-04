import ast
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_declares_modern_supported_python_and_launchers():
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text())

    project = metadata["project"]
    assert project["requires-python"] == ">=3.11,<3.14"
    assert "Programming Language :: Python :: 3.11" in project["classifiers"]
    assert "Programming Language :: Python :: 3.12" in project["classifiers"]
    assert "Programming Language :: Python :: 3.13" in project["classifiers"]

    script_files = metadata["tool"]["setuptools"]["script-files"]
    assert script_files == ["setoolkit", "seautomate", "seproxy", "seupdate"]


def test_runtime_dependencies_replace_pycrypto_with_pycryptodome():
    requirements = (ROOT / "requirements.txt").read_text().splitlines()
    normalized = {
        line.strip().lower()
        for line in requirements
        if line.strip() and not line.strip().startswith("#")
    }
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    dependencies = {dependency.lower() for dependency in pyproject["project"]["dependencies"]}

    assert "pycrypto" not in normalized
    assert "pycrypto" not in dependencies
    assert "pycryptodome" in normalized
    assert "pycryptodome" in dependencies


def test_setup_py_has_no_import_time_installer_side_effects():
    tree = ast.parse((ROOT / "setup.py").read_text())
    unsafe_calls = []

    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef)):
            continue
        if isinstance(node, ast.If) and _is_main_guard(node.test):
            continue
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                unsafe_calls.append(ast.unparse(child.func))

    assert unsafe_calls == []


def test_setup_py_imports_setuptools_only_for_packaging_commands():
    tree = ast.parse((ROOT / "setup.py").read_text())

    top_level_setuptools_imports = [
        node
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module == "setuptools"
    ]

    assert top_level_setuptools_imports == []


def _is_main_guard(node):
    return (
        isinstance(node, ast.Compare)
        and isinstance(node.left, ast.Name)
        and node.left.id == "__name__"
        and len(node.ops) == 1
        and isinstance(node.ops[0], ast.Eq)
        and len(node.comparators) == 1
        and isinstance(node.comparators[0], ast.Constant)
        and node.comparators[0].value == "__main__"
    )
