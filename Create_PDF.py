import csv
import cv2
import os
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm


total_height = A4[1]
total_width  = A4[0]
top    = A4[1]
bottom = 0
right  = A4[0]
left   = 0
margin = .5*cm
nrow   = 5
ncol   = 2
card_height = total_height/nrow
card_width  = total_width /ncol
l_text1 = .70*card_width
l_text2 = .90*card_width
text1_font = "Helvetica"
text1_size = 10
line_height_text1 = text1_size*1.125
text2_font = "Times-Italic"
text2_size = 10
temppdf = "hello2.pdf"
basepdf = "base.pdf"
outpdf  = "AA_out.pdf"
tempimgbase = "temp.jpg"

def write_top_to_bottom(self, text_x, text_y, text):
    
    self.rotate(-90)
    self.drawCentredString(-text_y, text_x, text)
    self.rotate(90)
Canvas.write_top_to_bottom = write_top_to_bottom

def write_bottom_to_top(self, text_x, text_y, text):
    
    self.rotate(90)
    self.drawCentredString(text_y, -text_x, text)
    self.rotate(-90)
Canvas.write_bottom_to_top = write_bottom_to_top

def write_bottom_to_top_lines(self, text_x, text_y, text, line_height):
    
    lines = text.split("\n")
    delta = 0
    for line in lines:
        write_bottom_to_top(self, text_x + delta, text_y, line)
        delta = delta + line_height
Canvas.write_bottom_to_top_lines = write_bottom_to_top_lines

#leitura de dados
with open('CartonsZoo.csv', newline='') as csvfile:
    data = list(csv.reader(csvfile))

n = 0

canvas1 = Canvas(temppdf, pagesize=A4)

while n < len(data):
    for row in range(nrow):
        for col in range(ncol):
            card_origin_x = left + col * card_width
            card_origin_y = bottom + row * card_height
            #text 1
            text1_x = card_origin_x + l_text1
            text1_y = card_origin_y + card_height / 2
            text1 = data[n][1]
            canvas1.setFont(text1_font, text1_size)
            canvas1.write_bottom_to_top_lines(text1_x,text1_y,text1,line_height_text1)
            #text 2
            text2_x = card_origin_x + l_text2
            text2_y = card_origin_y + card_height / 2
            text2 = data[n][0]
            canvas1.setFont(text2_font, text2_size)
            canvas1.write_top_to_bottom(text2_x,text2_y,text2)
            #rotate image
            image_path = data[n][4]
            tempimg = str(n) +tempimgbase
            image = cv2.imread(image_path)
            rotated_image = cv2.rotate(image, 2)
            cv2.imwrite(tempimg, rotated_image)
            #tamanho e pos imagem
            image_px_y, image_px_x, image_chanels = rotated_image.shape
            if  image_px_x/image_px_y < 1.25:
                image_width  = card_height - 2*margin
                image_height = image_px_x*image_width/image_px_y
                image_pos_x  = card_origin_x + margin
                image_pos_y  = card_origin_y + margin
            else:
                image_height = 1.25*(card_height - 2*margin)
                image_width  = image_px_y*image_height/image_px_x
                image_pos_x  = card_origin_x + margin
                image_pos_y  = card_origin_y + (card_height-image_width)/2
            canvas1.drawImage(tempimg, image_pos_x, image_pos_y, image_height, image_width)
            os.remove(tempimg)

            n = n+1
    canvas1.showPage()
canvas1.save()


#Meging
# Get the data
reader_base = PdfReader(basepdf)
reader = PdfReader(temppdf)
writer = PdfWriter()
# merge
for page_box in reader.pages:
    page_box.merge_page(reader_base.pages[0])
    writer.add_page(page_box)

# Write the result back
with open(outpdf, "wb") as fp:
    writer.write(fp)
os.remove(temppdf)
