from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx_togglebutton import Toggle
import xml.etree.ElementTree as ET
import re
import os

"""
- custom directive to put SVG images with stylized text in the document (similar to PDF_TEX inkscape export)
"""


def get_text_from_svg(svg_file_path):
    # check if a pdf_tex file exists
    pdf_tex_path = svg_file_path[:-3] + 'pdf_tex'
    if not os.path.isfile(pdf_tex_path) or not os.path.isfile(svg_file_path):
        return None

    # read the pdf_tex content
    with open(pdf_tex_path, 'r') as file:
        # Read the entire content of the file into a string
        pdf_tex_content = file.read()

    # extract the texts from the svg
    svg_content = extract_and_remove_text(svg_file_path)

    # generate a matching between svg and pdf_tex
    try:
        coordinates = find_coordinates(latex_content=pdf_tex_content,
                                       svg_output=svg_content)

        return coordinates

    except:
        return None


def get_tspan_text(element):
    # Initialize an empty list to store the text
    text_list = []

    # If the element has text, add it to the list
    if element.text:
        text_list.append(element.text)

    # Iterate over each child element
    for child in element:
        # If the child is a tspan, recursively get its text
        if child.tag.endswith('tspan'):
            # If the tspan has a new line role, add a line break before the text
            if child.get('{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}role') == 'line':
                text_list.append('\\')

            text_list.extend(get_tspan_text(child))

        # If the child has a tail (text after a nested element), add it to the list
        if child.tail:
            text_list.append(child.tail)

    # Return the combined text
    return text_list


def extract_and_remove_text(svg_file_path):
    tree = ET.parse(svg_file_path)
    root = tree.getroot()

    # Define the SVG namespace
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    # Create a dictionary to map from child elements to their parents
    parent_map = {c: p for p in root.iter() for c in p}

    # Find all text elements in the SVG file
    text_elements = root.findall(".//svg:text", ns)

    svg_texts = []

    for text_element in text_elements:

        text_list = get_tspan_text(text_element)[1:]

        parent = parent_map.get(text_element)
        if parent is not None:
            parent.remove(text_element)

        svg_texts.append(text_list)

    # Save the modified SVG file
    mod_svg_file = svg_file_path[:-4] + '_txt_removed.svg'
    tree.write(mod_svg_file)

    return svg_texts


def find_coordinates(latex_content, svg_output):
    # get the picture dimension
    picture_pattern = r"\\begin{picture}\((.*?),(.*?)\)%"
    dimensions = re.findall(picture_pattern, latex_content, re.DOTALL)

    width, height = [float(item) for item in dimensions[0]]

    # Regular expression to match \put(x,y){...} in LaTeX
    put_pattern = r"\\put\((.*?),(.*?)\){(.*?)}%"

    # Find all \put commands in the LaTeX content
    put_commands = re.findall(put_pattern, latex_content, re.DOTALL)

    # Initialize an empty dictionary to store the coordinates
    coordinates = []

    # Iterate over the SVG output
    for text_list in svg_output:
        # Iterate over the \put commands
        for x, y, put_content in put_commands:

            # Initialize a variable to keep track of the start position for searching
            start_pos = put_content.find(r'\begin{tabular}', 0)

            # Assume initially that all items will be found in order
            all_found_in_order = True

            # Iterate over the items in the text_list
            for item in text_list:
                # Try to find the item in the put_content, starting from start_pos
                pos = put_content.find(item, start_pos)

                # If the item was found, update start_pos for the next search
                if pos != -1:
                    start_pos = pos + len(item)
                else:
                    # If the item was not found, set all_found_in_order to False and break the loop
                    all_found_in_order = False
                    break

            # If all items were found in order, store the coordinates
            if all_found_in_order:
                # coordinates[tuple(text_list)] = [float(x)/width, float(y)/height]
                coordinates.append([tuple(text_list), [float(x) / width, float(y) / height]])

    return coordinates


class SVGOverlayDirective(Directive):
    """
    Important! This directive only works when Sphinx is run from the root directory!
    """
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    option_spec = {
        'width': str,
        'path': str,
        'font-size': str,
    }
    has_content = False

    def run(self):
        svg_file = self.arguments[0]
        width = self.options.get('width', '100%')
        path = self.options.get('path', '')
        font_size = self.options.get('font-size', '0.9em')

        matches = get_text_from_svg('docs/source/' + svg_file)
        if matches is None:
            overlay_html = ''
            svg_src = os.path.join(path, svg_file)
        else:
            overlay_html = ''.join([
                f'''
                <div style="position: absolute; bottom: {item[1][1] * 100}%; left: {item[1][0] * 100}%;
                    transform: translateY(+0.5em);">
                    <code class="docutils literal notranslate" style="font-size: {font_size};">
                        <span class="pre">{''.join(item[0])}</span>
                    </code>
                </div>''' for item in matches])
            svg_src = os.path.join(path, svg_file[:-4] + '_txt_removed.svg')

        raw_html = f'''
        <div style="position: relative; width: {width}; display: inline-block;">
          <object data="{svg_src}" type="image/svg+xml" style="width: 100%; height: auto; display: block;"></object>
          {overlay_html}
       </div>
        '''

        # <img src="{svg_src}" style="width: 100%; height: auto; display: block;">

        return [nodes.raw('', raw_html, format='html')]




def setup(app):
    app.add_directive('svgoverlay', SVGOverlayDirective)



