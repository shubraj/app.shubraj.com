import dns.resolver
import smtplib
import socket
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

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
            return True,[str(record.exchange) for record in mx_records]
        except dns.resolver.NoAnswer:
            return False, "No MX records found for the domain."
        except dns.resolver.NXDOMAIN:
            return False, "The domain does not exist."
        except (dns.resolver.Timeout, dns.resolver.NoNameservers):
            return False, "DNS lookup timed out or no nameservers available."
        except Exception as e:
            return False, f"An unexpected error occurred while checking the domain: {str(e)}"

    def ping_mx_server(self, mx_record):
        """Ping the MX server to verify the email address."""
        try:
            # Establish an SMTP connection
            server = smtplib.SMTP(timeout=10)
            server.connect(mx_record, 25)
            server.helo()  # Use EHLO/HELO handshake
            server.mail('test@example.com')

            # Check if the email address exists on the server
            code, message = server.rcpt(self.email)
            server.quit()

            if code == 250:
                return True, f"The email '{self.email}' exists on the server."
            elif code == 550:
                return False, f"The email '{self.email}' does not exist."
            else:
                return False, f"Unexpected response from server: {message.decode()}"
        except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected):
            return False, "Could not connect to the SMTP server."
        except smtplib.SMTPRecipientsRefused:
            return False, "Recipient address refused by the server."
        except smtplib.SMTPHeloError:
            return False, "The server refused our EHLO/HELO message."
        except smtplib.SMTPSenderRefused:
            return False, "The server refused the sender address."
        except smtplib.SMTPDataError:
            return False, "The server replied with an unexpected error code."
        except (socket.timeout, socket.error) as e:
            return False, f"Network error occurred: {str(e)}"
        except Exception as e:
            return False, f"An unexpected error occurred while pinging the MX server: {str(e)}"

    def validate(self):
        """Run full validation on the email."""

        # Check for valid syntax
        if not self.is_valid_syntax():
            return False, f"Invalid email syntax for '{self.email}'. Please ensure it follows the standard format (e.g., username@domain.com)."

        # Check for domain existence
        domain_exists, domain_message = self.domain_exists()
        if not domain_exists:
            return False, domain_message

        # Ping each MX server and check for the email existence
        for mx_record in domain_message:
            exists, message = self.ping_mx_server("smtp.gmail.com")
            print(mx_record)
            if exists:
                return True, f"The email '{self.email}' is valid and the domain exists."
            else:
                # Log each MX server's failure message but continue to the next one
                continue
        
        return False, "Failed to validate the email on all available MX servers."
if __name__ == "__main__":
    status,message = EmailValidator("shuvraj1234@gmail.com").validate()
    print(status,message)