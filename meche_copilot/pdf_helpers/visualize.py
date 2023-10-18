import io
import fitz
import matplotlib.pyplot as plt
from pydantic import BaseModel
from PIL import Image


red = (1, 0, 0)
blue = (0, 0, 1)
gold = (1, 1, 0)
green = (0, 1, 0)

class PdfPlotter(BaseModel):
  """Show a PDF page as img using matplotlib."""

  @classmethod
  def save(cls, fpath: str, page: fitz.Page, clip=None, scale_factor=1.0):
    mat = fitz.Matrix(scale_factor, scale_factor)
    page.get_pixmap(clip=clip, matrix=mat)
    pix = page.get_pixmap()
    img_data = pix.tobytes()
    img = Image.open(io.BytesIO(img_data))
    img.save(fpath)

  @classmethod
  def show(cls, page: fitz.Page, clip=None, scale_factor=1.0):
    mat = fitz.Matrix(scale_factor, scale_factor)
    page.get_pixmap(clip=clip, matrix=mat)
    pix = page.get_pixmap()
    img_data = pix.tobytes()
    img = Image.open(io.BytesIO(img_data))
    plt.imshow(img)
    plt.axis('off') # To turn off axes
    plt.show()

  @classmethod
  def visualize_blocks(cls, page: fitz.Page):
    # visialize blocks by highlighting them
    blocks = page.get_text_blocks()
    for block in blocks:
      highlight_rect(page, fitz.Rect(block[0], block[1], block[2], block[3]), f"{block[5],block[6]}")
    cls.show(page)

  @classmethod
  def visualize_lines(cls, page: fitz.Page):
      # visualize stroke/line drawings by highlighting them
      drawings = page.get_drawings()
      for d in drawings:
        if d['type'] == 's':
          highlight_line(page, d['items'][0][1], d['items'][0][2])
      cls.show(page)

def highlight_rect(page: fitz.Page, rect: fitz.Rect, text: str = "", color=gold) -> fitz.Page:
    shape = page.new_shape()
    shape.draw_rect(rect)
    shape.finish(width = 0.5, color=red, fill = color, stroke_opacity=0.5, fill_opacity=0.5)
    fontsize=rect.height/2
    shape.insert_text(rect.br, text, color = (0,0,1), fontsize=fontsize)
    shape.commit()
    return page

def outline_rect(page: fitz.Page, rect: fitz.Rect, text: str = "", color=red) -> fitz.Page:
    shape = page.new_shape()
    shape.draw_rect(rect)
    shape.finish(width = 0.5, color=color, fill = None, stroke_opacity=0.5, fill_opacity=0.5)
    fontsize=rect.height/2
    shape.insert_text(rect.br, text, color = (0,0,1), fontsize=fontsize)
    shape.commit()
    return page

def highlight_line(page: fitz.Page, p1: fitz.Point, p2: fitz.Point, text: str = "") -> fitz.Page:
    shape = page.new_shape()
    shape.draw_line(p1, p2)
    color = red
    if p1.x == p2.x: # horizontal
      color = blue
    shape.finish(width = 1.0, color=color, fill = color, stroke_opacity=0.5, fill_opacity=0.5)
    # shape.insert_textbox(p1, text, color = (0,0,1))
    shape.commit()
    return page