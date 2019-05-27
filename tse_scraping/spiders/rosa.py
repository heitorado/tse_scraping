# -*- coding: utf-8 -*-
import scrapy
import unidecode
import re
import collections


class RosaSpider(scrapy.Spider):
    # Initial Spider Configuration. We set its name, the allowed domains for it to crawl and the first URL to be used.
    # We are currently setting the starting url to an invalid one (no process has protocol number '1'), but on subsequent
    # requests we change the protocol number dynamically.
    name = 'rosa'
    allowed_domains = ['inter03.tse.jus.br']
    start_urls = ['http://inter03.tse.jus.br/sadpPush/ExibirDadosProcesso.do?nprot=1&comboTribunal=tse']

    # Here we have our regexes for each labeled data. Each one is crafted with the specific purpose of matching the shape (not always, but
    # I've tried to be as generic as possible, that is, to cover the most cases) of the
    # string that is stored under that label
    regexDict = {
        "process_number": r'(\d*-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})',
        "municipio": r'(^[^-]*[^ -])',
        "uf": r'(\b[A-Z]{2}\b$)',
        "protocol_number": r'(^[0-9]+)',
        "date": r'(\d{1,2}\/\d{1,2}\/\d{4})',
        "time": r'(\d{1,2}:\d{1,2})',
        "more_than_two": r'(\b\w{3}\w*\b)',            # For matching more than 2 characters. Useful for the "idenficacao" field.
        "anything": r'(.+)',
        "uf_initials_text_end": r'( *[A-z]*$)'
    }

    # Here we have some hardcoded parameters. The thing is, protocols on the TSE website follow this pattern:
    # {number}{year}, for example 12008, 22008, 32008 represents the three first data that received a protocol number at the year 2008.
    # 
    # We will limit the {number} to grow until it reaches 60000, since we empirically tested that there are no more that 60000
    # data inserted each year on the TSE website. 
    # 
    # In short, we will search each year starting from 1, like:
    # 12008, 22008, 32008 ... until we reach 600002008. Then we go forward to next year and start from 1 again.
    # We will get data from 2008 (inclusive) to 2019 (exclusive)
    req_protocol_number = 1
    req_protocol_number_limit = 60000
    req_protocol_year = 2008
    req_protocol_year_limit = 2019

    # Process metadata - These are data that identifies or talk about the process in some manner. Where it was created, who started it, etc.
    identificacao = ""
    numproc = ""
    numprocvinculado = ""
    municipio = ""
    uf = ""
    protocolo = ""
    representantes = "" 
    representados = ""
    relator = "" 
    assunto = "" 
    localizacao = "" 
    fase_atual = ""
    

    # Possible parts names in the process - That is, the titles the active and passive poles can take in an electoral dispute.
    apelantes = []
    apelados = []
    agravantes = []
    agravados = []
    recorrentes = []
    recorridos = []
    embargantes = []
    embargados = []
    impetrantes = []
    impetrados = []
    requerentes = []
    requeridos = []
    reclamantes = []
    reclamados = []
    exequentes = []
    executados = []
    demandantes = []
    demandados = []
    denunciantes = []
    denunciados = []
    excipientes = []
    exceptos = []
    querelantes = []
    querelados = []
    autores = []
    reus = []

    # Here we will generalize the parts independent of its title, just saying if its on the passive or active pole of the process.
    polo_ativo = []
    polo_passivo = []

    # Main Rosa method.
    def parse(self, response):
        for processo in response.xpath("//table"):
            reset_attributes(self)

            for item in processo.xpath("//tr"):
                try:
                    selector = item.xpath(".//td/b/text()").getall()
                    for label in selector:
                        label = parse_text(label)

                        if(label is not None):
                            get_corresponding_attribute(self, label, item)
                except TypeError:
                    continue
            if(self.protocolo != ""):
                yield {
                    'identificacao': parse_identificacao(self),
                    'num_processo': extract_literal_regex_only(self.numproc, self.regexDict["process_number"]),
                    'num_processo_vinculado': extract_literal_regex_only(self.numprocvinculado, self.regexDict["process_number"]),
                    'municipio': extract_literal_regex_only(self.municipio, self.regexDict["municipio"]),
                    'uf': self.uf,
                    'protocolo': {
                        'numero': extract_literal_regex_only(self.protocolo, self.regexDict["protocol_number"]),
                        'data': extract_literal_regex_only(self.protocolo, self.regexDict["date"]),
                        'hora': extract_literal_regex_only(self.protocolo, self.regexDict["time"])
                    },
                    'partes': {
                        'representantes': list(flatten(self.representantes)),
                        'representados': list(flatten(self.representados)),

                        'apelantes': list(flatten(self.apelantes)),
                        'apelados': list(flatten(self.apelados)),

                        'agravantes': list(flatten(self.agravantes)),
                        'agravados': list(flatten(self.agravados)),

                        'recorrentes': list(flatten(self.recorrentes)),
                        'recorridos': list(flatten(self.recorridos)),

                        'embargantes': list(flatten(self.embargantes)),
                        'embargados': list(flatten(self.embargados)),

                        'impetrantes': list(flatten(self.impetrantes)),
                        'impetrados': list(flatten(self.impetrados)),

                        'requerentes': list(flatten(self.requerentes)),
                        'requeridos': list(flatten(self.requeridos)),

                        'reclamantes': list(flatten(self.reclamantes)),
                        'reclamados': list(flatten(self.reclamados)),

                        'exequentes': list(flatten(self.exequentes)),
                        'executados': list(flatten(self.executados)),

                        'demandantes': list(flatten(self.demandantes)),
                        'demandados': list(flatten(self.demandados)),

                        'denunciantes': list(flatten(self.denunciantes)),
                        'denunciados': list(flatten(self.denunciados)),

                        'excipientes': list(flatten(self.excipientes)),
                        'exceptos': list(flatten(self.exceptos)),

                        'querelantes': list(flatten(self.querelantes)),
                        'querelados': list(flatten(self.querelados)),

                        'autores': list(flatten(self.autores)),
                        'reus': list(flatten(self.reus)),

                        'polos': {
                            'polo_ativo': list(flatten(self.polo_ativo)),
                            'polo_passivo': list(flatten(self.polo_passivo))
                        }
                    },
                    'relator': extract_matching_string_from_list(self.relator, self.regexDict["anything"]),
                    'assunto': extract_literal_regex_only(self.assunto, self.regexDict["anything"]),
                    'localizacao': extract_literal_regex_only(self.localizacao, self.regexDict["anything"]),
                    'fase_atual': {
                        'data_ultima_atualizacao': extract_literal_regex_only(self.fase_atual, self.regexDict["date"]),
                        'hora_ultima_atualizacao': extract_literal_regex_only(self.fase_atual, self.regexDict["time"]),
                        'comentario': parse_commentary(self),
                    },
                    'url': response.request.url
                }
            
        # Crawling logic:
        # We increment the number that precedes the year by one but don't let it above the threshold we set earlier.
        # If it reaches the threshold, it will be set to 0 and then the year will be incremented by one,
        # sucessfully restarting the cycle.
        self.req_protocol_number = (self.req_protocol_number + 1) % self.req_protocol_number_limit
        if(self.req_protocol_number == 0):
            self.req_protocol_year += 1
        
        # Our next page will always be the number + year, that we get from the previous crawling logic operation.
        next_page_url = f"http://inter03.tse.jus.br/sadpPush/ExibirDadosProcesso.do?nprot={ str(self.req_protocol_number) + str(self.req_protocol_year) }&comboTribunal=tse"
        
        # But if our next page is a None object or if the protocol year is equal to the year limit we set earlier, the scraping stops.
        if((next_page_url is not None) and (self.req_protocol_year != self.req_protocol_year_limit)):
            yield scrapy.Request(response.urljoin(next_page_url))

def reset_attributes(self):
    # Process metadata
    self.identificacao = ""
    self.numproc = ""
    self.numprocvinculado = ""
    self.municipio = ""
    self.uf = ""
    self.protocolo = ""
    self.relator = "" 
    self.assunto = "" 
    self.localizacao = "" 
    self.fase_atual = ""

    # Possible parts names in the process
    self.representantes = [] 
    self.representados = []
    self.apelantes = []
    self.apelados = []
    self.agravantes = []
    self.agravados = []
    self.recorrentes = []
    self.recorridos = []
    self.embargantes = []
    self.embargados = []
    self.impetrantes = []
    self.impetrados = []
    self.requerentes = []
    self.requeridos = []
    self.reclamantes = []
    self.reclamados = []
    self.exequentes = []
    self.executados = []
    self.demandantes = []
    self.demandados = []
    self.denunciantes = []
    self.denunciados = []
    self.excipientes = []
    self.exceptos = []
    self.querelantes = []
    self.querelados = []
    self.autores = []
    self.reus = []

    # Parts generalization
    self.polo_ativo = []
    self.polo_passivo = []

def get_corresponding_attribute(self, selector, current_element):
    # Here we will scrape the variables corresponding to the process metadata.
    if("IDENTIFICACAO" in selector):
        self.identificacao = current_element.xpath(".//td/text()").getall()
        self.identificacao = unidecode_all(self.identificacao)
        self.identificacao = remove_special_characters_all(self.identificacao)
        self.identificacao = remove_empty_strings(self.identificacao)
    elif("PROCESSO" in selector and "VINCULADO" not in selector):
        self.numproc = current_element.xpath(".//td/text()").getall()
        self.numproc = unidecode_all(self.numproc)
        self.numproc = remove_special_characters_all(self.numproc)
        self.numproc = remove_empty_strings(self.numproc)
    elif("PROCESSO" in selector and "VINCULADO" in selector):
        self.numprocvinculado = current_element.xpath(".//td/text()").getall()
        self.numprocvinculado = unidecode_all(self.numprocvinculado)
        self.numprocvinculado = remove_special_characters_all(self.numprocvinculado)
        self.numprocvinculado = remove_empty_strings(self.numprocvinculado)
    elif("MUNICIPIO" in selector):
        self.municipio = current_element.xpath(".//td/text()").getall()
        self.municipio = unidecode_all(self.municipio)
        self.municipio = remove_special_characters_all(self.municipio)
        self.municipio = remove_empty_strings(self.municipio)
    elif("UF" in selector):
        self.uf = current_element.xpath(".//td/text()").getall()
        self.uf = unidecode_all(self.uf)
        self.uf = remove_special_characters_all(self.uf)
        self.uf = extract_matching_string_from_list(self.uf, self.regexDict["uf"])
    elif("PROTOCOLO" in selector):
        self.protocolo = current_element.xpath(".//td/text()").getall()
        self.protocolo = remove_special_characters_all(self.protocolo)
        self.protocolo = remove_empty_strings(self.protocolo)
    elif("RELATOR" in selector):
        self.relator = current_element.xpath(".//td/text()").getall()
        self.relator = unidecode_all(self.relator)
        self.relator = remove_special_characters_all(self.relator)
        self.relator = remove_empty_strings(self.relator)
    elif("ASSUNTO" in selector):
        self.assunto = current_element.xpath(".//td/text()").getall()
        self.assunto = unidecode_all(self.assunto)
        self.assunto = remove_special_characters_all(self.assunto)
        self.assunto = remove_empty_strings(self.assunto)
    elif("LOCALIZAC" in selector):
        self.localizacao = current_element.xpath(".//td/text()").getall()
        self.localizacao = unidecode_all(self.localizacao)
        self.localizacao = remove_special_characters_all(self.localizacao)
        self.localizacao = remove_empty_strings(self.localizacao)
    elif("FASE" in selector):
        self.fase_atual = current_element.xpath(".//td/text()").getall()
        self.fase_atual = unidecode_all(self.fase_atual)
        self.fase_atual = remove_special_characters_all(self.fase_atual)
        self.fase_atual = remove_empty_strings(self.fase_atual)

    # Now we scrape the process parts
    elif("REPRESENTANT" in selector):
        self.representantes.append(get_and_sanitize_string(current_element, self.representantes))
        self.polo_ativo = self.representantes
    elif("REPRESENTAD" in selector):
        self.representados.append(get_and_sanitize_string(current_element, self.representados))
        self.polo_passivo = self.representados
    elif ('APELANT' in selector):
        self.apelantes.append(get_and_sanitize_string(current_element, self.apelantes))
        self.polo_ativo = self.apelantes
    elif ('APELAD' in selector): 
        self.apelados.append(get_and_sanitize_string(current_element, self.apelados))
        self.polo_passivo = self.apelados
    elif ('AGRAVANT' in selector):
        self.agravantes.append(get_and_sanitize_string(current_element, self.agravantes))
        self.polo_ativo = self.agravantes
    elif ('AGRAVAD' in selector):
        self.agravados.append(get_and_sanitize_string(current_element, self.agravados))
        self.polo_passivo = self.agravados
    elif ('RECORRENT' in selector):
        self.recorrentes.append(get_and_sanitize_string(current_element, self.apelantes))
        self.polo_ativo = self.recorrentes
    elif ('RECORRID' in selector):
        self.recorridos.append(get_and_sanitize_string(current_element, self.recorridos))
        self.polo_passivo = self.recorridos
    elif ('EMBARGANT' in selector):
        self.embargantes.append(get_and_sanitize_string(current_element, self.embargantes))
        self.polo_ativo = self.embargantes
    elif ('EMBARGAD' in selector):
        self.embargados.append(get_and_sanitize_string(current_element, self.embargados))
        self.polo_passivo = self.embargados
    elif ('IMPETRANT' in selector):
        self.impetrantes.append(get_and_sanitize_string(current_element, self.impetrantes))
        self.polo_ativo = self.impetrantes
    elif ('IMPETRAD' in selector):
        self.impetrados.append(get_and_sanitize_string(current_element, self.impetrados))
        self.polo_passivo = self.impetrados
    elif ('REQUERENT' in selector):
        self.requerentes.append(get_and_sanitize_string(current_element, self.requerentes))
        self.polo_ativo = self.requerentes
    elif ('REQUERID' in selector):
        self.requeridos.append(get_and_sanitize_string(current_element, self.requeridos))
        self.polo_passivo = self.requeridos
    elif ('RECLAMANT' in selector):
        self.reclamantes.append(get_and_sanitize_string(current_element, self.reclamantes))
        self.polo_ativo = self.reclamantes
    elif ('RECLAMAD' in selector):
        self.reclamados.append(get_and_sanitize_string(current_element, self.reclamados))
        self.polo_passivo = self.reclamados
    elif ('EXEQUENT' in selector):
        self.exequentes.append(get_and_sanitize_string(current_element, self.exequentes))
        self.polo_ativo = self.exequentes
    elif ('EXECUTAD' in selector):
        self.executados.append(get_and_sanitize_string(current_element, self.executados))
        self.polo_passivo = self.executados
    elif ('DEMANDANT' in selector):
        self.demandantes.append(get_and_sanitize_string(current_element, self.demandantes))
        self.polo_ativo = self.demandantes
    elif ('DEMANDAD' in selector):
        self.demandados.append(get_and_sanitize_string(current_element, self.demandados))
        self.polo_passivo = self.demandados
    elif ('DENUNCIANT' in selector):
        self.denunciantes.append(get_and_sanitize_string(current_element, self.denunciantes))
        self.polo_ativo = self.denunciantes
    elif ('DENUNCIAD' in selector):
        self.denunciados.append(get_and_sanitize_string(current_element, self.denunciados))
        self.polo_passivo = self.denunciados
    elif ('EXCIPIENT' in selector):
        self.excipientes.append(get_and_sanitize_string(current_element, self.excipientes))
        self.polo_ativo = self.excipientes
    elif ('EXCEPT' in selector):
        self.exceptos.append(get_and_sanitize_string(current_element, self.exceptos))
        self.polo_passivo = self.exceptos
    elif ('QUERELANT' in selector):
        self.querelantes.append(get_and_sanitize_string(current_element, self.querelantes))
        self.polo_ativo = self.querelantes
    elif ('QUERELAD' in selector):
        self.querelados.append(get_and_sanitize_string(current_element, self.querelados))
        self.polo_passivo = self.querelados
    elif ('AUTOR' in selector):
        self.autores.append(get_and_sanitize_string(current_element, self.autores))
        self.polo_ativo = self.autores
    # Special case - If we use ('RE' in selector) the spider gets much more prone to misclassifying data by getting wrong labels such as
    # INTE[RE]SSADOS, COR[RE]GEDOR, et al
    # So we have to check SPECIFICALLY for the match, and we have the word REU for male subject and RE for female subject.
    # Considering the hypothetical case when the two subjects are mixed, we add a case for REU/RE and RE/REU (but these are theoretical, no examples found yet.)
    # All the other word matches are specific enough for not being misclassified.    
    elif (('REU' == selector) or ('RE' == selector) or ('REU/RE' == selector) or ('RE/REU' == selector)):
        self.reus.append(get_and_sanitize_string(current_element, self.reus))
        self.polo_passivo = self.reus
    

# Gets all the strings from the current "element" passed as parameter using the xpath(".//td/text()") and:
# - Unidecode everything
# - Remove special characters line \n \r \t
# - Remove all empty strings ("")
# The resulting string will be stored in the variable passed in the parameter 'var'
def get_and_sanitize_string(element, var):
    var = element.xpath(".//td/text()").getall()
    var = unidecode_all(var)
    var = remove_special_characters_all(var)
    var = remove_empty_strings(var)
    return var


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

def remove_empty_strings(arr):
    return [x for x in arr if x != ""]

def remove_special_characters_all(str_arr):
    clean_arr = []
    for word in str_arr:
        clean_arr.append(word.replace("\n","").replace("\t","").replace("\r","").strip())
    
    return clean_arr

def extract_matching_string_from_list(arr, regex):
    str_matches = []
    regex = re.compile(regex)
    matches = [x for x in arr if regex.match(x)]

    for match in matches:
        str_matches.append(match)
        if(match is not matches[-1]):
            str_matches.append(",")

    return "".join(str_matches)

def extract_literal_regex_only(text, regex):
    if( (isinstance(text, str) and text == "") or (text is None)):
        return ""
    
    if(isinstance(text, list)):
        text = " ".join(text)

    search_results = re.search(regex, text)
    if(search_results is not None):
        text = search_results.group(0)
    else:
        text = ""

    return text

def remove_first_regex_occurrence(text, regex):
    text_to_remove = extract_literal_regex_only(text, regex)
    return text.replace(text_to_remove,"",1)

def join_and_split_by_comma(str_arr):
    elements = "".join(str_arr)
    return elements.split(",")

# 
def parse_identificacao(self):
    self.identificacao = extract_literal_regex_only(self.identificacao, self.regexDict["anything"])
    self.identificacao = remove_first_regex_occurrence(self.identificacao, self.regexDict["uf_initials_text_end"])
    return self.identificacao.replace("&ordm;", "um.") 

# Specific for separating date and time from the "Fase Atual" field
def parse_commentary(self):
    text_arr = self.fase_atual
    commentary = extract_literal_regex_only(text_arr, self.regexDict["anything"])
    commentary = remove_first_regex_occurrence(commentary, self.regexDict["time"])
    commentary = remove_first_regex_occurrence(commentary, self.regexDict["date"])
    return commentary.replace("-","").strip()

def flatten(irregular_list):
    for elem in irregular_list:
        if isinstance(elem, collections.Iterable) and not isinstance(elem, (str, bytes)):
            yield from flatten(elem)
        else:
            yield elem
