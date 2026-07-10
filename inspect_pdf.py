import pdfplumber

def inspect_pdf():
    pdf_path = "Villa.pdf"
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"--- Page {i + 1} ---")
            tables = page.extract_tables()
            if not tables:
                print("No tables found. Trying raw text...")
                text = page.extract_text()
                print(text[:500])
                continue
            
            for j, table in enumerate(tables):
                print(f"Table {j + 1}:")
                for row in table[:10]: # Print first 10 rows
                    print(row)
            break # Just check the first page

if __name__ == "__main__":
    inspect_pdf()
