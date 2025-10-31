import ssl
import socket
from datetime import datetime
from typing import Dict, Optional, List
import certifi


def get_ssl_certificate_info(domain: str, port: int = 443, timeout: int = 10) -> Dict:
    """
    Retrieve SSL certificate information for a given domain.
    
    Args:
        domain: Domain name (without protocol)
        port: Port number (default: 443)
        timeout: Connection timeout in seconds
        
    Returns:
        Dictionary containing certificate information or error details
    """
    # Remove protocol if present
    domain = domain.replace('https://', '').replace('http://', '').strip().strip('/')
    
    if not domain:
        return {
            'error': 'Domain is required',
            'status': 'error'
        }
    
    try:
        # Create SSL context
        context = ssl.create_default_context(cafile=certifi.where())
        
        # Connect to the server
        with socket.create_connection((domain, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                # Get binary form for additional parsing if needed
                try:
                    cert_der = ssock.getpeercert(binary_form=True)
                except:
                    cert_der = None
                
                # Get certificate information
                info = {}
                
                # Parse subject
                subject = dict(x[0] for x in cert.get('subject', []))
                info['subject'] = subject.get('commonName', '') or subject.get('CN', '')
                if not info['subject']:
                    info['subject'] = ', '.join([f"{k}={v}" for k, v in subject.items()])
                
                # Parse issuer
                issuer = dict(x[0] for x in cert.get('issuer', []))
                issuer_parts = []
                if issuer.get('organizationName'):
                    issuer_parts.append(issuer['organizationName'])
                if issuer.get('organizationalUnitName'):
                    issuer_parts.append(issuer['organizationalUnitName'])
                if issuer.get('commonName'):
                    issuer_parts.append(issuer['commonName'])
                info['issuer'] = ', '.join(issuer_parts) if issuer_parts else ', '.join([f"{k}={v}" for k, v in issuer.items()])
                
                # Validity dates
                valid_from_str = cert.get('notBefore', '')
                valid_until_str = cert.get('notAfter', '')
                
                if valid_from_str:
                    try:
                        valid_from = datetime.strptime(valid_from_str, '%b %d %H:%M:%S %Y %Z')
                        info['valid_from'] = valid_from.strftime('%Y-%m-%d %H:%M:%S UTC')
                    except:
                        info['valid_from'] = valid_from_str
                
                if valid_until_str:
                    try:
                        valid_until = datetime.strptime(valid_until_str, '%b %d %H:%M:%S %Y %Z')
                        info['valid_until'] = valid_until.strftime('%Y-%m-%d %H:%M:%S UTC')
                        
                        # Calculate days until expiry
                        now = datetime.utcnow()
                        days_left = (valid_until - now).days
                        info['days_until_expiry'] = days_left
                        
                        # Determine status
                        if days_left < 0:
                            info['status'] = 'expired'
                        elif days_left <= 30:
                            info['status'] = 'expiring_soon'
                        else:
                            info['status'] = 'valid'
                    except:
                        info['valid_until'] = valid_until_str
                        info['status'] = 'unknown'
                
                # Serial number - get from certificate dict if available
                if 'serialNumber' in cert:
                    info['serial_number'] = str(cert['serialNumber'])
                
                # Version
                if 'version' in cert:
                    info['version'] = f"v{cert['version'] + 1}"
                
                # Subject Alternative Names
                sans = []
                for ext in cert.get('subjectAltName', []):
                    if isinstance(ext, tuple) and len(ext) >= 2:
                        sans.append(ext[1])
                if sans:
                    info['sans'] = sans
                
                # Domain matches
                domain_match = False
                if domain.lower() in info['subject'].lower():
                    domain_match = True
                elif sans and any(domain.lower() in san.lower() for san in sans):
                    domain_match = True
                
                info['domain_match'] = domain_match
                
                return info
                
    except socket.gaierror as e:
        return {
            'error': f'Could not resolve domain: {str(e)}',
            'status': 'error'
        }
    except socket.timeout:
        return {
            'error': 'Connection timeout. The domain may be unreachable.',
            'status': 'error'
        }
    except ssl.SSLError as e:
        return {
            'error': f'SSL error: {str(e)}',
            'status': 'error'
        }
    except Exception as e:
        return {
            'error': f'Error checking certificate: {str(e)}',
            'status': 'error'
        }

