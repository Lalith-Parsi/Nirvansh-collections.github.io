import fitz  # PyMuPDF
from datetime import datetime
import sys
import os


def insert_date_into_pdf(
    pdf_path,
    output_path,
    date_str=None,
    font_size=12,
    font_color=(0, 0, 0),
    font_name="times-roman",
    verbose=True
):
    # Default to today's date if not provided
    date_str = date_str or datetime.today().strftime("%Y-%m-%d")

    # Validate font
    try:
        fitz.Font(fontname=font_name)
    except RuntimeError:
        raise ValueError(f"Font '{font_name}' is not supported by PyMuPDF.")

    # Open PDF
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    date_filled = {"date": False, "entered": False}

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            for line in block.get("lines", []):
                full_line = "".join([span["text"] for span in line["spans"]]).strip()

                for span in line["spans"]:
                    text = span["text"].strip()

                    # Match "ENTERED:"
                    if not date_filled["entered"] and "ENTERED:" in text:
                        x = span["bbox"][2] + 10
                        y = (span["bbox"][1] + span["bbox"][3]) / 2
                        page.insert_text((x, y), date_str,
                                         fontsize=font_size,
                                         color=font_color,
                                         fontname=font_name)
                        date_filled["entered"] = True
                        if verbose:
                            print(f"[Page {page_num}] Date inserted after 'ENTERED:'")

                    # Match line starting with "Date:"
                    if not date_filled["date"] and full_line.startswith("Date:"):
                        x = span["bbox"][2] + 10
                        y = (span["bbox"][1] + span["bbox"][3]) / 2
                        page.insert_text((x, y), date_str,
                                         fontsize=font_size,
                                         color=font_color,
                                         fontname=font_name)
                        date_filled["date"] = True
                        if verbose:
                            print(f"[Page {page_num}] Date inserted after 'Date:'")

                if all(date_filled.values()):
                    break
            if all(date_filled.values()):
                break
        if all(date_filled.values()):
            break

    # Save output
    doc.save(output_path)
    doc.close()
    if verbose:
        print(f"✔ PDF saved to {output_path}")


# Example usage
if __name__ == "__main__":
    try:
        insert_date_into_pdf(
            pdf_path="output_filled.pdf",
            output_path="final_with_custom_font.pdf",
            date_str=None,  # or '2025-04-14'
            font_size=12,
            font_color=(0, 0, 0),
            font_name="times-roman",
            verbose=True
        )
    except Exception as e:
        print(f"⚠ Error: {e}", file=sys.stderr)
