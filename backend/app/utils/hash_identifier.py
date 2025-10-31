import re
from typing import Dict, List, Optional


def identify_hash(hash_string: str) -> Dict:
    """
    Identify the type of hash algorithm based on hash string characteristics.
    
    Args:
        hash_string: The hash string to identify
        
    Returns:
        Dictionary containing possible hash types with confidence levels
    """
    if not hash_string or not hash_string.strip():
        return {
            'error': 'Please provide a hash string',
            'possible_types': []
        }
    
    hash_str = hash_string.strip()
    hash_length = len(hash_str)
    
    # Remove common prefixes (like $2a$, $2b$, $2y$ for bcrypt)
    hash_for_analysis = hash_str
    
    results = {
        'hash_string': hash_str,
        'length': hash_length,
        'possible_types': [],
        'most_likely': None
    }
    
    # Check for bcrypt hashes
    # Format: $2a$, $2b$, $2y$, $2x$ followed by cost parameter and 53 char hash
    if hash_str.startswith('$2a$') or hash_str.startswith('$2b$') or \
       hash_str.startswith('$2y$') or hash_str.startswith('$2x$'):
        if len(hash_str) == 60:
            results['possible_types'].append({
                'type': 'bcrypt',
                'confidence': 'Very High',
                'description': 'Bcrypt hash (Blowfish-based)'
            })
            results['most_likely'] = 'bcrypt'
    
    # Check for MD5 (32 hex characters)
    if hash_length == 32 and re.match(r'^[a-fA-F0-9]{32}$', hash_str):
        results['possible_types'].append({
            'type': 'MD5',
            'confidence': 'High',
            'description': 'MD5 hash (128-bit, 32 hex characters)'
        })
        if not results['most_likely']:
            results['most_likely'] = 'MD5'
    
    # Check for SHA-1 (40 hex characters)
    if hash_length == 40 and re.match(r'^[a-fA-F0-9]{40}$', hash_str):
        results['possible_types'].append({
            'type': 'SHA-1',
            'confidence': 'High',
            'description': 'SHA-1 hash (160-bit, 40 hex characters)'
        })
        if not results['most_likely']:
            results['most_likely'] = 'SHA-1'
    
    # Check for SHA-224 (56 hex characters)
    if hash_length == 56 and re.match(r'^[a-fA-F0-9]{56}$', hash_str):
        results['possible_types'].append({
            'type': 'SHA-224',
            'confidence': 'High',
            'description': 'SHA-224 hash (224-bit, 56 hex characters)'
        })
        if not results['most_likely']:
            results['most_likely'] = 'SHA-224'
    
    # Check for SHA-256 (64 hex characters)
    if hash_length == 64 and re.match(r'^[a-fA-F0-9]{64}$', hash_str):
        results['possible_types'].append({
            'type': 'SHA-256',
            'confidence': 'High',
            'description': 'SHA-256 hash (256-bit, 64 hex characters)'
        })
        if not results['most_likely']:
            results['most_likely'] = 'SHA-256'
    
    # Check for SHA-384 (96 hex characters)
    if hash_length == 96 and re.match(r'^[a-fA-F0-9]{96}$', hash_str):
        results['possible_types'].append({
            'type': 'SHA-384',
            'confidence': 'High',
            'description': 'SHA-384 hash (384-bit, 96 hex characters)'
        })
        if not results['most_likely']:
            results['most_likely'] = 'SHA-384'
    
    # Check for SHA-512 (128 hex characters)
    if hash_length == 128 and re.match(r'^[a-fA-F0-9]{128}$', hash_str):
        results['possible_types'].append({
            'type': 'SHA-512',
            'confidence': 'High',
            'description': 'SHA-512 hash (512-bit, 128 hex characters)'
        })
        if not results['most_likely']:
            results['most_likely'] = 'SHA-512'
    
    # Check for Argon2 hashes
    # Format: $argon2id$v=19$m=...$t=...$p=...
    if hash_str.startswith('$argon2'):
        results['possible_types'].append({
            'type': 'Argon2',
            'confidence': 'Very High',
            'description': 'Argon2 password hash (Argon2id, Argon2i, or Argon2d)'
        })
        if not results['most_likely']:
            results['most_likely'] = 'Argon2'
    
    # Check for scrypt
    # Format: $scrypt$...
    if hash_str.startswith('$scrypt$'):
        results['possible_types'].append({
            'type': 'scrypt',
            'confidence': 'Very High',
            'description': 'scrypt password hash'
        })
        if not results['most_likely']:
            results['most_likely'] = 'scrypt'
    
    # Check for PBKDF2
    # Format: $pbkdf2$...
    if hash_str.startswith('$pbkdf2'):
        results['possible_types'].append({
            'type': 'PBKDF2',
            'confidence': 'Very High',
            'description': 'PBKDF2 (Password-Based Key Derivation Function 2)'
        })
        if not results['most_likely']:
            results['most_likely'] = 'PBKDF2'
    
    # Check for MySQL PASSWORD() (old, deprecated)
    # 16 hex characters
    if hash_length == 16 and re.match(r'^[a-fA-F0-9]{16}$', hash_str):
        results['possible_types'].append({
            'type': 'MySQL OLD_PASSWORD',
            'confidence': 'Medium',
            'description': 'MySQL OLD_PASSWORD() function (deprecated)'
        })
    
    # Check for CRC32 (8 hex characters)
    if hash_length == 8 and re.match(r'^[a-fA-F0-9]{8}$', hash_str):
        results['possible_types'].append({
            'type': 'CRC32',
            'confidence': 'Medium',
            'description': 'CRC32 checksum (32-bit, 8 hex characters)'
        })
        if not results['most_likely']:
            results['most_likely'] = 'CRC32'
    
    # Check for NTLM hash (32 hex characters, but different from MD5 context)
    # NTLM is also 32 hex chars, so it's ambiguous with MD5
    if hash_length == 32 and re.match(r'^[a-fA-F0-9]{32}$', hash_str):
        results['possible_types'].append({
            'type': 'NTLM',
            'confidence': 'Low',
            'description': 'NTLM hash (could also be MD5 - context dependent)'
        })
    
    # Check for SHA-256 in base64 (44 characters with padding)
    if hash_length == 44 or hash_length == 43:
        if re.match(r'^[A-Za-z0-9+/=]+$', hash_str):
            results['possible_types'].append({
                'type': 'SHA-256 (Base64)',
                'confidence': 'Medium',
                'description': 'SHA-256 hash encoded in Base64'
            })
    
    # Check for SHA-512 in base64 (88 characters)
    if hash_length == 88 or hash_length == 87:
        if re.match(r'^[A-Za-z0-9+/=]+$', hash_str):
            results['possible_types'].append({
                'type': 'SHA-512 (Base64)',
                'confidence': 'Medium',
                'description': 'SHA-512 hash encoded in Base64'
            })
    
    # If no matches found
    if not results['possible_types']:
        results['possible_types'].append({
            'type': 'Unknown',
            'confidence': 'N/A',
            'description': f'Could not identify hash type. Length: {hash_length} characters'
        })
        results['most_likely'] = None
    
    return results

