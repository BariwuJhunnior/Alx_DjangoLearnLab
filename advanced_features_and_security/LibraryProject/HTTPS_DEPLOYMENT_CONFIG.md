# HTTPS Deployment Configuration Guide

This document provides instructions and configuration examples for deploying the Django application with HTTPS support using popular web servers (Nginx and Apache).

## Prerequisites

- SSL/TLS certificate from a trusted certificate authority (Let's Encrypt, DigiCert, etc.)
- Private key corresponding to the SSL certificate
- Web server (Nginx or Apache) installed and running
- Django application served by a WSGI application server (Gunicorn, uWSGI, etc.)

---

## 1. Obtaining SSL/TLS Certificates

### Using Let's Encrypt (Free)

Let's Encrypt provides free SSL certificates valid for 90 days. Renewal is automated.

```bash
# Install Certbot (Let's Encrypt client)
sudo apt-get install certbot python3-certbot-nginx  # For Nginx
# OR
sudo apt-get install certbot python3-certbot-apache  # For Apache

# Obtain a certificate (example for domain: example.com)
sudo certbot certonly --standalone -d example.com -d www.example.com

# Certificates are typically stored in:
# /etc/letsencrypt/live/example.com/
#   - fullchain.pem (certificate chain)
#   - privkey.pem (private key)
```

### Using a Commercial CA

Contact your certificate provider (DigiCert, Comodo, etc.) and follow their CSR (Certificate Signing Request) generation process. You'll receive:

- `certificate.crt` or `certificate.pem`
- `private_key.key` or `private_key.pem`
- Optionally, intermediate certificates

---

## 2. Nginx Configuration

Below is a production-ready Nginx configuration with HTTPS, redirects, and security headers.

### File: `/etc/nginx/sites-available/libraryproject`

```nginx
# Redirect all HTTP requests to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;

    # Redirect all HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS server block
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name example.com www.example.com;

    # SSL Certificate and Private Key paths
    # (Update these paths to match your certificate location)
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # SSL/TLS Configuration
    # Use modern cipher suites and TLS 1.2+
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS (HTTP Strict Transport Security)
    # Tells browsers to always use HTTPS for this domain (max-age in seconds; 31536000 = 1 year)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:" always;

    # Logging
    access_log /var/log/nginx/libraryproject_access.log;
    error_log /var/log/nginx/libraryproject_error.log;

    # Django application (Gunicorn/uWSGI)
    location / {
        proxy_pass http://127.0.0.1:8000;  # Adjust port if using different WSGI server
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Static files (CSS, JS, images)
    location /static/ {
        alias /path/to/django/static/;  # Update to your project's static directory
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files (user uploads)
    location /media/ {
        alias /path/to/django/media/;  # Update to your project's media directory
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

### Enable the site and test Nginx config:

```bash
# Create symbolic link to enable the site
sudo ln -s /etc/nginx/sites-available/libraryproject /etc/nginx/sites-enabled/

# Test Nginx configuration syntax
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## 3. Apache Configuration

Below is a production-ready Apache configuration with HTTPS, redirects, and security headers.

### File: `/etc/apache2/sites-available/libraryproject.conf`

```apache
# Redirect all HTTP requests to HTTPS
<VirtualHost *:80>
    ServerName example.com
    ServerAlias www.example.com

    # Redirect all HTTP to HTTPS
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

    # Log files
    ErrorLog ${APACHE_LOG_DIR}/libraryproject_error.log
    CustomLog ${APACHE_LOG_DIR}/libraryproject_access.log combined
</VirtualHost>

# HTTPS server block
<VirtualHost *:443>
    ServerName example.com
    ServerAlias www.example.com

    # SSL/TLS Configuration
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/example.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/example.com/privkey.pem

    # Modern SSL/TLS protocols and ciphers
    SSLProtocol -all +TLSv1.2 +TLSv1.3
    SSLCipherSuite HIGH:!aNULL:!MD5
    SSLHonorCipherOrder on

    # HSTS (HTTP Strict Transport Security)
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"

    # Security Headers
    Header always set X-Frame-Options "DENY"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    Header always set Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:"

    # Enable required Apache modules
    <IfModule mod_rewrite.c>
        RewriteEngine On
    </IfModule>

    # Proxy to Django (Gunicorn/uWSGI)
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
    RequestHeader set X-Forwarded-Proto https
    RequestHeader set X-Forwarded-For %{REMOTE_ADDR}s

    # Static files (CSS, JS, images)
    Alias /static/ /path/to/django/static/
    <Directory /path/to/django/static/>
        Require all granted
        <IfModule mod_expires.c>
            ExpiresActive On
            ExpiresDefault "access plus 30 days"
        </IfModule>
    </Directory>

    # Media files (user uploads)
    Alias /media/ /path/to/django/media/
    <Directory /path/to/django/media/>
        Require all granted
        <IfModule mod_expires.c>
            ExpiresActive On
            ExpiresDefault "access plus 7 days"
        </IfModule>
    </Directory>

    # Log files
    ErrorLog ${APACHE_LOG_DIR}/libraryproject_error.log
    CustomLog ${APACHE_LOG_DIR}/libraryproject_access.log combined
</VirtualHost>
```

### Enable the site and required modules:

```bash
# Enable SSL and proxy modules
sudo a2enmod ssl
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod rewrite
sudo a2enmod headers
sudo a2enmod expires

# Enable the site
sudo a2ensite libraryproject.conf

# Disable the default site (optional)
sudo a2dissite 000-default.conf

# Test Apache configuration syntax
sudo apache2ctl configtest

# Restart Apache
sudo systemctl restart apache2
```

---

## 4. Django Settings for HTTPS

The Django application is already configured in `settings.py` with HTTPS support:

```python
# In LibraryProject/settings.py

# Redirect HTTP to HTTPS (set to False for local development)
SECURE_SSL_REDIRECT = False  # Change to True in production

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Secure cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Security headers
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
```

To enable HTTPS in Django for production:

1. Ensure your web server (Nginx/Apache) is configured with SSL/TLS.
2. Update `ALLOWED_HOSTS` in `settings.py` to include your production domain:
   ```python
   ALLOWED_HOSTS = ['example.com', 'www.example.com']
   ```
3. Set `SECURE_SSL_REDIRECT = True` in production.
4. Set `DEBUG = False` in production.
5. Use environment variables or separate production settings file to manage sensitive configurations.

---

## 5. WSGI Application Server Setup (Gunicorn Example)

Deploy the Django application using Gunicorn:

```bash
# Install Gunicorn
pip install gunicorn

# Run Gunicorn (binds to localhost:8000)
gunicorn --bind 127.0.0.1:8000 --workers 4 LibraryProject.wsgi:application
```

### Systemd Service File: `/etc/systemd/system/libraryproject.service`

```ini
[Unit]
Description=LibraryProject Django Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/django/project
ExecStart=/path/to/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 4 LibraryProject.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable libraryproject.service
sudo systemctl start libraryproject.service
```

---

## 6. Certificate Renewal (Let's Encrypt)

Let's Encrypt certificates expire after 90 days. Set up automatic renewal:

```bash
# Certbot automatically installs a cron job for renewal, but you can manually renew:
sudo certbot renew --dry-run  # Test renewal (doesn't actually renew)
sudo certbot renew            # Actually renew expiring certificates
```

For automated renewal with Nginx:

```bash
# Add Certbot renewal timer
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## 7. Testing HTTPS Configuration

### Verify SSL certificate:

```bash
# Check certificate details
openssl s_client -connect example.com:443

# Verify certificate validity
curl -v https://example.com
```

### Test HSTS headers:

```bash
# Check HSTS header
curl -I https://example.com | grep Strict-Transport-Security
```

### SSL/TLS Labs test:

Visit [SSL Labs](https://www.ssllabs.com/ssltest/) to rate your HTTPS configuration (A+ recommended for production).

---

## 8. Troubleshooting

| Issue                  | Solution                                                                                         |
| ---------------------- | ------------------------------------------------------------------------------------------------ |
| "502 Bad Gateway"      | Check if Gunicorn/uWSGI is running on the correct port. Verify proxy settings in Nginx/Apache.   |
| Certificate not found  | Verify paths to certificate and key files. Ensure permissions allow the web server to read them. |
| Mixed content warning  | Ensure all resources (CSS, JS, images) are loaded over HTTPS. Check Content-Security-Policy.     |
| HSTS causing issues    | HSTS cannot be easily disabled once set. Test thoroughly before enabling for production.         |
| Cookies not being sent | Verify `SESSION_COOKIE_SECURE = True` is set. Check that connection is actually HTTPS.           |

---

## Summary

This configuration ensures:

- ✅ All traffic is encrypted (HTTPS)
- ✅ Automatic HTTP → HTTPS redirects
- ✅ HSTS prevents downgrade attacks
- ✅ Security headers protect against XSS and clickjacking
- ✅ Secure cookies prevent interception
- ✅ Proper logging for monitoring

For production, review the checklist in Django's [deployment documentation](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/).
