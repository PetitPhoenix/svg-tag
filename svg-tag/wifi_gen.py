import io
import os
from text2svg import text_svg
from SVGprocess import SVG, read_svg
import qrcode
import qrcode.image.svg
# https://github.com/lincolnloop/python-qrcode

def QR_svg(network, password, protocol, hidden, box_size=10, border=0):
    # factory = qrcode.image.svg.SvgImage # Simple factory, just a set of rects
    # factory = qrcode.image.svg.SvgFragmentImage # Fragment factory (also just a set of rects)
    factory = qrcode.image.svg.SvgPathImage # Combined path factory, fixes white space that may occur when zooming   # Utilisez SvgPathImage pour un SVG compact
    #SvgSquareDrawer, SvgCircleDrawer, SvgPathSquareDrawer, or SvgPathCircleDrawer
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
        image_factory=factory,
    )
    
    qr.add_data(f'WIFI:T:{protocol};S:{network};P:{password};H:{hidden};;')
    qr.make(fit=True)
    img = qr.make_image()
    
    svg_io = io.BytesIO()
    img.save(svg_io)
    svg_string = svg_io.getvalue().decode('utf-8')
    
    # qr = qrcode.make(f'WIFI:T:{protocol};S:{network};P:{password};H:{hidden};;', 
    #                      image_factory=factory, 
    #                      box_size=box_size,
    #                      border=border)
    return svg_string

def QR_gen(network, password, protocol, hidden, text_elements, width_mm, height_mm, padding_mm):
    for element in text_elements:
        element['width'] = element['width']*(width_mm - 2 * padding_mm)
        element['height'] = element['height']*(height_mm - 2 * padding_mm)
        element['x'] = padding_mm
        element['y'] = element['y']*(height_mm - 2 * padding_mm) + padding_mm
    
    
    svg_instance = SVG()
    svg_instance.unit = 'mm'
    svg_instance.width = width_mm
    svg_instance.height = height_mm
    svg_instance.viewBox = [0, 0, width_mm, height_mm]
    
    for element in text_elements:
        font_path = f'../static/fonts/{element["font"].replace(".ttf", "")}/{element["font"]}'
        svg_data = text_svg(
            text=element['text'],
            font_path=font_path,
            font_size=element['fontsize'],
            zone_width=element['width'],
            zone_height=element['height'],
            x0=element['x'],
            y0=element['y']
        )
        svg_instance.add_group(svg_data.elements, translate=[0, 0], scale=1.0)
        # svg_instance.add_element("rect", {"x": element['x'], 
        #                               "y": element['y'], 
        #                               "width": element['width'],
        #                               "height": element['height'],
        #                               "stroke": "black", "fill": "none", "stroke-width": 0.1 }, 
        #                      {"translate": (0, 0), "scale": 1})
    
    qr_svg = QR_svg(network, password, protocol, hidden, box_size=10, border=0)
    qr_svg = SVG(qr_svg)
    scale = min((width_mm / 2 - 2 * padding_mm) / qr_svg.width, (height_mm / 2 - 2 * padding_mm) / qr_svg.height)
    svg_instance.add_group(qr_svg.elements, 
                           # translate=[width_mm / 2 + padding_mm, height_mm / 2 + padding_mm], 
                           translate=[width_mm * 3 / 4 - qr_svg.width * scale / 2, height_mm / 2 + padding_mm], 
                           scale=scale)
    
    wifi = read_svg(r'..\static\images\wifi.svg')
    wifi = SVG(wifi)
    scale = min((width_mm / 6) / wifi.width, (height_mm / 12) / wifi.height)
    svg_instance.add_group(wifi.elements, 
                           translate=[width_mm * 3 / 4 - wifi.width * scale / 2, height_mm / 2 - wifi.height * scale / 2], 
                           scale=scale)
    
    signal = read_svg(r'..\static\images\network.svg')
    signal = SVG(signal)
    scale = min((width_mm / 3 - 2 * padding_mm) / signal.width, (height_mm / 2 - 2 * padding_mm) / signal.height)
    svg_instance.add_group(signal.elements, 
                           translate=[width_mm * 2 / 3, height_mm / 4 - signal.height * scale / 2], 
                           scale=scale)
    
    return svg_instance
    
if __name__ == '__main__':
    # Paramètres de réseau
    network='Mon réseau'
    password='Mon mot de passe'
    protocol='WPA/WPA2'
    hidden='true'

    # Paramètres de la forme
    width_mm = 100
    height_mm = 100
    padding_mm = 5
    thk = 1
    x_mm = 0
    y_mm = 0
    
    text_elements = [
        {'text': 'Bienvenue', 'width': 2/3, 'height': 1/4, 'x': 0, 'y': 0, 'font': 'Southmore.ttf', 'fontsize': 30},
        {'text': 'Profitez du wifi', 'width': 2/3, 'height': 1/10, 'x': 0, 'y': 1/4, 'font': 'BillionDreams.ttf', 'fontsize': 20},
        {'text': 'Réseau', 'width': 1/2, 'height': 1/10, 'x': 0, 'y': 6/12, 'font': 'Stark.ttf', 'fontsize': 18},
        {'text': f'{network}', 'width': 1/2, 'height': 1/12, 'x': 0, 'y': 7.2/12, 'font': 'Kollektif.ttf', 'fontsize': 13},
        {'text': 'Mot de passe', 'width': 1/2, 'height': 1/10, 'x': 0, 'y': 9/12, 'font': 'Stark.ttf', 'fontsize': 18},
        {'text': f'{password}', 'width': 1/2, 'height': 1/12, 'x': 0, 'y': 10.2/12, 'font': 'Kollektif.ttf', 'fontsize': 13}
    ]
        
    filename = 'Commande_XYZ'
    folder = r'..\examples\outputs\wifi'
    
    svg_instance = QR_gen(network, password, protocol, hidden, text_elements, width_mm, height_mm, padding_mm)
    svg_instance.generate_svg_file(os.path.join(folder, filename + '.svg'))
    
