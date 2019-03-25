# -*- coding: utf-8 -*-
import scrapy
import unidecode
import re


class RosaSpider(scrapy.Spider):
    name = 'rosa'
    allowed_domains = ['inter03.tse.jus.br']
    start_urls = ['http://inter03.tse.jus.br/sadpPush/ExibirDadosProcesso.do?nprot=89242000&comboTribunal=tse']

    regexDict = {
        "process_number": r'([0-9-.]*[0-9-.])\d+',
        "municipio": r'([A-z]*.*[-]+)',
        "uf": r'(\b[A-z]{2}\b)'
    }
    
    inc = 1

    numproc = ""
    municipio = ""
    uf = ""

    def parse(self, response):
        for processo in response.xpath("//table"):
            reset_attributes(self)

            try:
                for item in processo.xpath("//tr"):
                    print(item.xpath(".//td/b/text()").get())
                    try:
                        selector = item.xpath(".//td/b/text()").getall()
                        for label in selector:
                            label = parse_text(label)

                            if(label is not None):
                                get_corresponding_attribute(self, label, item)
                    except TypeError:
                        continue

                yield {
                    'processo_num': self.numproc, #processo.xpath("//tr/td[1]/b/text()").get(),
                    'municipio': self.municipio,
                    'uf': self.uf
                }
            except TypeError as t:
                print("error:")
                print(t)
                continue
            

        next_page_url = f'http://inter03.tse.jus.br/sadpPush/ExibirDadosProcesso.do?nprot={self.inc}&comboTribunal=tse'
        self.inc += 1
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

def reset_attributes(self):
    self.numproc = ""
    self.municipio = ""
    self.uf = ""

def get_corresponding_attribute(self, selector, current_element):
    if("PROCESSO" in selector):
        self.numproc = current_element.xpath(".//td/text()").re(self.regexDict["process_number"])[0]
    elif("MUNICIPIO" in selector):
        self.municipio = current_element.xpath(".//td/text()").getall()
        self.municipio = unidecode_all(self.municipio)
        self.municipio = remove_special_characters_all(self.municipio)
        self.municipio = extract_string_from_list(self.municipio, self.regexDict["municipio"])
    elif("UF" in selector):
        self.uf = current_element.xpath(".//td/text()").getall()
        self.uf = unidecode_all(self.uf)
        self.uf = remove_special_characters_all(self.uf)
        self.uf = extract_string_from_list(self.uf, self.regexDict["uf"])


def parse_text(text):
    if(text is not None):
        text = unidecode.unidecode(text.replace(":","").strip())
        return text
    else:
        return None

def unidecode_all(str_arr):
    decoded_arr = []
    for word in str_arr:
        decoded_arr.append(unidecode.unidecode(word))
    
    return decoded_arr

def remove_special_characters_all(str_arr):
    clean_arr = []
    for word in str_arr:
        clean_arr.append(word.replace("\n","").replace("\t","").strip())
    
    return clean_arr

def extract_string_from_list(arr, regex):
    str_matches = []
    regex = re.compile(regex)
    matches = [x for x in arr if regex.match(x)]

    for match in matches:
        str_matches.append(match)
        if(match is not matches[-1]):
            str_matches.append(",")

    return "".join(str_matches)