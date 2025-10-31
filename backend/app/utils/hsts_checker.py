import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
import re


def check_hsts(domain: str, timeout: int = 10) -> Dict:
    """
    Check HSTS (HTTP Strict Transport Security) configuration for a domain.
    
    Args:
        domain: Domain name (without protocol)
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing HSTS information
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
        'hsts_enabled': False,
        'status': 'not_found',
        'header_value': None,
        'max_age': None,
        'include_subdomains': False,
        'preload': False,
        'details': {}
    }
    
    try:
        # Try HTTPS first
        url = f'https://{domain}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; HSTS-Checker/1.0)'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, verify=True)
            
            # Check for Strict-Transport-Security header
            hsts_header = response.headers.get('Strict-Transport-Security', '')
            
            if hsts_header:
                result['hsts_enabled'] = True
                result['status'] = 'enabled'
                result['header_value'] = hsts_header
                
                # Parse HSTS header
                # Format: max-age=SECONDS; includeSubDomains; preload
                
                # Extract max-age
                max_age_match = re.search(r'max-age=(\d+)', hsts_header, re.IGNORECASE)
                if max_age_match:
                    max_age_seconds = int(max_age_match.group(1))
                    result['max_age'] = max_age_seconds
                    result['details']['max_age_seconds'] = max_age_seconds
                    result['details']['max_age_days'] = max_age_seconds // 86400
                    result['details']['max_age_years'] = max_age_seconds // (86400 * 365)
                    
                    # Determine if it's a long-term policy (31536000 seconds = 1 year)
                    if max_age_seconds >= 31536000:
                        result['details']['policy_type'] = 'Long-term (≥1 year)'
                    elif max_age_seconds >= 86400:
                        result['details']['policy_type'] = 'Medium-term (≥1 day)'
                    else:
                        result['details']['policy_type'] = 'Short-term (<1 day)'
                
                # Check for includeSubDomains
                if re.search(r'includeSubDomains', hsts_header, re.IGNORECASE):
                    result['include_subdomains'] = True
                    result['details']['include_subdomains'] = True
                
                # Check for preload
                if re.search(r'preload', hsts_header, re.IGNORECASE):
                    result['preload'] = True
                    result['details']['preload'] = True
                    result['details']['preload_note'] = 'Domain may be eligible for browser preload lists'
                
                # Additional security headers check
                result['details']['additional_headers'] = {}
                
                # Check for Content-Security-Policy
                if 'Content-Security-Policy' in response.headers:
                    result['details']['additional_headers']['csp'] = True
                
                # Check for X-Frame-Options
                if 'X-Frame-Options' in response.headers:
                    result['details']['additional_headers']['x_frame_options'] = True
                
                # Check for X-Content-Type-Options
                if 'X-Content-Type-Options' in response.headers:
                    result['details']['additional_headers']['x_content_type_options'] = True
                
            else:
                result['status'] = 'not_enabled'
                result['details']['recommendation'] = 'HSTS header not found. Consider enabling it for better security.'
            
            # Store final URL (after redirects)
            result['final_url'] = response.url
            result['status_code'] = response.status_code
            
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

