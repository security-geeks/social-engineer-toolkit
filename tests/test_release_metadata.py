from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_release_version_is_consistent():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    set_version = (ROOT / "src/core/set.version").read_text().strip()

    assert pyproject["project"]["version"] == "8.1.3"
    assert set_version == "8.1.3"


def test_ci_targets_supported_python_versions():
    workflow = (ROOT / ".github/workflows/Python_tests.yml").read_text()

    assert "python-version: [\"3.11\", \"3.12\", \"3.13\"]" in workflow
    assert "actions/checkout@v4" in workflow
    assert "actions/setup-python@v5" in workflow
    assert "pytest -q" in workflow
