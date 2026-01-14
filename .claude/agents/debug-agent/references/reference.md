# Debug Agent Reference

---

## Error Patterns

### Authentication Errors
- `401 Unauthorized`
- `Authentication failed`
- `Invalid credentials`

**Solution:** Refresh OAuth tokens, check .env file

### Rate Limiting
- `429 Too Many Requests`
- `rate limit exceeded`

**Solution:** Implement exponential backoff, increase check interval

### Connection Errors
- `Connection timeout`
- `Network unreachable`

**Solution:** Check internet, verify API endpoint, increase timeout

### Permission Errors
- `403 Forbidden`
- `Permission denied`

**Solution:** Check file permissions, verify API scopes

### Import Errors
- `ModuleNotFoundError`
- `No module named`

**Solution:** Install missing dependencies

---

## PM2 Commands

```bash
# List processes
pm2 list

# Check logs
pm2 logs <process_name>

# Restart
pm2 restart <process_name>

# View details
pm2 show <process_name>
```

---

## Log Locations

| Type | Location |
|------|----------|
| PM2 error logs | `~/.pm2/logs/*-error.log` |
| PM2 output logs | `~/.pm2/logs/*-out.log` |
| Vault logs | `AI_Employee_Vault/Logs/YYYY-MM-DD.json` |
