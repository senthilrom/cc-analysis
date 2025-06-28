from fpdf import FPDF
import os

def create_hdfc_mock_pdf(path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Mock HDFC Credit Card Statement", ln=True)

    sample_lines = [
        "04/01/2025 07:12:57 REDBUS INDIA PRIVATE Bangalore 28 1094.25",
        "06/01/2025 22:00:21 SANTHOSH BAR AND RESTAURABANGALORE 228 8621.00",
        "09/01/2025 20:02:12 Redbus India Private L Bangalore 116 4455.00"
    ]
    for line in sample_lines:
        pdf.cell(200, 8, txt=line, ln=True)

    pdf.output(path)

def create_indusind_mock_pdf(path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Mock IndusInd Credit Card Statement", ln=True)

    sample_lines = [
        "09/01/2025 ZOMATO ONLINE SERVICES GURGAON 45 575.65 DR",
        "12/01/2025 AMAZON RETAIL INDIA MUMBAI 55 2350.00 DR",
        "14/01/2025 MCDONALDS BANGALORE 60 650.00 DR"
    ]
    for line in sample_lines:
        pdf.cell(200, 8, txt=line, ln=True)

    pdf.output(path)

from PyPDF2 import PdfReader, PdfWriter

def encrypt_pdf(input_path, output_path, password):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)
    with open(output_path, "wb") as f:
        writer.write(f)

if __name__ == "__main__":
    os.makedirs("tests/test_data", exist_ok=True)
    create_hdfc_mock_pdf("tests/test_data/mock_hdfc.pdf")
    create_indusind_mock_pdf("tests/test_data/mock_indusind.pdf")
    encrypt_pdf("tests/test_data/mock_hdfc.pdf", "tests/test_data/mock_hdfc_encrypted.pdf", "RSEN1211")
    encrypt_pdf("tests/test_data/mock_indusind.pdf", "tests/test_data/mock_indusind_encrypted.pdf", "sent1211")
    print("✅ Mock PDFs generated in tests/test_data/")