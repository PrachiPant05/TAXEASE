import os
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

class ReportAgent:
    def generate_pdf_report(self, name, tax_data):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Tax Report for {name}", ln=True, align='C')
        pdf.ln(10)

        for key, value in tax_data.items():
            pdf.cell(200, 10, txt=f"{key.replace('_', ' ').title()}: {value}", ln=True)

        report_path = f"static/{name}_tax_report.pdf"
        pdf.output(report_path)
        return report_path

    def send_report(self, email, report_path):
        sender = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASS")

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = email
        msg['Subject'] = "Your Tax Report"

        msg.attach(MIMEText("Please find your tax report attached.", 'plain'))

        with open(report_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(report_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(report_path)}"'
            msg.attach(part)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
