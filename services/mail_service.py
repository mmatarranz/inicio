import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv()

def get_inbox_summary(limit=5):
    """Fetch the latest emails from an IMAP server."""
    host = os.getenv("IMAP_SERVER")
    user = os.getenv("IMAP_USER")
    password = os.getenv("IMAP_PASS")
    
    if not all([host, user, password]):
        return {"error": "Missing IMAP credentials"}
        
    try:
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(host)
        mail.login(user, password)
        mail.select("inbox")
        
        # Search for all emails
        _, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        
        # Get only the last 'limit' emails
        latest_ids = email_ids[-limit:][::-1]
        emails = []
        
        for e_id in latest_ids:
            _, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8")
                    
                    sender, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(sender, bytes):
                        sender = sender.decode(encoding or "utf-8")
                        
                    emails.append({"from": sender, "subject": subject})
                    
        mail.logout()
        return emails
        
    except Exception as e:
        return {"error": str(e)}
