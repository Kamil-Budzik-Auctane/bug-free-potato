import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from models import Package, EnrichedPackage
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@shipstation.com")
        self.mock_mode = self.api_key is None or self.api_key == "mock_api_key"
        
        if self.mock_mode:
            logger.info("EmailService initialized in MOCK MODE (no SendGrid API key)")
        else:
            logger.info(f"EmailService initialized with SendGrid API key: {self.api_key[:8] if self.api_key else 'None'}...")
            logger.info(f"From email: {self.from_email}")
            self.sg = SendGridAPIClient(api_key=self.api_key)
    
    async def send_delay_alert(
        self, 
        enriched_package: EnrichedPackage, 
        customer_email: Optional[str] = None
    ) -> dict:
        """Send delay alert email to customer"""
        
        logger.info(f"Preparing delay alert email for package {enriched_package.package_id}")
        logger.info(f"Package risk score: {enriched_package.risk_score}, reasons: {enriched_package.reasons}")
        
        # Use mock email if none provided
        recipient_email = customer_email or "customer@example.com"
        logger.info(f"Recipient email: {recipient_email}")
        
        # Generate email content
        subject = f"Delivery Alert: Package {enriched_package.package_id} may be delayed"
        logger.info(f"Email subject: {subject}")
        
        html_content = self._generate_alert_email_html(enriched_package)
        plain_content = self._generate_alert_email_text(enriched_package)
        logger.info(f"Email content generated (HTML: {len(html_content)} chars, Text: {len(plain_content)} chars)")
        
        if self.mock_mode:
            logger.info("Using MOCK email sending")
            return await self._mock_send_email(recipient_email, subject, html_content)
        else:
            logger.info("Using real SendGrid email sending")
            return await self._send_email_via_sendgrid(
                recipient_email, subject, html_content, plain_content
            )
    
    def _generate_alert_email_html(self, package: EnrichedPackage) -> str:
        """Generate HTML email content"""
        reasons_list = "</li><li>".join(package.reasons)
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
                <h2 style="color: #e74c3c;">⚠️ Package Delivery Alert</h2>
                
                <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <h3>Package Details:</h3>
                    <ul>
                        <li><strong>Package ID:</strong> {package.package_id}</li>
                        <li><strong>Destination:</strong> {package.destination_city}, {package.destination_zip}</li>
                        <li><strong>Carrier:</strong> {package.carrier}</li>
                        <li><strong>Expected Delivery:</strong> {package.expected_delivery_date}</li>
                        <li><strong>Risk Level:</strong> {package.risk_score}/100</li>
                    </ul>
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <h3>Potential Delay Reasons:</h3>
                    <ul>
                        <li>{reasons_list}</li>
                    </ul>
                </div>
                
                <div style="margin: 20px 0; text-align: center;">
                    <h3>What would you like to do?</h3>
                    <p>Please visit our customer portal to choose your preferred action:</p>
                    
                    <div style="margin: 10px 0;">
                        <a href="#" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px;">Accept Delay</a>
                        <a href="#" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px;">Request Refund</a>
                        <a href="#" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px;">Resend Package</a>
                    </div>
                </div>
                
                <footer style="margin-top: 20px; font-size: 12px; color: #666;">
                    <p>This is an automated message from ShipStation. Please do not reply to this email.</p>
                </footer>
            </div>
        </body>
        </html>
        """
        return html
    
    def _generate_alert_email_text(self, package: EnrichedPackage) -> str:
        """Generate plain text email content"""
        reasons_text = "\n- ".join(package.reasons)
        
        return f"""
PACKAGE DELIVERY ALERT

Your package may be delayed:

Package Details:
- Package ID: {package.package_id}
- Destination: {package.destination_city}, {package.destination_zip}
- Carrier: {package.carrier}
- Expected Delivery: {package.expected_delivery_date}
- Risk Level: {package.risk_score}/100

Potential Delay Reasons:
- {reasons_text}

What would you like to do?
Please visit our customer portal to choose your preferred action:
1. Accept Delay
2. Request Refund  
3. Resend Package

This is an automated message from ShipStation.
        """
    
    async def _send_email_via_sendgrid(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        plain_content: str
    ) -> dict:
        """Send email using SendGrid API"""
        logger.info(f"Attempting to send email via SendGrid to {to_email}")
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=plain_content
            )
            logger.info(f"SendGrid message object created (from: {self.from_email}, to: {to_email})")
            
            response = self.sg.send(message)
            logger.info(f"SendGrid API response: status_code={response.status_code}")
            
            return {
                "success": True,
                "message": "Email sent successfully",
                "email_sent": True,
                "status_code": response.status_code
            }
            
        except Exception as e:
            logger.error(f"Failed to send email via SendGrid: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to send email: {str(e)}",
                "email_sent": False
            }
    
    async def _mock_send_email(self, to_email: str, subject: str, content: str) -> dict:
        """Mock email sending for development/testing"""
        logger.info(f"[MOCK EMAIL] To: {to_email}")
        logger.info(f"[MOCK EMAIL] Subject: {subject}")
        logger.info(f"[MOCK EMAIL] Content preview: {content[:100]}...")
        
        return {
            "success": True,
            "message": "Email sent successfully (mock mode)",
            "email_sent": True,
            "mock_mode": True
        }