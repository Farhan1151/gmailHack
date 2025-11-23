import imaplib
import email
from email.header import decode_header
import time
import re

# Your Gmail credentials
EMAIL = "shark551151@gmail.com"
PASSWORD = ""  # Your app password 

# Store the IDs of emails we've already seen
seen_emails = set()

def format_html_with_newlines(html_content):
    """Add newlines for HTML tags to improve text formatting, then remove HTML tags"""
    if not html_content:
        return ""
    
    # Add newlines for block-level HTML tags
    html_content = re.sub(r'</div>', '</div>\n\n', html_content)
    html_content = re.sub(r'</p>', '</p>\n\n', html_content)
    html_content = re.sub(r'<br\s*/?>', '<br>\n', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'</h[1-6]>', '</h>\n\n', html_content)
    html_content = re.sub(r'</ul>', '</ul>\n\n', html_content)
    html_content = re.sub(r'</ol>', '</ol>\n\n', html_content)
    html_content = re.sub(r'</li>', '</li>\n', html_content)
    html_content = re.sub(r'</table>', '</table>\n\n', html_content)
    html_content = re.sub(r'</tr>', '</tr>\n', html_content)
    html_content = re.sub(r'</td>', '</td>\t', html_content)
    
    # Remove all HTML tags but keep the content
    clean_text = re.sub(r'<[^>]+>', '', html_content)
    
    # Clean up multiple newlines
    clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)
    clean_text = re.sub(r'[ \t]+\n', '\n', clean_text)
    
    return clean_text.strip()

def get_email_body(msg):
    """Extract full email body from message - process HTML for formatting but remove tags"""
    body = ""
    plain_text_found = False
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            # Skip attachments
            if "attachment" in content_disposition:
                continue
                
            if content_type == "text/plain":
                try:
                    part_body = part.get_payload(decode=True)
                    if part_body:
                        body += part_body.decode('utf-8', errors='ignore') + "\n"
                        plain_text_found = True
                except Exception as e:
                    try:
                        body += str(part.get_payload()) + "\n"
                        plain_text_found = True
                    except:
                        pass
            elif content_type == "text/html" and not plain_text_found:
                # Use HTML content only if no plain text was found
                try:
                    part_body = part.get_payload(decode=True)
                    if part_body:
                        html_content = part_body.decode('utf-8', errors='ignore')
                        # Format HTML with newlines and remove tags
                        formatted_text = format_html_with_newlines(html_content)
                        if formatted_text:
                            body += formatted_text + "\n"
                except:
                    pass
    else:
        # Not multipart - simple email
        content_type = msg.get_content_type()
        try:
            email_body = msg.get_payload(decode=True)
            if email_body:
                if content_type == "text/plain":
                    body = email_body.decode('utf-8', errors='ignore')
                elif content_type == "text/html":
                    # Format HTML with newlines and remove tags
                    html_content = email_body.decode('utf-8', errors='ignore')
                    body = format_html_with_newlines(html_content)
                else:
                    body = str(msg.get_payload())
            else:
                body = str(msg.get_payload())
        except Exception as e:
            body = str(msg.get_payload())
    
    return body.strip()

def check_for_new_emails():
    """
    Check for new emails and return True if new emails found
    Only shows new emails that haven't been seen before
    """
    try:
        # Connect to Gmail IMAP server
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")  # Select inbox folder
        
        # Search for all emails
        status, messages = mail.search(None, "ALL")
        
        if status != "OK":
            return False
        
        # Convert messages to list of email IDs
        email_ids = messages[0].split()
        
        new_emails_found = False
        
        # Process emails from newest to oldest
        for email_id in reversed(email_ids):
            if email_id in seen_emails:
                continue  # Skip already seen emails
                
            # Mark as seen and process
            seen_emails.add(email_id)
            new_emails_found = True
            
            # Fetch the email
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            
            if status != "OK":
                continue
                
            # Parse email content
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Get email body only
            body = get_email_body(msg)
            
            # Display only the email content
            if body:
                print(body)
                print()  # Just a single newline between emails
        
        # Close connection
        mail.close()
        mail.logout()
        
        return new_emails_found
        
    except Exception as e:
        print(f"Error checking emails: {str(e)}")
        return False

def load_existing_emails():
    """Load existing emails without displaying them (just mark as seen)"""
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")
        
        status, messages = mail.search(None, "ALL")
        
        if status == "OK":
            email_ids = messages[0].split()
            # Mark all existing emails as seen (but don't display them)
            for email_id in email_ids:
                seen_emails.add(email_id)
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"Error loading existing emails: {str(e)}")

def email_monitor():
    """Continuously monitor for new emails - shows only content"""
    print("🚀 Starting email monitor...")
    print("⏰ Checking for new emails every second")
    print("Press Ctrl+C to stop\n")
    
    # Load existing emails to mark them as seen (but don't display them)
    load_existing_emails()
    print("Ready - waiting for new emails...\n")
    
    try:
        while True:
            # Check for new emails
            check_for_new_emails()
            time.sleep(1)  # Check every 1 second
            
    except KeyboardInterrupt:
        print("\n🛑 Email monitor stopped")

if __name__ == "__main__":
    # Start monitoring immediately
    email_monitor()