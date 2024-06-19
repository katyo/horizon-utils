#!/usr/bin/env python

import os.path
import argparse
import pypdf
import horizon

UNIT = 25.4 / 72

def mm2u(mm): return mm / UNIT
def u2mm(u): return u * UNIT

# Export PDFs
#
# Horizon-EDA Options:
# {
#   'layers': {
#     '-100': {'color': {b: 1.0, g: 1.0, r: 1.0}, enabled: False, mode: 'fill' },
#     '-110': {'color': {'b': 0.0, 'g': 0.0, 'r': 0.0}, 'enabled': True, 'mode': 'fill'},
#     '-120': {'color': {'b': 0.0, 'g': 0.0, 'r': 0.0}, 'enabled': False, 'mode': 'outline'},
#     '-130': {'color': {'b': 0.0, 'g': 0.0, 'r': 0.0}, 'enabled': False, 'mode': 'outline'},
#     '-140': {'color': {'b': 0.0, 'g': 0.0, 'r': 0.0}, 'enabled': False, 'mode': 'outline'},
#     '-150': {'color': {'b': 0.0, 'g': 0.0, 'r': 0.0}, 'enabled': False, 'mode': 'outline'},
#     '0': {'color': {'b': 1.0, 'g': 1.0, 'r': 1.0}, 'enabled': False, 'mode': 'fill'},
#     '10': {'color': {'b': 0.0, 'g': 0.0, 'r': 0.0}, 'enabled': False, 'mode': 'fill'},
#     '100': {'color': {'b': 1.0, 'g': 1.0, 'r': 1.0}, 'enabled': True, 'mode': 'fill'},
#     '10000': {'color': {'b': 0.0, 'g': 0.0, 'r': 0.0}, 'enabled': False, 'mode': 'fill'},
#     '110': {'color': {'b': 0.0, 'g': 0.0, 'r': 0.0}, 'enabled': False, 'mode': 'outline'},
#     '20': {'color': {'b': 0.0, 'g': 0.0, 'r': 0.0}, 'enabled': False, 'mode': 'outline'},
#     '30': {'color': {'b': 0.0, 'g': 0.0, 'r': 0.0}, 'enabled': False, 'mode': 'outline'},
#     '40': {'color': {'b': 0.0, 'g': 0.0, 'r': 0.0}, 'enabled': False, 'mode': 'outline'},
#     '50': {'color': {'b': 0.0, 'g': 0.0, 'r': 0.0}, 'enabled': False, 'mode': 'outline'},
#   },
#   'min_line_width': 0,
#   'holes_diameter': 200000,
#   'mirror': False,
#   'output_filename': 'export.pdf',
#   'reverse_layers': True,
#   'set_holes_size': True,
# }

LAYER_INDEX = {
    "HOLES": 10000,
    "TOP_NOTES": 200,
    "OUTLINE_NOTES": 110,
    "L_OUTLINE": 100,
    "TOP_COURTYARD": 60,
    "TOP_ASSEMBLY": 50,
    "TOP_PACKAGE": 40,
    "TOP_PASTE": 30,
    "TOP_SILKSCREEN": 20,
    "TOP_MASK": 10,
    "TOP_COPPER": 0,
    "IN1_COPPER": -1,
    "IN2_COPPER": -2,
    "IN3_COPPER": -3,
    "IN4_COPPER": -4,
    "IN5_COPPER": -5,
    "IN6_COPPER": -6,
    "IN7_COPPER": -7,
    "IN8_COPPER": -8,
    "BOTTOM_COPPER": -100,
    "BOTTOM_MASK": -110,
    "BOTTOM_SILKSCREEN": -120,
    "BOTTOM_PASTE": -130,
    "BOTTOM_PACKAGE": -140,
    "BOTTOM_ASSEMBLY": -150,
    "BOTTOM_COURTYARD": -160,
    "BOTTOM_NOTES": -200,
}

COLOR = {
    "WHITE": {"b": 1.0, "g": 1.0, "r": 1.0},
    "BLACK": {"b": 0.0, "g": 0.0, "r": 0.0},
}

class Exporter:
    def __init__(self, args):
        self.input = args.input
        self.output = args.output
        self.marker_pdf = args.marker_pdf

        self.field = mm2u(args.field)
        self.margin = mm2u(args.margin)
        self.border = mm2u(args.border)
        self.hole = mm2u(args.hole)
        self.rotate = args.rotate
        self.marker_offset = mm2u(args.marker_offset)
        self.paper = pypdf.PaperSize.A4

    def run(self):
        # open project
        self.prj = horizon.Project(self.input)

        # open board
        self.brd = self.prj.open_board()

        top_copper = self.merge_layers([
            self.get_layer("L_OUTLINE", mirror = True),
            self.get_layer("L_OUTLINE", mirror = True, outline = True, border = self.border),
            self.get_layer("TOP_COPPER", invert = True, mirror = True),
            self.get_layer("HOLES", mirror = True, hole = self.hole),
        ])

        bottom_copper = self.merge_layers([
            self.get_layer("L_OUTLINE"),
            self.get_layer("L_OUTLINE", outline = True, border = self.border),
            self.get_layer("BOTTOM_COPPER", invert = True),
            self.get_layer("HOLES", hole = self.hole),
        ])

        top_mask = self.merge_layers([
            self.get_layer("L_OUTLINE", mirror = True, outline = True, border = self.border),
            self.get_layer("L_OUTLINE", invert = True, mirror = True),
            self.get_layer("TOP_MASK", mirror = True),
        ])

        bottom_mask = self.merge_layers([
            self.get_layer("L_OUTLINE", outline = True, border = self.border),
            self.get_layer("L_OUTLINE", invert = True),
            self.get_layer("BOTTOM_MASK"),
        ])

        self.create_template([
            (top_copper, -1, 0),
            (bottom_copper, 1, 0),
            (top_mask, -1, 1),
            (bottom_mask, 1, 1),
        ])

    def find_file(self, path):
        if os.path.isfile(path):
            return path
        data_path = os.path.dirname(__file__)
        new_path = os.path.join(data_path, path)
        if os.path.isfile(new_path):
            return new_path
        new_path += '.pdf'
        if os.path.isfile(new_path):
            return new_path
        return path

    def get_layer(self, layer, invert = False, mirror = False, outline = False, border = 0.0, hole = 0.0):
        pdf_settings = self.brd.get_pdf_export_settings()
        pdf_settings['output_filename'] = self.output
        pdf_settings['min_line_width'] = border * 1000000
        pdf_settings['holes_diameter'] = hole * 1000000
        pdf_settings['set_holes_size'] = True
        pdf_settings['mirror'] = mirror

        for layer_index in pdf_settings['layers']:
            pdf_settings['layers'][layer_index] = {
                "color": COLOR["WHITE"],
                "enabled": False,
                "mode": "outline",
            }

        pdf_settings['layers'][LAYER_INDEX[layer]] = {
            "color": COLOR["WHITE"] if invert else COLOR["BLACK"],
            "enabled": True,
            "mode": "outline" if outline else "fill",
        }

        self.brd.export_pdf(pdf_settings)
        return pypdf.PdfReader(self.output)

    def merge_layers(self, layers):
        if len(layers) > 0:
            page = layers[0].pages[0]
            for layer in layers[1:]:
                page.merge_page(layer.pages[0])
            pdf = pypdf.PdfWriter()
            pdf.add_page(page)
            pdf.write(self.output)
            pdf.close()
            return pypdf.PdfReader(self.output)

    def create_template(self, layers):
        tpl_pdf = pypdf.PdfWriter()
        tpl_pdf.add_blank_page(pypdf.PaperSize.A4.width, pypdf.PaperSize.A4.height)
        tpl_page = tpl_pdf.pages[0]
        tpl_mbox = tpl_page.mediabox
        for (layer, x, y) in layers:
            page = layer.pages[0]
            mbox = page.mediabox
            page.add_transformation(pypdf.Transformation()
                                    .translate(-mbox.width / 2, -mbox.height / 2)
                                    .rotate(self.rotate if x < 0 else -self.rotate), True)
            mbox = page.mediabox
            trsf = pypdf.Transformation().translate(tpl_mbox.width / 2 + (mbox.width + self.margin) / 2 * x,
                                                    tpl_mbox.height - self.field - mbox.height / 2 -
                                                    (mbox.height + self.margin) * y)
            tpl_page.merge_transformed_page(page, trsf)
            if self.marker_pdf is not None:
                marker_pdf = pypdf.PdfReader(self.find_file(self.marker_pdf))
                marker_page = marker_pdf.pages[0]
                marker_mbox = marker_page.mediabox
                marker_page.add_transformation(pypdf.Transformation()
                                               .translate(-marker_mbox.width / 2, -marker_mbox.height / 2), True)
                for (x, y) in [(-mbox.width / 2 - self.marker_offset, -mbox.height / 2 - self.marker_offset),
                               (-mbox.width / 2 - self.marker_offset, mbox.height / 2 + self.marker_offset),
                               (mbox.width / 2 + self.marker_offset, mbox.height / 2 + self.marker_offset),
                               (mbox.width / 2 + self.marker_offset, -mbox.height / 2 - self.marker_offset)]:
                    tpl_page.merge_transformed_page(marker_page, trsf.translate(x, y))
        tpl_pdf.write(self.output)
        tpl_pdf.close()

def main():
    parser = argparse.ArgumentParser(prog='brd2tpl',
                                     description='Export horizon-eda board to photo template',
                                     epilog='See https://github.com/katyo/horizon-utils')

    parser.add_argument("input", type=str, help="Project to export")
    parser.add_argument("output", type=str, help="PDF file to export to")
    parser.add_argument("-f", "--field", type=float, help="The top field width (mm)", default=10)
    parser.add_argument("-m", "--margin", type=float, help="The margin distance (mm)", default=10)
    parser.add_argument("-b", "--border", type=float, help="The border width (mm)", default=0.5)
    parser.add_argument("-d", "--hole", type=float, help="The hole diameter (mm)", default=0.1)
    parser.add_argument("-r", "--rotate", type=float, help="The rotation angle (deg)", default=0)
    parser.add_argument("-c", "--marker-pdf", type=str, help="The PDF file to use as marker", default=None)
    parser.add_argument("-p", "--marker-offset", type=float, help="The marker to corner distance (mm)", default=2.0)

    args = parser.parse_args()

    Exporter(args).run()

if __name__ == "__main__":
    main()
