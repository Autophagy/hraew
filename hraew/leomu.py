# -*- coding: utf-8 -*-
import yaml
from os.path import dirname, join
import bleach
import re
from flask import url_for, render_template

class Lim(object):

    def __init__(self, key, name, head, body):
        self.key = key
        self.name = name
        self.head = head
        self.body = body

    def to_html(self):
        return self._parse_body()

    def _parse_body(self):
        elements = self.body.split('\n\n')
        html_elements = []

        for element in elements:
            ele_head = self._get_element_head(element)

            if ele_head.strip() == '[BILIÞ]':
                html_elements.append(self._create_image(element))
            else:
                # Just treat it as a paragraph
                html_elements.append(self._create_paragraph(element))

        return '\n'.join(html_elements)

    def _get_element_head(self, element):
        element_lines = element.split('\n')
        return element_lines[0]

    def _create_paragraph(self, element):
        paragraph_wrap = "<p>{0}</p>"
        element = bleach.clean(element)

        # Parse geþeodan
        geþeodanified_element = self._create_geþeodan(element)

        paragraph = paragraph_wrap.format(geþeodanified_element)
        return paragraph

    def _create_image(self, element):
        # Image tags will be in the form:
        # [BILIÞ]
        # [image.format :: optional caption]

        regex = '\[(.*?)\]'

        try:
            image_definition = element.split('\n')[1]
            image_definition = re.search(regex, image_definition).group(1)

            image_uri = ''
            image_alt = ''

            if '::' in image_definition:
                image_uri, image_alt = image_definition.split('::')
            else:
                image_uri = image_definition

            return render_template('bilith.html', lim_key=self.key,
                                                  image_uri=image_uri.strip(),
                                                  image_alt=image_alt.strip())
        except Exception:
            print("{0} is an invalid image definition.".format(image_definition))
            return ''

    def _create_geþeodan(self, element):
        # Geþeodan tags will be in the form
        # [GEÞEODAN :: uri :: geþeodan]

        def get_geþeodan_elements(geþeodan_string):
            try:
                if '::' in geþeodan_string:
                    geþeodan_uri, geþeodan_text = geþeodan_string.split('::')
                else:
                    geþeodan_uri = geþeodan_string
                    geþeodan_text = geþeodan_string
                return {'uri': geþeodan_uri.strip(),
                        'text': geþeodan_text.strip()}
            except Exception:
                print("{0} is an invalid getheodan definition.".format(geþeodan_string))

        regex = re.compile('\[GEÞEODAN :: (.*?)\]')

        # Create innan geþeodan
        element = regex.sub(lambda x: render_template('getheodan.html',
                            geþeodan=get_geþeodan_elements(x.group(1))), element)

        return element


with open(join(dirname(__file__), "leomu/leomu.yml"), "r") as leomu_yml:
    leomu = yaml.load(leomu_yml)
    for key, value in leomu.items():
        leomu[key] = Lim(key, value['name'], value['head'], value['body'])
