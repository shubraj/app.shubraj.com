import whois
import socket
from datetime import datetime
from typing import Dict, Optional
import re


def get_domain_age(domain: str, timeout: int = 10) -> Dict:
    """
    Get domain registration date and calculate age.
    
    Args:
        domain: Domain name (without protocol)
        timeout: Connection timeout in seconds
        
    Returns:
        Dictionary containing domain age information or error details
    """
    # Remove protocol if present
    domain = domain.replace('https://', '').replace('http://', '').strip().strip('/')
    
    # Remove www. prefix if present for whois lookup
    domain_clean = domain.replace('www.', '')
    
    if not domain_clean:
        return {
            'error': 'Domain is required',
            'status': 'error'
        }
    
    # Extract just the domain name (remove paths)
    domain_parts = domain_clean.split('/')[0].split('?')[0]
    domain_name = domain_parts.split(':')[0]  # Remove port if present
    
    # Basic domain validation
    domain_pattern = r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$'
    if not re.match(domain_pattern, domain_name.lower()):
        return {
            'error': 'Invalid domain format',
            'status': 'error',
            'domain': domain_name
        }
    
    result = {
        'domain': domain_name,
        'status': 'success',
        'queried_domain': domain_name
    }
    
    try:
        # Try WHOIS lookup
        try:
            w = whois.whois(domain_name)
            
            # Get creation date (registration date)
            creation_date = None
            if w.creation_date:
                if isinstance(w.creation_date, list):
                    creation_date = w.creation_date[0]
                else:
                    creation_date = w.creation_date
            
            if not creation_date and w.registered_date:
                if isinstance(w.registered_date, list):
                    creation_date = w.registered_date[0]
                else:
                    creation_date = w.registered_date
            
            if creation_date:
                if isinstance(creation_date, str):
                    # Try to parse date string
                    try:
                        creation_date = datetime.strptime(creation_date.split()[0], '%Y-%m-%d')
                    except:
                        try:
                            creation_date = datetime.strptime(creation_date.split()[0], '%Y-%m-%d %H:%M:%S')
                        except:
                            creation_date = None
                
                if creation_date:
                    result['creation_date'] = creation_date.strftime('%Y-%m-%d')
                    result['creation_date_formatted'] = creation_date.strftime('%B %d, %Y')
                    
                    # Calculate age
                    now = datetime.now()
                    age_delta = now - creation_date
                    
                    years = age_delta.days // 365
                    months = (age_delta.days % 365) // 30
                    days = age_delta.days % 30
                    
                    age_parts = []
                    if years > 0:
                        age_parts.append(f"{years} year{'s' if years != 1 else ''}")
                    if months > 0:
                        age_parts.append(f"{months} month{'s' if months != 1 else ''}")
                    if days > 0 or not age_parts:
                        age_parts.append(f"{days} day{'s' if days != 1 else ''}")
                    
                    result['age'] = ', '.join(age_parts)
                    result['age_days'] = age_delta.days
                    result['age_years'] = round(age_delta.days / 365.25, 2)
            
            # Get expiration date
            expiration_date = None
            if w.expiration_date:
                if isinstance(w.expiration_date, list):
                    expiration_date = w.expiration_date[0]
                else:
                    expiration_date = w.expiration_date
            
            if expiration_date:
                if isinstance(expiration_date, str):
                    try:
                        expiration_date = datetime.strptime(expiration_date.split()[0], '%Y-%m-%d')
                    except:
                        try:
                            expiration_date = datetime.strptime(expiration_date.split()[0], '%Y-%m-%d %H:%M:%S')
                        except:
                            expiration_date = None
                
                if expiration_date:
                    result['expiration_date'] = expiration_date.strftime('%Y-%m-%d')
                    result['expiration_date_formatted'] = expiration_date.strftime('%B %d, %Y')
                    
                    # Calculate days until expiration
                    now = datetime.now()
                    if expiration_date > now:
                        days_until_expiry = (expiration_date - now).days
                        result['days_until_expiry'] = days_until_expiry
                        if days_until_expiry < 30:
                            result['expiration_warning'] = True
                    else:
                        result['expired'] = True
                        result['days_since_expiry'] = (now - expiration_date).days
            
            # Get registrar information
            if w.registrar:
                result['registrar'] = w.registrar
            
            # Get name servers
            if w.name_servers:
                if isinstance(w.name_servers, list):
                    result['name_servers'] = list(set([ns.lower() for ns in w.name_servers if ns]))
                else:
                    result['name_servers'] = [w.name_servers.lower()] if w.name_servers else []
            
            # Get domain status
            if w.status:
                if isinstance(w.status, list):
                    result['status_info'] = list(set([s for s in w.status if s]))
                else:
                    result['status_info'] = [w.status] if w.status else []
            
            # If no creation date found
            if 'creation_date' not in result:
                result['status'] = 'partial'
                result['error'] = 'Domain creation date not available in WHOIS data'
                result['available_info'] = []
                if result.get('registrar'):
                    result['available_info'].append('Registrar information')
                if result.get('name_servers'):
                    result['available_info'].append('Name servers')
                if result.get('expiration_date'):
                    result['available_info'].append('Expiration date')
                
        except Exception as e:
            # WHOIS parsing error
            result['status'] = 'error'
            error_msg = str(e).lower()
            if 'no whois server' in error_msg or 'timed out' in error_msg:
                result['error'] = 'WHOIS lookup timed out or no WHOIS server found for this domain'
            elif 'expiration' in error_msg or 'registration' in error_msg:
                result['error'] = 'Unable to retrieve registration information for this domain'
            else:
                result['error'] = f'WHOIS lookup failed: {str(e)}'
    
    except socket.gaierror:
        result['status'] = 'error'
        result['error'] = 'Invalid domain or domain does not exist'
    except Exception as e:
        result['status'] = 'error'
        result['error'] = f'Failed to query domain: {str(e)}'
    
    return result

