# The Social-Engineer Toolkit (SET)

The Social-Engineer Toolkit is an open-source penetration testing framework for authorized social-engineering assessments. SET provides guided attack vectors for security teams that need to test user awareness, validate controls, and run consent-based red-team exercises.

SET is a TrustedSec project written by David Kennedy (ReL1K) / @HackingDave.

## Responsible Use

SET is only for authorized testing where explicit permission and scope have been established. Do not use SET against systems, accounts, networks, or people without consent. Review the license in [readme/LICENSE](readme/LICENSE) before using or distributing SET.

## Supported Platforms

- Linux
- macOS, experimental
- Windows through WSL/WSL2 Kali or another supported Linux environment

SET 8.1.3 targets Python 3.11 through Python 3.13.

## Installation

### Kali Linux / WSL

```bash
sudo apt update
sudo apt install set -y
```

### From Source

```bash
git clone https://github.com/trustedsec/social-engineer-toolkit/ setoolkit/
cd setoolkit
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

For the legacy system-wide layout, run the installer with elevated privileges:

```bash
sudo python3 setup.py
```

The legacy installer copies SET to `/usr/local/share/setoolkit`, writes `/etc/setoolkit/set.config`, and creates `/usr/local/bin/setoolkit`.

## Usage

Launch the interactive console:

```bash
sudo setoolkit
```

From a source checkout, you can also run:

```bash
sudo ./setoolkit
```

The full user manual is available at [readme/User_Manual.pdf](https://github.com/trustedsec/social-engineer-toolkit/raw/master/readme/User_Manual.pdf).

## Development

```bash
python -m pip install -e .
python -m pip install pytest
python -m compileall -q .
pytest -q
```

## Security Reports

Please report vulnerabilities through the process in [SECURITY.md](SECURITY.md). Do not open public issues for exploitable vulnerabilities.

## Bugs and Enhancements

For non-sensitive bug reports or enhancement requests, open an issue at https://github.com/trustedsec/social-engineer-toolkit/issues with SET version, platform, Python version, and reproduction steps.
