# Personal AI Employee - Security

## Table of Contents

1. [Overview](#overview)
2. [Security Principles](#security-principles)
3. [Credential Management](#credential-management)
4. [Data Protection](#data-protection)
5. [Network Security](#network-security)
6. [Access Control](#access-control)
7. [Audit Logging](#audit-logging)
8. [Threat Model](#threat-model)
9. [Best Practices](#best-practices)
10. [Incident Response](#incident-response)

---

## Overview

The Personal AI Employee is designed with **security-first** principles. This document outlines the security architecture, potential threats, and best practices for secure operation.

**Key Security Features**:
- ✅ Local-first architecture (data never leaves your control)
- ✅ OAuth2 for external service authentication
- ✅ Credential isolation in `config/` directory
- ✅ Comprehensive audit logging
- ✅ Human-in-the-loop approval workflows
- ✅ No hardcoded credentials
- ✅ Environment variable isolation

---

## Security Principles

### 1. Local-First Architecture

**Principle**: All data stored locally, no cloud dependencies.

**Implementation**:
- Obsidian vault stored on local filesystem
- Credentials stored in `config/` (gitignored)
- Logs stored locally in `Logs/`
- No data sent to external servers (except API calls)

**Benefits**:
- Full data ownership
- Privacy by design
- Works offline (except API calls)
- No vendor lock-in

### 2. Credential Isolation

**Principle**: Credentials isolated from code and git.

**Implementation**:
```bash
config/
├── client_secret.json         # Google OAuth (gitignored)
├── .xero_credentials.json     # Xero tokens (gitignored)
├── .env                       # Environment variables (gitignored)
└── *.session                  # Browser sessions (gitignored)
```

**Benefits**:
- Credentials never committed to git
- Centralized credential management
- Easy to rotate credentials
- Audit trail for credential usage

### 3. Human-in-the-Loop

**Principle**: All sensitive actions require human approval.

**Implementation**:
- Social media posts require approval
- Email sends require approval
- Payment actions require approval
- File deletions require approval

**Benefits**:
- Prevents accidental actions
- Builds trust in system
- Allows review before execution
- No "rogue AI" scenarios

### 4. Least Privilege

**Principle**: Components only have access to what they need.

**Implementation**:
- OAuth2 scopes limited to required permissions
- File system access restricted to vault
- Network access limited to required APIs
- PM2 processes run with minimal permissions

**Benefits**:
- Reduced blast radius
- Limits potential damage
- Compliance with best practices

---

## Credential Management

### OAuth2 Credentials

**Google (Gmail, Calendar)**:
```python
# Stored in: config/client_secret.json
{
  "installed": {
    "client_id": "...",
    "client_secret": "...",
    "redirect_uris": ["http://localhost:8080"]
  }
}
```

**Token Storage**:
```python
# Tokens stored in: config/.gmail_token.json
{
  "token": "...",
  "refresh_token": "...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "...",
  "client_secret": "...",
  "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
}
```

**Security Measures**:
1. **Read-only scopes** where possible
2. **Token auto-refresh** (no manual intervention)
3. **Token encryption** (future enhancement)
4. **Token rotation** (recommended every 90 days)

### Browser Session Credentials

**CDP (Chrome DevTools Protocol)**:
```bash
# Chrome started with:
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug"
```

**Security Measures**:
1. **Port 9222 localhost only** (not exposed to network)
2. **User data directory isolated**
3. **No credentials stored in code**
4. **Session persistence** (uses existing login)

**Recommendations**:
- Keep Chrome updated
- Use dedicated Chrome profile for automation
- Lock computer when not in use
- Monitor CDP port for unauthorized access

### Environment Variables

**Sensitive Configuration**:
```bash
# Stored in: config/.env (gitignored)
XERO_API_KEY=secret_key_here
XERO_API_SECRET=secret_secret_here
ENCRYPTION_KEY=encryption_key_here
```

**Security Measures**:
1. **Never commit .env to git**
2. **Use strong, unique values**
3. **Rotate keys periodically**
4. **Limit .env file permissions**

---

## Data Protection

### Data at Rest

**Obsidian Vault**:
- Stored on local filesystem
- Protected by OS user permissions
- Optional: Full disk encryption (BitLocker/FileVault)

**Logs**:
- Stored in `Logs/YYYY-MM-DD.json`
- JSON format for structured querying
- Contains timestamps, actions, results
- Recommended: Encrypt sensitive logs

**Credentials**:
- Isolated in `config/` directory
- Gitignored to prevent accidental commits
- Recommended: Encrypt credential files

### Data in Transit

**API Calls**:
- All HTTPS/TLS encrypted
- Certificate verification enabled
- No HTTP (unencrypted) connections

**CDP Connection**:
- Localhost only (127.0.0.1)
- Not exposed to network
- No encryption required (local)

**Recommendations**:
- Use VPN on public networks
- Verify HTTPS certificates
- Monitor for unusual traffic

### Data Retention

**Logs**:
- Retention: 90 days (configurable)
- Automatic cleanup via cron job
- Archive option available

**Vault**:
- Indefinite retention
- User responsible for cleanup
- Archive old items to `Archive/`

---

## Network Security

### Allowed Outbound Connections

**Services**:
```
accounts.google.com          # Google OAuth
gmail.googleapis.com         # Gmail API
www.googleapis.com           # Google Calendar API
api.xero.com                # Xero API
web.whatsapp.com            # WhatsApp Web
business.facebook.com       # Meta Business Suite
twitter.com or X.com        # Twitter/X
linkedin.com                # LinkedIn
```

**Firewall Rules** (if applicable):
```bash
# Allow outbound HTTPS
ufw allow out 443/tcp

# Allow local CDP
ufw allow from 127.0.0.1 to any port 9222

# Deny inbound connections (except SSH)
ufw default deny incoming
```

### CDP Security

**Chrome DevTools Protocol**:
- **Port**: 9222
- **Binding**: 127.0.0.1 (localhost only)
- **Exposure**: NOT exposed to network

**Verification**:
```bash
# Check if port is exposed
netstat -ano | findstr :9222

# Should show:
# TCP    127.0.0.1:9222    0.0.0.0:0    LISTENING
```

**Warning Signs**:
- Port bound to 0.0.0.0 (all interfaces)
- External connections to port 9222
- Unknown processes on port 9222

---

## Access Control

### File System Permissions

**Recommended Permissions**:
```bash
# Vault directory
chmod 700 ~/PERSONAL_AI_EMPLOYEE

# Config directory (credentials)
chmod 700 config/
chmod 600 config/*.json
chmod 600 config/.env

# Scripts (read-only for others)
chmod 755 scripts/
chmod 644 scripts/*.py

# Logs
chmod 700 Logs/
chmod 600 Logs/*.json
```

**Windows**:
```powershell
# Use NTFS permissions
icacls "PERSONAL_AI_EMPLOYEE" /grant:r "$($env:USERNAME):(OI)(CI)F"
icacls "config" /inheritance:r
icacls "config" /grant "$($env:USERNAME):F"
```

### PM2 Process Permissions

**Run as non-root user**:
```bash
# Create dedicated user
useradd -m -s /bin/bash ai-employee

# Run PM2 as ai-employee
su - ai-employee
pm2 start process-manager/pm2.config.js
```

**Windows**: Run as standard user (not Administrator)

### OS User Accounts

**Recommendations**:
- Use dedicated user account for AI Employee
- Don't use admin/root account
- Enable screen lock
- Use strong password

---

## Audit Logging

### Log Format

**All actions logged**:
```json
{
  "timestamp": "2026-01-11T18:00:00Z",
  "component": "twitter_approval_monitor",
  "action": "twitter_post_published",
  "details": {
    "file": "TWITTER_POST_20260111_180000.md",
    "content_length": 240,
    "timestamp": "2026-01-11T18:00:15Z",
    "result": "success"
  }
}
```

### Log Locations

```
Logs/
├── 2026-01-01.json
├── 2026-01-02.json
└── ...
```

### Log Analysis

**Review logs regularly**:
```bash
# Find all actions today
cat Logs/$(date +%Y-%m-%d).json | jq '.action'

# Find failed actions
cat Logs/*.json | jq 'select(.details.result == "failed")'

# Find all posts
cat Logs/*.json | jq 'select(.action | contains("post"))'
```

### Log Retention

**Default**: 90 days
**Cleanup**: Automated via cron job
**Archive**: Optional (move to Archive/)

---

## Threat Model

### Potential Threats

| Threat | Likelihood | Impact | Mitigation |
|--------|-----------|--------|------------|
| Unauthorized access to vault | Medium | High | File permissions, encryption |
| Credential theft | Low | High | Isolation, rotation |
| Social media account compromise | Low | Medium | 2FA, strong passwords |
| Malicious code execution | Low | High | Approval workflow, code review |
| Data exfiltration | Low | High | Local-only, no cloud sync |
| Rogue AI actions | Very Low | High | Human-in-the-loop, dry-run mode |

### Attack Vectors

**Vector 1: Stolen Laptop**
- **Risk**: Vault and credentials exposed
- **Mitigation**: Full disk encryption, strong password

**Vector 2: Compromised OAuth Token**
- **Risk**: Unauthorized API access
- **Mitigation**: Token auto-refresh, scope limitation

**Vector 3: Malicious Script**
- **Risk**: Unauthorized actions
- **Mitigation**: Approval workflow, code review

**Vector 4: Network Interception**
- **Risk**: Credentials intercepted
- **Mitigation**: HTTPS/TLS, VPN on public networks

**Vector 5: CDP Port Exposure**
- **Risk**: Browser control
- **Mitigation**: Localhost binding only, firewall

---

## Best Practices

### Development

1. **Never hardcode credentials**
2. **Use environment variables for secrets**
3. **Implement dry-run mode**
4. **Add input validation**
5. **Sanitize file paths**
6. **Use parameterized queries** (if database)

### Deployment

1. **Run as non-root user**
2. **Use firewall to restrict ports**
3. **Enable OS updates**
4. **Monitor logs regularly**
5. **Backup vault frequently**
6. **Test security controls**

### Operations

1. **Review logs daily**
2. **Rotate credentials quarterly**
3. **Update dependencies monthly**
4. **Audit file permissions**
5. **Test backup restoration**
6. **Monitor for unusual activity**

### Incident Response

**If credentials are compromised**:
1. Revoke OAuth tokens immediately
2. Rotate all credentials
3. Review audit logs for suspicious activity
4. Change all passwords
5. Enable 2FA on all accounts

**If system behaves unexpectedly**:
1. Stop all PM2 processes
2. Review recent logs
3. Check for unauthorized changes
4. Restore from backup if needed
5. Document incident

---

## Security Checklist

### Initial Setup

- [ ] Enable full disk encryption
- [ ] Create dedicated user account
- [ ] Set strong password
- [ ] Configure firewall rules
- [ ] Verify CDP port binding
- [ ] Set up log monitoring
- [ ] Configure backup system
- [ ] Enable 2FA on all accounts

### Ongoing Maintenance

- [ ] Review logs weekly
- [ ] Update dependencies monthly
- [ ] Rotate credentials quarterly
- [ ] Audit file permissions monthly
- [ ] Test backup restoration quarterly
- [ ] Review access rights monthly
- [ ] Update this document

### Before Going Public

- [ ] Remove test credentials
- [ ] Verify .gitignore is comprehensive
- [ ] Review all commits for secrets
- [ ] Test dry-run mode
- [ ] Document all credentials
- [ ] Create incident response plan
- [ ] Security audit (optional)

---

## Resources

### Tools

- **git-secrets**: Scan for secrets in git history
- **truffleHog**: Find credentials in code
- **OWASP ZAP**: Web application security testing
- **Wireshark**: Network traffic analysis

### Documentation

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OAuth 2.0 Security Best Current Practice](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)

### Community

- Report security issues: [GitHub Security]
- Security discussions: [GitHub Discussions]

---

## Disclaimer

This security document provides guidelines for securing the Personal AI Employee. Security is an ongoing process, and no system is completely secure. Users should:

1. Understand their threat model
2. Implement appropriate controls
3. Monitor for suspicious activity
4. Update security practices regularly
5. Seek professional advice for high-security requirements

---

*Last Updated: 2026-01-11*
