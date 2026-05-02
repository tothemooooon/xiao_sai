# -*- coding: utf-8 -*-
from docx import Document

doc = Document("E:/code/model/token.docx")
for p in doc.paragraphs:
    if p.text.strip():
        print(p.text)
