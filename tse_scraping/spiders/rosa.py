# -*- coding: utf-8 -*-
import scrapy
import unidecode
import re


class RosaSpider(scrapy.Spider):
    name = 'rosa'
    allowed_domains = ['inter03.tse.jus.br']
    start_urls = ['http://inter03.tse.jus.br/sadpPush/ExibirDadosProcesso.do?nprot=1&comboTribunal=tse']

    regexDict = {
        "process_number": r'(\d*-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})',
        "municipio": r'(^[^-]*[^ -])',
        "uf": r'(\b[A-Z]{2}\b$)',
        "protocol_number": r'(^[0-9]+)',
        "date": r'(\d{1,2}\/\d{1,2}\/\d{4})',
        "time": r'(\d{1,2}:\d{1,2})',
        "more_than_two": r'(\b\w{3}\w*\b)',            # For matching more than 2 characters. Useful for the "idenficacao" field.
        "anything": r'(.+)'
    }

    req_protocol_number = 1
    req_protocol_number_limit = 60000
    req_protocol_year = 2008
    req_protocol_year_limit = 2019

    # Metadados do processo
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
    

    # Possíveis nomes das Partes do Processo
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

    # Generalização das partes, separando em polo ativo ou passivo
    polo_ativo = []
    polo_passivo = []

    def parse(self, response):
        for processo in response.xpath("//table"):
            reset_attributes(self)

            # try:
            for item in processo.xpath("//tr"):
                #print(item.xpath(".//td/b/text()").get())
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
                    'identificacao': extract_literal_regex_only(self.identificacao, self.regexDict["more_than_two"]),
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
                        'representantes': self.representantes,
                        'representados': self.representados,

                        'apelantes': self.apelantes,
                        'apelados': self.apelados,

                        'agravantes': self.agravantes,
                        'agravados': self.agravados,

                        'recorrentes': self.recorrentes,
                        'recorridos': self.recorridos,

                        'embargantes': self.embargantes,
                        'embargados': self.embargados,

                        'impetrantes': self.impetrantes,
                        'impetrados': self.impetrados,

                        'requerentes': self.requerentes,
                        'requeridos': self.requeridos,

                        'reclamantes': self.reclamantes,
                        'reclamados': self.reclamados,

                        'exequentes': self.exequentes,
                        'executados': self.executados,

                        'demandantes': self.demandantes,
                        'demandados': self.demandados,

                        'denunciantes': self.denunciantes,
                        'denunciados': self.denunciados,

                        'excipientes': self.excipientes,
                        'exceptos': self.exceptos,

                        'querelantes': self.querelantes,
                        'querelados': self.querelados,

                        'autores': self.autores,
                        'reus': self.reus,

                        'polos': {
                            'polo_ativo': self.polo_ativo,
                            'polo_passivo': self.polo_passivo
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
            

        self.req_protocol_number = (self.req_protocol_number + 1) % self.req_protocol_number_limit
        if(self.req_protocol_number == 0):
            self.req_protocol_year += 1
        
        next_page_url = f"http://inter03.tse.jus.br/sadpPush/ExibirDadosProcesso.do?nprot={ str(self.req_protocol_number) + str(self.req_protocol_year) }&comboTribunal=tse"
        if((next_page_url is not None) and (self.req_protocol_year != self.req_protocol_year_limit)):
            yield scrapy.Request(response.urljoin(next_page_url))

def reset_attributes(self):
    # Metadados do processo
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

    # Possíveis nomes das partes do processo
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

    # Generalização das partes
    self.polo_ativo = []
    self.polo_passivo = []

def get_corresponding_attribute(self, selector, current_element):
    # Identificadores dos metadados do processo
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
    # Inicio da verificação das partes do processo
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

# Specific for separating date and time from the "Fase Atual" field
def parse_commentary(self):
    text_arr = self.fase_atual
    commentary = extract_literal_regex_only(text_arr, self.regexDict["anything"])
    commentary = remove_first_regex_occurrence(commentary, self.regexDict["time"])
    commentary = remove_first_regex_occurrence(commentary, self.regexDict["date"])
    return commentary.replace("-","").strip()

