# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Fast Inference Server seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please do NOT:

- Open a public GitHub issue
- Disclose the vulnerability publicly before it has been addressed

### Please DO:

1. **Email us directly** at: security@yourproject.com (replace with your actual email)
2. **Include the following information**:
   - Type of vulnerability
   - Full paths of source file(s) related to the vulnerability
   - Location of the affected source code (tag/branch/commit or direct URL)
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the issue, including how an attacker might exploit it

### What to expect:

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Updates**: We will send you regular updates about our progress
- **Timeline**: We aim to address critical vulnerabilities within 7 days
- **Credit**: We will credit you in the security advisory (unless you prefer to remain anonymous)

## Security Best Practices

When deploying Fast Inference Server:

### 1. Network Security

- **Use HTTPS**: Always use HTTPS in production (add nginx/traefik as reverse proxy)
- **Firewall**: Restrict access to the server port
- **VPN/Private Network**: Deploy in a private network when possible

### 2. Authentication

- **Add API Keys**: Implement authentication for production use
- **Rate Limiting**: Add rate limiting to prevent abuse
- **IP Whitelisting**: Restrict access to known IP addresses

Example authentication:
```python
from functools import wraps
from flask import request

API_KEY = os.environ.get('API_KEY', 'change-me-in-production')

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = request.headers.get('X-API-Key')
        if key != API_KEY:
            return {"error": "Unauthorized"}, 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/infer', methods=['POST'])
@require_api_key
def infer():
    # ... existing code
```

### 3. Input Validation

- **Validate file uploads**: Check file types and sizes
- **Sanitize inputs**: Validate all input data
- **Size limits**: Set maximum request size

### 4. Model Security

- **Verify model files**: Check integrity of uploaded models
- **Sandboxing**: Run inference in isolated environment
- **Resource limits**: Set memory and CPU limits

### 5. Logging and Monitoring

- **Log all requests**: Keep audit logs
- **Monitor anomalies**: Set up alerts for unusual activity
- **Regular updates**: Keep dependencies up to date

### 6. Docker Security

- **Non-root user**: Run container as non-root user
- **Read-only filesystem**: Mount volumes as read-only when possible
- **Security scanning**: Scan images for vulnerabilities

Example secure Dockerfile:
```dockerfile
FROM python:3.10-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app
COPY --chown=appuser:appuser . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Switch to non-root user
USER appuser

# Run server
CMD ["python", "server.py"]
```

## Known Security Considerations

### 1. Pickle Deserialization

**Risk**: Pickle can execute arbitrary code during deserialization

**Mitigation**:
- Only accept requests from trusted clients
- Use network isolation
- Consider alternative serialization (msgpack, protobuf) for untrusted sources

### 2. Model Upload

**Risk**: Malicious model files could contain harmful code

**Mitigation**:
- Validate tar file contents
- Check for path traversal attacks (already implemented)
- Scan uploaded files
- Require authentication for model updates

### 3. Resource Exhaustion

**Risk**: Large requests could exhaust server resources

**Mitigation**:
- Set request size limits
- Implement rate limiting
- Use timeouts
- Monitor resource usage

### 4. Information Disclosure

**Risk**: Error messages might leak sensitive information

**Mitigation**:
- Use generic error messages in production
- Log detailed errors server-side only
- Don't expose stack traces to clients

## Security Checklist for Production

- [ ] Enable HTTPS with valid SSL certificate
- [ ] Implement authentication (API keys, OAuth, etc.)
- [ ] Add rate limiting
- [ ] Set up firewall rules
- [ ] Use environment variables for secrets
- [ ] Enable logging and monitoring
- [ ] Regular security updates
- [ ] Run as non-root user
- [ ] Set resource limits
- [ ] Implement input validation
- [ ] Use security headers
- [ ] Regular security audits
- [ ] Backup and disaster recovery plan

## Vulnerability Disclosure Timeline

1. **Day 0**: Vulnerability reported
2. **Day 1-2**: Acknowledgment sent, initial assessment
3. **Day 3-7**: Investigation and patch development
4. **Day 7-14**: Testing and validation
5. **Day 14**: Public disclosure and patch release

## Security Updates

Security updates will be released as patch versions (e.g., 1.0.1, 1.0.2) and announced via:

- GitHub Security Advisories
- Release notes
- Email notification (if subscribed)

## Contact

For security issues: security@yourproject.com (replace with actual email)

For general issues: https://github.com/yourusername/Server_OpenSource/issues

---

Thank you for helping keep Fast Inference Server secure!
