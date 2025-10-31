import requests
from typing import Dict, List, Optional
from urllib.parse import urlparse, urljoin
import time


def analyze_redirect_chain(url: str, max_redirects: int = 20, timeout: int = 10) -> Dict:
    """
    Analyze HTTP redirect chain for a given URL.
    
    Args:
        url: URL to analyze (can include or exclude protocol)
        max_redirects: Maximum number of redirects to follow
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing redirect chain information
    """
    # Normalize URL - add protocol if missing
    if not url:
        return {
            'error': 'URL is required',
            'status': 'error'
        }
    
    # Remove whitespace
    url = url.strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    result = {
        'original_url': url,
        'status': 'success',
        'redirect_chain': [],
        'final_url': None,
        'total_redirects': 0,
        'has_redirects': False,
        'redirect_types': [],
        'issues': [],
        'warnings': []
    }
    
    try:
        redirect_chain = []
        current_url = url
        seen_urls = set()  # Track to detect loops
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Redirect-Chain-Analyzer/1.0)'
        }
        
        for step in range(max_redirects + 1):
            if current_url in seen_urls:
                result['issues'].append(f'Redirect loop detected: {current_url}')
                result['status'] = 'loop_detected'
                break
            
            seen_urls.add(current_url)
            
            try:
                response = requests.head(
                    current_url,
                    headers=headers,
                    timeout=timeout,
                    allow_redirects=False,  # Manually follow redirects
                    verify=True
                )
                
                redirect_info = {
                    'step': step + 1,
                    'url': current_url,
                    'status_code': response.status_code,
                    'status_text': get_status_text(response.status_code),
                    'redirect_type': None,
                    'location': None,
                    'headers': {}
                }
                
                # Check if it's a redirect
                if response.status_code in [301, 302, 303, 307, 308]:
                    location = response.headers.get('Location')
                    if location:
                        # Handle relative URLs
                        redirect_info['location'] = location
                        redirect_info['redirect_type'] = get_redirect_type(response.status_code)
                        
                        # Get absolute URL for next request
                        if location.startswith('http://') or location.startswith('https://'):
                            next_url = location
                        else:
                            parsed = urlparse(current_url)
                            next_url = urljoin(f"{parsed.scheme}://{parsed.netloc}", location)
                        
                        redirect_chain.append(redirect_info)
                        current_url = next_url
                        result['has_redirects'] = True
                        result['total_redirects'] += 1
                        result['redirect_types'].append(redirect_info['redirect_type'])
                        
                        # Check for issues
                        if response.status_code == 301 and step > 0:
                            # Permanent redirects in chain might be inefficient
                            result['warnings'].append(f'Step {step + 1}: Permanent redirect (301) in chain - consider updating to final URL')
                        
                        continue
                    else:
                        # Redirect status but no Location header
                        redirect_info['issues'] = ['Redirect status code but no Location header']
                        redirect_chain.append(redirect_info)
                        break
                
                # Not a redirect - final destination
                redirect_info['is_final'] = True
                redirect_chain.append(redirect_info)
                result['final_url'] = current_url
                break
                
            except requests.exceptions.TooManyRedirects:
                result['status'] = 'too_many_redirects'
                result['error'] = f'Too many redirects (exceeded {max_redirects} redirects)'
                break
                
            except requests.exceptions.Timeout:
                result['status'] = 'timeout'
                result['error'] = f'Request to {current_url} timed out'
                break
                
            except requests.exceptions.ConnectionError:
                result['status'] = 'connection_error'
                result['error'] = f'Could not connect to {current_url}'
                break
                
            except requests.exceptions.SSLError:
                result['status'] = 'ssl_error'
                result['error'] = f'SSL/TLS error with {current_url}'
                break
                
            except requests.exceptions.RequestException as e:
                result['status'] = 'error'
                result['error'] = f'Request failed: {str(e)}'
                break
        
        if step >= max_redirects:
            result['status'] = 'max_redirects_reached'
            result['warnings'].append(f'Maximum redirect limit ({max_redirects}) reached')
        
        result['redirect_chain'] = redirect_chain
        
        # Additional analysis
        if result['has_redirects']:
            # Check for mixed protocols
            protocols = set()
            for step_info in redirect_chain:
                parsed = urlparse(step_info['url'])
                if parsed.scheme:
                    protocols.add(parsed.scheme)
            
            if 'http://' in protocols and 'https://' in protocols:
                result['warnings'].append('Mixed HTTP/HTTPS redirects detected - consider using HTTPS only')
            
            # Check redirect chain length
            if result['total_redirects'] > 5:
                result['warnings'].append(f'Long redirect chain ({result["total_redirects"]} redirects) - consider shortening for better performance')
            
            # Check for temporary redirects to permanent destinations
            if 302 in result['redirect_types'] or 307 in result['redirect_types']:
                result['warnings'].append('Temporary redirects (302/307) detected - consider using permanent redirects (301/308) if destination is stable')
        
    except Exception as e:
        result['status'] = 'error'
        result['error'] = f'Unexpected error: {str(e)}'
    
    return result


def get_redirect_type(status_code: int) -> str:
    """Get human-readable redirect type."""
    redirect_types = {
        301: 'Permanent Redirect',
        302: 'Temporary Redirect',
        303: 'See Other',
        307: 'Temporary Redirect',
        308: 'Permanent Redirect'
    }
    return redirect_types.get(status_code, 'Unknown Redirect')


def get_status_text(status_code: int) -> str:
    """Get HTTP status text."""
    status_texts = {
        200: 'OK',
        301: 'Moved Permanently',
        302: 'Found',
        303: 'See Other',
        307: 'Temporary Redirect',
        308: 'Permanent Redirect',
        404: 'Not Found',
        500: 'Internal Server Error'
    }
    return status_texts.get(status_code, f'Status {status_code}')

