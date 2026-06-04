# Security Policy

## Supported Versions

Security fixes are provided for the current released version of SET. Older releases may receive fixes at maintainer discretion when the impact and patch risk justify it.

| Version | Supported |
| ------- | --------- |
| 8.1.x   | Yes       |
| < 8.1   | No        |

## Reporting A Vulnerability

Do not open a public GitHub issue for exploitable vulnerabilities.

Report security concerns through TrustedSec's normal vulnerability disclosure channels or contact the maintainers privately with:

- Affected version and commit
- Platform and Python version
- Clear reproduction steps
- Expected impact
- Any proof-of-concept material needed to validate the issue

The project will acknowledge valid reports as maintainers are available, triage impact, and coordinate a fix or disclosure path when appropriate.

## Scope

Reports should focus on vulnerabilities in SET itself, including unintended code execution, path traversal, unsafe file handling, credential disclosure beyond intended local operator output, dependency risks, or bypasses of safety checks.

Requests to recover or obtain passwords, access third-party accounts, or attack systems without authorization are not valid security reports and will be closed.
