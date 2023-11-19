import tempfile
from io import StringIO
#import tabula
#import camelot
import pandas as pd
import numpy as np
#import pdftotext
from PIL import Image, ImageFont, ImageDraw
from pdf2image import convert_from_path
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import dataframe_image as dfi
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

pd.set_option('display.max_colwidth', None)

PDF = 'BPD-IAD-complaints-2019.pdf'
pdf_img = convert_from_path(PDF, dpi=300)[0]

#plt.figure(figsize=(15, 10))
#plt.axis('off')
#plt.imshow(pdf_img)


def adjust_string(s, out_width):
    """Pad string with whitespaces to the right.

    It wil make current string of the same length as longest
    string in a series. Needed further to evenly split strings
    into columns on a divider such as empty vertical-wise
    string through all the rows.
    """
    fill_width = out_width - len(s)
    s += ' ' * fill_width
    return s



pdfminer_string = StringIO()
with open(PDF, "rb") as in_file:
    parser = PDFParser(in_file)
    doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    device = TextConverter(rsrcmgr,
                           pdfminer_string,
                           laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)
pdfminer_lines = pdfminer_string.getvalue().splitlines()
pdfminer_lines = [ln for ln in pdfminer_lines if ln]


# get matrix with all elements of a string including spaces
# to further search for a vertical empty string through all the rows
pdf_lines = pd.Series(pdfminer_lines)
max_width = pdf_lines.str.len().max()
pdf_lines_adjusted = pdf_lines.apply(adjust_string, args=(max_width, ))
pdf_lines_mtx = np.stack(pdf_lines_adjusted.map(list).to_numpy())

# indicies of empty vertical strings as column dividers
whitespace_сols = np.where(np.all(pdf_lines_mtx == ' ', axis=0))[0]
rightmost_whitespace_cols = np.where(np.diff(whitespace_сols) != 1)[0]
column_dividers = np.append(whitespace_сols[rightmost_whitespace_cols],
                            whitespace_сols[-1])

# %%

df_mtx = pd.DataFrame(pdf_lines_mtx)
df_mtx_w_dividers = df_mtx.copy()

df_mtx_w_dividers.loc[:, column_dividers] = (df_mtx_w_dividers[column_dividers]
                                             .replace({' ': '\u2022'}))

fig, ax = plt.subplots(2, 1)
titles = ['char matrix ...', '... with rightmost column dividers']
for i, img in enumerate([make_df_image(d, max_cols=60)
                         for d in [df_mtx, df_mtx_w_dividers]]):
    ax[i].axis("off")
    ax[i].set_adjustable("box")
    ax[i].title.set_text(titles[i])
    ax[i].imshow(img)
fig.tight_layout()

# %%

splitted_lines = []
for row in pdf_lines_adjusted:
    current_row = []
    for e in range(len(column_dividers) - 1):
        if e == 0:
            current_row.append(row[: column_dividers[e]].strip())
        (current_row
         .append(row[column_dividers[e]: column_dividers[e + 1]]
                 .strip()))
    current_row.append(row[column_dividers[-1]:].strip())
    splitted_lines.append(current_row)

# %%

pdf_df = pd.DataFrame(splitted_lines)
empty_cols = (pdf_df == '').all()
pdf_df = pdf_df[pdf_df.columns[~empty_cols]]

plt.axis('off')
plt.imshow(make_df_image(pdf_df))

# %%

header_row = pdf_df.iloc[0, :].copy()
table_rows = pdf_df.iloc[1:, :].copy()

odd_rows = table_rows.iloc[::2].copy()
odd_rows.reset_index(drop=True, inplace=True)

evn_rows = table_rows[1::2].copy()
evn_rows.reset_index(drop=True, inplace=True)

evn_rows.replace({'': np.nan}, inplace=True)
evn_rows.dropna(axis=1, how='all', inplace=True)

all_rows = pd.concat([odd_rows, evn_rows], axis=1, sort=True)
all_rows.sort_index(axis=1, inplace=True)
all_rows.columns = all_rows.columns.astype(str)
all_rows.reset_index(drop=True, inplace=True)
all_rows.replace({np.nan: ''}, inplace=True)

fig, ax = plt.subplots(2, 1)
titles = ['original layout', 'flatten layout']
for i, img in enumerate(map(make_df_image, [table_rows, all_rows])):
    ax[i].axis("off")
    ax[i].set_adjustable("box")
    ax[i].title.set_text(titles[i])
    ax[i].imshow(img)
fig.tight_layout()

# %%

# columns with underscored indicies got from splitting original names by '/'
header_splitted = header_row.str.split('/')

header_indicies = []
for i, element in enumerate(header_splitted):
    if len(element) == 1:
        header_indicies.append(str(i))
    else:
        for j, w in enumerate(element):
            if j == 0:
                header_indicies.append(str(i))
            else:
                header_indicies.append('{}_{}'.format(i, j))

header_elements = [item for sublist in header_splitted
                   for item in sublist]

column_names = pd.Series(data=header_elements,
                         index=header_indicies)

# %%

all_rows.columns = add_postfix_after(all_rows.columns.astype(int).tolist())

plt.axis('off')
plt.imshow(make_df_image(all_rows, max_rows=3))


# %%

final_table = concat_cols_on_condition(table=all_rows,
                                       iterable=column_names.index,
                                       filter_func=lambda iterable, element:
                                           str(element) not in iterable)

final_table.columns = column_names[final_table.columns]

fig, ax = plt.subplots(2, 1)
titles = ['semi-structured data', 'structured data']
for i, img in enumerate([make_lines_image(pdfminer_lines),
                         make_df_image(final_table)]):
    ax[i].axis("off")
    ax[i].set_adjustable("box")
    ax[i].title.set_text(titles[i])
    ax[i].imshow(img)
fig.tight_layout()
