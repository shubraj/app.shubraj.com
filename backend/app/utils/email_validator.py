import dns.resolver
import smtplib
import socket
import re
from django.contrib import messages

class EmailValidationError(Exception):
    """Base class for exceptions in this module."""
    pass

class InvalidEmailSyntax(EmailValidationError):
    """Exception raised for invalid email syntax."""
    pass

class DomainDoesNotExist(EmailValidationError):
    """Exception raised when the domain does not exist."""
    pass

class NoMXRecordsFound(EmailValidationError):
    """Exception raised when no MX records are found for the domain."""
    pass

class SMTPConnectionError(EmailValidationError):
    """Exception raised for errors in SMTP connection."""
    pass

class EmailNotFound(EmailValidationError):
    """Exception raised when the email address does not exist."""
    pass

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
            return True, [str(record.exchange) for record in mx_records]
        except dns.resolver.NoAnswer:
            raise NoMXRecordsFound("No MX records found for the domain.")
        except dns.resolver.NXDOMAIN:
            raise DomainDoesNotExist("The domain does not exist.")
        except (dns.resolver.Timeout, dns.resolver.NoNameservers):
            raise SMTPConnectionError("DNS lookup timed out or no nameservers available.")
        except Exception as e:
            raise EmailValidationError(f"An unexpected error occurred while checking the domain: {str(e)}")

    def ping_mx_server(self, mx_record):
        """Ping the MX server to verify the email address."""
        try:
            # Establish an SMTP connection to the MX server
            server = smtplib.SMTP(mx_record, 25, timeout=10)
            server.ehlo()  # Identify ourselves to the server
            
            # Upgrade the connection to a secure TLS connection
            server.starttls()
            server.ehlo()  # Re-identify ourselves over the TLS connection

            server.mail('test@example.com')

            # Check if the email address exists on the server
            code, message = server.rcpt(self.email)
            server.quit()
            
            if code == 250:
                return True, f"The email '{self.email}' exists on the server."
            elif code == 550:
                raise EmailNotFound(f"The email '{self.email}' does not exist.")
            else:
                raise EmailValidationError(f"Unexpected response from server: {message.decode()}")
        except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected):
            raise SMTPConnectionError("Could not connect to the SMTP server.")
        except smtplib.SMTPRecipientsRefused:
            raise EmailNotFound("Recipient address refused by the server.")
        except smtplib.SMTPHeloError:
            raise SMTPConnectionError("The server refused our EHLO/HELO message.")
        except smtplib.SMTPSenderRefused:
            raise SMTPConnectionError("The server refused the sender address.")
        except smtplib.SMTPDataError:
            raise EmailValidationError("The server replied with an unexpected error code.")
        except (socket.timeout, socket.error) as e:
            raise SMTPConnectionError(f"Network error occurred: {str(e)}")
        except Exception as e:
            raise EmailValidationError(f"An unexpected error occurred while pinging the MX server: {str(e)}")

    def validate(self):
        """Run full validation on the email."""
        # Check for valid syntax
        if not self.is_valid_syntax():
            raise InvalidEmailSyntax(f"Invalid email syntax for '{self.email}'. Please ensure it follows the standard format (e.g., username@domain.com).")

        # Check for domain existence
        domain_exists, domain_message = self.domain_exists()
        if not domain_exists:
            return False, domain_message

        # Ping each MX server and check for the email existence
        exists, message = self.ping_mx_server(domain_message[0])
        if exists:
            return True, f"The email '{self.email}' is valid."
        
        return False, "Failed to validate the email on all available MX servers."

if __name__ == "__main__":
    try:
        status, message = EmailValidator("shuvraj1234@gmail.com").validate()
        print(status, message)
    except EmailValidationError as e:
        print(f"Validation Error: {e}")
