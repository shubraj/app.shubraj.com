import requests
from typing import Dict, Optional, List
import re
import ssl
import socket
from urllib.parse import urlparse


def check_security_headers(domain: str, timeout: int = 10) -> Dict:
    """
    Check security headers for a domain.
    
    Args:
        domain: Domain name (without protocol)
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing security headers information
    """
    # Remove protocol if present
    domain = domain.replace('https://', '').replace('http://', '').strip().strip('/')
    
    if not domain:
        return {
            'error': 'Domain is required',
            'status': 'error'
        }
    
    result = {
        'domain': domain,
        'status': 'success',
        'headers_found': [],
        'headers_missing': [],
        'security_score': 0,
        'details': {},
        'recommendations': []
    }
    
    # Define security headers to check
    security_headers = {
        'Strict-Transport-Security': {
            'name': 'HSTS',
            'recommended': True,
            'description': 'Forces HTTPS connections',
            'score': 20
        },
        'Content-Security-Policy': {
            'name': 'CSP',
            'recommended': True,
            'description': 'Prevents XSS attacks',
            'score': 20
        },
        'X-Frame-Options': {
            'name': 'X-Frame-Options',
            'recommended': True,
            'description': 'Prevents clickjacking',
            'score': 15
        },
        'X-Content-Type-Options': {
            'name': 'X-Content-Type-Options',
            'recommended': True,
            'description': 'Prevents MIME-type sniffing',
            'score': 15
        },
        'Referrer-Policy': {
            'name': 'Referrer-Policy',
            'recommended': True,
            'description': 'Controls referrer information',
            'score': 10
        },
        'Permissions-Policy': {
            'name': 'Permissions-Policy',
            'recommended': True,
            'description': 'Controls browser features',
            'score': 10
        },
        'Cross-Origin-Embedder-Policy': {
            'name': 'COEP',
            'recommended': True,
            'description': 'Prevents document from loading cross-origin resources',
            'score': 5
        },
        'Cross-Origin-Opener-Policy': {
            'name': 'COOP',
            'recommended': True,
            'description': 'Isolates browsing context',
            'score': 5
        },
        'Cross-Origin-Resource-Policy': {
            'name': 'CORP',
            'recommended': True,
            'description': 'Controls resource embedding',
            'score': 5
        },
        'X-DNS-Prefetch-Control': {
            'name': 'DNS Prefetch Control',
            'recommended': True,
            'description': 'Controls DNS prefetching',
            'score': 3
        },
        'X-XSS-Protection': {
            'name': 'X-XSS-Protection',
            'recommended': False,
            'description': 'Legacy XSS protection (deprecated)',
            'score': 5,
            'note': 'Deprecated but still used by some sites'
        },
        'Expect-CT': {
            'name': 'Expect-CT',
            'recommended': False,
            'description': 'Certificate Transparency (deprecated)',
            'score': 0,
            'note': 'Deprecated in favor of TLS 1.3'
        },
        'Public-Key-Pins': {
            'name': 'HPKP',
            'recommended': False,
            'description': 'HTTP Public Key Pinning (deprecated)',
            'score': 0,
            'note': 'Deprecated - can cause site lockout'
        }
    }
    
    try:
        # Try HTTPS first
        url = f'https://{domain}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Security-Headers-Checker/1.0)'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, verify=True)
            
            # Check each security header
            found_count = 0
            total_score = 0
            
            for header_name, header_info in security_headers.items():
                header_value = response.headers.get(header_name, '')
                
                header_result = {
                    'name': header_info['name'],
                    'full_name': header_name,
                    'present': bool(header_value),
                    'value': header_value if header_value else None,
                    'recommended': header_info['recommended'],
                    'description': header_info['description'],
                    'score': header_info['score'] if header_value else 0
                }
                
                if 'note' in header_info:
                    header_result['note'] = header_info['note']
                
                # Analyze header values for recommendations
                if header_value:
                    found_count += 1
                    total_score += header_info['score']
                    
                    # Analyze HSTS
                    if header_name == 'Strict-Transport-Security':
                        max_age_match = re.search(r'max-age=(\d+)', header_value, re.IGNORECASE)
                        if max_age_match:
                            max_age = int(max_age_match.group(1))
                            if max_age < 31536000:  # Less than 1 year
                                header_result['recommendation'] = 'Consider increasing max-age to at least 1 year (31536000 seconds)'
                            if 'includeSubDomains' not in header_value:
                                header_result['recommendation'] = 'Consider adding includeSubDomains directive'
                    
                    # Analyze CSP
                    elif header_name == 'Content-Security-Policy':
                        if "unsafe-inline" in header_value or "unsafe-eval" in header_value:
                            header_result['warning'] = 'Contains unsafe directives (unsafe-inline or unsafe-eval)'
                    
                    # Analyze X-Frame-Options
                    elif header_name == 'X-Frame-Options':
                        if header_value.upper() not in ['DENY', 'SAMEORIGIN']:
                            header_result['warning'] = 'Should be DENY or SAMEORIGIN'
                    
                    # Analyze X-Content-Type-Options
                    elif header_name == 'X-Content-Type-Options':
                        if header_value.upper() != 'NOSNIFF':
                            header_result['warning'] = 'Should be nosniff'
                
                result['details'][header_name] = header_result
                
                if header_value:
                    result['headers_found'].append(header_name)
                elif header_info['recommended']:
                    result['headers_missing'].append(header_name)
                    result['recommendations'].append(f"Add {header_name} header for better security")
            
            result['security_score'] = total_score
            result['max_score'] = sum([h['score'] for h in security_headers.values() if h['recommended']])
            result['headers_found_count'] = found_count
            result['total_headers_checked'] = len(security_headers)
            
            # Determine overall security level
            score_percentage = (total_score / result['max_score'] * 100) if result['max_score'] > 0 else 0
            if score_percentage >= 80:
                result['security_level'] = 'excellent'
                result['security_level_text'] = 'Excellent'
            elif score_percentage >= 60:
                result['security_level'] = 'good'
                result['security_level_text'] = 'Good'
            elif score_percentage >= 40:
                result['security_level'] = 'fair'
                result['security_level_text'] = 'Fair'
            else:
                result['security_level'] = 'poor'
                result['security_level_text'] = 'Poor'
            
            # Store response info
            result['final_url'] = response.url
            result['status_code'] = response.status_code
            result['server'] = response.headers.get('Server', 'Unknown')
            
            # Analyze cookies for security flags
            result['cookie_security'] = analyze_cookies(response)
            
            # Check TLS version
            tls_info = check_tls_version(domain)
            if tls_info:
                result['tls_info'] = tls_info
            
            # Check CORS policy
            cors_info = analyze_cors_headers(response.headers)
            if cors_info:
                result['cors_info'] = cors_info
            
            # Check for information disclosure
            info_disclosure = check_information_disclosure(response.headers)
            if info_disclosure:
                result['information_disclosure'] = info_disclosure
            
            # Check for additional security-related headers
            result['additional_headers'] = {}
            security_related = ['Cache-Control', 'X-Powered-By', 'Server', 'Via', 'X-AspNet-Version']
            for header in security_related:
                if header in response.headers:
                    result['additional_headers'][header] = response.headers[header]
            
            # Recommendation about X-Powered-By
            if 'X-Powered-By' in response.headers:
                result['recommendations'].append('Remove X-Powered-By header to hide server technology')
            
            if 'Server' in response.headers and len(response.headers['Server']) > 0:
                result['recommendations'].append('Consider removing or minimizing Server header to hide server version')
            
        except requests.exceptions.SSLError:
            result['status'] = 'ssl_error'
            result['error'] = 'SSL/TLS error - domain may not support HTTPS or has certificate issues'
        except requests.exceptions.ConnectionError:
            result['status'] = 'connection_error'
            result['error'] = 'Could not connect to the domain'
        except requests.exceptions.Timeout:
            result['status'] = 'timeout'
            result['error'] = 'Connection timeout'
        except requests.exceptions.RequestException as e:
            result['status'] = 'error'
            result['error'] = f'Request failed: {str(e)}'
    
    except Exception as e:
        result['status'] = 'error'
        result['error'] = f'Unexpected error: {str(e)}'
    
    return result


def analyze_cookies(response: requests.Response) -> Dict:
    """Analyze Set-Cookie headers for security flags."""
    # Get Set-Cookie headers - requests may have multiple
    # Try to get from response.raw or check response.cookies
    cookies_raw = []
    
    # Check response.cookies (already parsed, but we need raw headers for flags)
    if hasattr(response, 'raw') and hasattr(response.raw, 'headers'):
        # Access raw headers for Set-Cookie
        raw_headers = getattr(response.raw, 'headers', {})
        if 'Set-Cookie' in raw_headers:
            set_cookie_val = raw_headers['Set-Cookie']
            if isinstance(set_cookie_val, list):
                cookies_raw = set_cookie_val
            else:
                cookies_raw = [set_cookie_val]
    
    # Fallback: try to get from response.headers
    if not cookies_raw:
        set_cookie = response.headers.get('Set-Cookie', '')
        if set_cookie:
            cookies_raw = [set_cookie] if isinstance(set_cookie, str) else set_cookie
    
    if not cookies_raw:
        return {
            'cookies_found': False,
            'total_cookies': 0,
            'secure_cookies': 0,
            'httponly_cookies': 0,
            'samesite_cookies': 0,
            'details': []
        }
    
    analysis = {
        'cookies_found': True,
        'total_cookies': len(cookies_raw),
        'secure_cookies': 0,
        'httponly_cookies': 0,
        'samesite_cookies': 0,
        'details': []
    }
    
    for cookie in cookies_raw:
        cookie_info = {
            'cookie': cookie.split(';')[0] if ';' in cookie else cookie,
            'has_secure': False,
            'has_httponly': False,
            'has_samesite': False,
            'samesite_value': None,
            'issues': []
        }
        
        cookie_lower = cookie.lower()
        
        if 'secure' in cookie_lower:
            cookie_info['has_secure'] = True
            analysis['secure_cookies'] += 1
        else:
            cookie_info['issues'].append('Missing Secure flag - cookie can be sent over HTTP')
        
        if 'httponly' in cookie_lower:
            cookie_info['has_httponly'] = True
            analysis['httponly_cookies'] += 1
        else:
            cookie_info['issues'].append('Missing HttpOnly flag - accessible via JavaScript')
        
        samesite_match = re.search(r'samesite=([^;]+)', cookie_lower)
        if samesite_match:
            cookie_info['has_samesite'] = True
            cookie_info['samesite_value'] = samesite_match.group(1).strip()
            analysis['samesite_cookies'] += 1
            
            if cookie_info['samesite_value'] not in ['strict', 'lax', 'none']:
                cookie_info['issues'].append(f"Invalid SameSite value: {cookie_info['samesite_value']}")
            elif cookie_info['samesite_value'] == 'none' and 'secure' not in cookie_lower:
                cookie_info['issues'].append('SameSite=None requires Secure flag')
        else:
            cookie_info['issues'].append('Missing SameSite attribute - vulnerable to CSRF')
        
        analysis['details'].append(cookie_info)
    
    return analysis


def check_tls_version(domain: str) -> Optional[Dict]:
    """Check TLS/SSL version being used."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                tls_version = ssock.version()
                
                info = {
                    'version': tls_version,
                    'version_name': tls_version.replace('TLS', 'TLS ').replace('PROTOCOL', '').strip(),
                    'is_secure': False,
                    'recommendation': None
                }
                
                # TLS 1.3 is the latest and most secure
                if 'TLSv1.3' in tls_version:
                    info['is_secure'] = True
                    info['security_level'] = 'excellent'
                elif 'TLSv1.2' in tls_version:
                    info['is_secure'] = True
                    info['security_level'] = 'good'
                    info['recommendation'] = 'Consider upgrading to TLS 1.3 for better security'
                elif 'TLSv1.1' in tls_version or 'TLSv1.0' in tls_version:
                    info['is_secure'] = True
                    info['security_level'] = 'weak'
                    info['recommendation'] = 'TLS 1.0/1.1 are deprecated - upgrade to TLS 1.2 or 1.3'
                elif 'SSL' in tls_version:
                    info['security_level'] = 'insecure'
                    info['recommendation'] = 'SSL is deprecated and insecure - use TLS 1.2 or 1.3'
                
                return info
    except:
        return None


def analyze_cors_headers(headers: Dict) -> Optional[Dict]:
    """Analyze CORS (Cross-Origin Resource Sharing) headers."""
    cors_headers = {
        'Access-Control-Allow-Origin': headers.get('Access-Control-Allow-Origin'),
        'Access-Control-Allow-Methods': headers.get('Access-Control-Allow-Methods'),
        'Access-Control-Allow-Headers': headers.get('Access-Control-Allow-Headers'),
        'Access-Control-Allow-Credentials': headers.get('Access-Control-Allow-Credentials'),
        'Access-Control-Max-Age': headers.get('Access-Control-Max-Age'),
    }
    
    # Check if any CORS headers are present
    has_cors = any(cors_headers.values())
    
    if not has_cors:
        return None
    
    analysis = {
        'cors_enabled': True,
        'details': {},
        'warnings': [],
        'recommendations': []
    }
    
    # Check Access-Control-Allow-Origin
    acao = cors_headers['Access-Control-Allow-Origin']
    if acao:
        analysis['details']['allow_origin'] = acao
        if acao == '*':
            if cors_headers['Access-Control-Allow-Credentials'] == 'true':
                analysis['warnings'].append('Wildcard (*) origin with credentials is not allowed by browsers')
            else:
                analysis['warnings'].append('Wildcard origin allows any site to access resources')
                analysis['recommendations'].append('Use specific origin instead of * when possible')
        else:
            analysis['details']['allow_origin'] = acao
    
    # Check Access-Control-Allow-Credentials
    if cors_headers['Access-Control-Allow-Credentials']:
        analysis['details']['allow_credentials'] = cors_headers['Access-Control-Allow-Credentials']
        if cors_headers['Access-Control-Allow-Credentials'].lower() == 'true':
            if acao == '*':
                analysis['warnings'].append('Credentials with wildcard origin will be blocked by browsers')
            else:
                analysis['recommendations'].append('Ensure allow-origin is specific and trusted when credentials=true')
    
    # Check allowed methods
    if cors_headers['Access-Control-Allow-Methods']:
        analysis['details']['allow_methods'] = cors_headers['Access-Control-Allow-Methods']
        methods = [m.strip() for m in cors_headers['Access-Control-Allow-Methods'].split(',')]
        if 'DELETE' in methods or 'PUT' in methods or 'PATCH' in methods:
            analysis['recommendations'].append('Review allowed methods - restrict to only what is necessary')
    
    return analysis


def check_information_disclosure(headers: Dict) -> Dict:
    """Check for information disclosure in headers."""
    disclosure = {
        'issues_found': [],
        'details': {}
    }
    
    # Server header
    server = headers.get('Server', '')
    if server and server.lower() != 'unknown':
        disclosure['details']['server'] = server
        if any(version in server for version in ['/', 'v', 'version']):
            disclosure['issues_found'].append('Server header reveals version information')
    
    # X-Powered-By
    if 'X-Powered-By' in headers:
        disclosure['details']['x_powered_by'] = headers['X-Powered-By']
        disclosure['issues_found'].append('X-Powered-By reveals application framework')
    
    # X-AspNet-Version
    if 'X-AspNet-Version' in headers:
        disclosure['details']['x_aspnet_version'] = headers['X-AspNet-Version']
        disclosure['issues_found'].append('X-AspNet-Version reveals ASP.NET version')
    
    # Via header (can reveal proxy/load balancer info)
    if 'Via' in headers:
        disclosure['details']['via'] = headers['Via']
        disclosure['issues_found'].append('Via header reveals proxy/load balancer information')
    
    # X-Runtime (Ruby on Rails)
    if 'X-Runtime' in headers:
        disclosure['details']['x_runtime'] = headers['X-Runtime']
        disclosure['issues_found'].append('X-Runtime reveals application runtime')
    
    if disclosure['issues_found']:
        disclosure['has_issues'] = True
    else:
        disclosure['has_issues'] = False
    
    return disclosure

