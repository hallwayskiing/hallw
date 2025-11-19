# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

Please report (suspected) security vulnerabilities to **ethannie88@gmail.com**. You will receive a response within 48 hours. If the issue is confirmed, we will release a patch as soon as possible depending on complexity but historically within a few days.

### What to Report

Please report any security vulnerabilities that could affect users, including but not limited to:

- **Authentication/Authorization flaws**: Issues with API key handling or validation
- **Code execution vulnerabilities**: Remote code execution or arbitrary command execution
- **Information disclosure**: Leakage of sensitive data, credentials, or file system access
- **Injection attacks**: SQL injection, command injection, or other injection vulnerabilities
- **Cross-Site Scripting (XSS)**: While HALLW is primarily a CLI tool, report if discovered
- **Improper input validation**: Buffer overflows, path traversal, or other input validation issues
- **Denial of Service**: Issues that could cause the agent to crash or become unresponsive

### What NOT to Report

The following are considered acceptable behaviors or low-risk issues:

- Missing security headers in HTTP responses (browser automation only)
- Rate limiting (no rate limiting is implemented by design)
- Missing security.txt files
- Disclosure of version numbers or dependency versions
- Issues that require physical access to the machine
- Issues that require extensive user interaction
- Social engineering attacks
- Issues in third-party dependencies (please report to the upstream project)

## Security Considerations

### API Key Management

- **Never commit API keys** to version control
- Use environment variables or secure secret management
- Rotate API keys regularly
- Use the `.env` file (which is gitignored) for local development

### Browser Automation

- HALLW can control your browser and access websites on your behalf
- Only run tasks from trusted sources
- Review agent actions when automating sensitive operations
- Use headless mode in production if possible

### File System Access

- HALLW can read and write files on your system
- Be cautious when allowing file operations in untrusted directories
- Review file paths in agent tasks before execution
- Use `FILE_BASE_DIR` to restrict file operations to specific directories

### Network Security

- The agent makes network requests to LLM APIs and websites
- Ensure API endpoints are from trusted sources
- Be aware that browser automation can expose your IP and browser fingerprint
- Consider using VPN or proxy for sensitive operations

### Best Practices

1. **Sandboxing**: Consider running HALLW in isolated environments (containers, VMs)
2. **Monitoring**: Monitor agent actions and API usage
3. **Access Control**: Limit file system and network access when possible
4. **Updates**: Keep HALLW and dependencies up to date
5. **Audit Logs**: Review logs regularly for suspicious activities

## Security Updates

Security updates will be:

1. Released as patch versions (e.g., 0.1.1, 0.1.2)
2. Documented in the CHANGELOG.md
3. Announced via GitHub releases
4. Tagged with `security` label in issues

## Disclosure Policy

We follow a coordinated disclosure process:

1. **Private reporting**: Vulnerabilities are reported privately via email
2. **Investigation**: We investigate and confirm the vulnerability
3. **Fix development**: We develop and test a fix
4. **Disclosure**: After a fix is released, we disclose the vulnerability publicly
5. **Credit**: We credit researchers who responsibly disclose vulnerabilities (if desired)

## Contact

For security issues, please email: **ethannie88@gmail.com**

For general questions or non-security issues, please use [GitHub Issues](https://github.com/hallwayskiing/hallw/issues).

Thank you for helping keep HALLW and its users safe!
