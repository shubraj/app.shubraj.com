import dns.resolver
import smtplib
import socket
import re

class EmailValidator:
    def __init__(self, email):
        self.email = email

    def is_valid_syntax(self):
        """Check if the email syntax is valid."""
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}(\.[a-zA-Z]{2,6})?$'
        return re.match(regex, self.email) is not None

    def domain_exists(self):
        """Check if the domain of the email exists."""
        domain = self.email.split('@')[-1]

        try:
            # Query MX records for the domain
            mx_records = dns.resolver.resolve(domain, 'MX')
            return [str(record.exchange) for record in mx_records]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            return False
        except Exception:
            return False

    def ping_mx_server(self, mx_record):
        """Ping the MX server to verify the email address."""
        try:
            # Establish an SMTP connection
            server = smtplib.SMTP(mx_record, 25, timeout=10)
            server.set_debuglevel(0)  # Set to 1 for debug output
            
            # HELO or EHLO command
            server.helo()
            
            # MAIL FROM command
            sender = f'test@{self.email.split("@")[-1]}'
            server.mail(sender)
            
            # RCPT TO command
            recipient = self.email
            code, message = server.rcpt(recipient)
            
            # Close the SMTP connection
            server.quit()

            # Check the response code for recipient existence
            if code == 250:
                return True, f"Email '{recipient}' exists."
            elif code == 550:
                return False, f"Email '{recipient}' does not exist."
            else:
                return False, f"Unexpected response from server: {message.decode()}"
        except (smtplib.SMTPException, socket.error) as e:
            return False, f"SMTP error occurred: {str(e)}"

    def validate(self):
        """Run full validation on the email."""
        
        # Check for valid syntax
        if not self.is_valid_syntax():
            return False, f"Invalid email syntax for '{self.email}'. Please ensure it follows the standard format (e.g., username@domain.com)."
        
        # Check for domain existence
        mx_records = self.domain_exists()
        if not mx_records:
            return False, f"The domain '{self.email.split('@')[-1]}' does not exist. Please check for typos or use a different domain."

        # Ping each MX server and check for the email existence
        for mx_record in mx_records:
            exists, message = self.ping_mx_server(mx_record)
            if exists:
                return True, f"The email '{self.email}' is valid and the domain exists."
            else:
                return False, message
        
        return False, "Email validation failed without a clear reason."

# Example usage
if __name__ == "__main__":
    email = 'test@shubraj.com.np'  # Replace with the email you want to validate
    validator = EmailValidator(email)
    is_valid, message = validator.validate()
    print(message)

    # Test with an invalid email
    email_invalid = 'invalid-email@'
    validator_invalid = EmailValidator(email_invalid)
    is_valid_invalid, message_invalid = validator_invalid.validate()
    print(message_invalid)
