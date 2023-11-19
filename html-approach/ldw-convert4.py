import pdfminer.high_level
import pdfminer.layout
import pdfminer.pdfpage
import pdfminer.pdfinterp
import pdfminer.utils

def extract_columns(pdf_path, x_positions):
    with open(pdf_path, 'rb') as f:
        rsrcmgr = pdfminer.high_level.PDFResourceManager()
        device = pdfminer.high_level.PDFPageAggregator(rsrcmgr, laparams=pdfminer.layout.LAParams())
        interpreter = pdfminer.pdfinterp.PDFPageInterpreter(rsrcmgr, device)
        for page in pdfminer.pdfdocument.PDFDocument.get_pages(f):
            interpreter.process_page(page)
            page_layout = device.get_page_layout()
            for element in page_layout:
                if isinstance(element, pdfminer.layout.LTTextBox):
                    text = element.get_text()
                    x0, y0, x1, y1 = element.bbox
                    if y0 == y1:
                        for x_position in x_positions:
                            if x0 <= x_position <= x1:
                                print(text)

if __name__ == '__main__':
    pdf_path = 'BPD-IAD-complaints-2019.pdf'
    x_positions = [100, 200, 300]
    extract_columns(pdf_path, x_positions)

