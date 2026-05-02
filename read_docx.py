# -*- coding: utf-8 -*-
import codecs
from docx import Document

doc = Document("E:/code/model/q.docx")
with open("E:/code/model/output.txt", "w", encoding="utf-8") as f:
    for p in doc.paragraphs:
        if p.text.strip():
            f.write(p.text + "\n")
print("Done")
