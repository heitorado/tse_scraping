# -*- coding: utf-8 -*-
import scrapy
import unidecode
import re


class RosaSpider(scrapy.Spider):
    name = 'rosa'
    allowed_domains = ['inter03.tse.jus.br']
    start_urls = ['http://inter03.tse.jus.br/sadpPush/ExibirDadosProcesso.do?nprot=89242000&comboTribunal=tse']

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

    test_prot_codes = [100011996,100011997,100012016,10002011,10002012,10002016,100022015,100032007,100032016,100042006,100042016,100062003,100062008,100062009,100072004,100082004,100082015,100102003,100102012,100112011,10012011,100121998,100122005,100151996,100152001,100162010,100162016,100172004,100172014,100172016,100182003,100191998,1002002,100202013,10021960,10022010,10022016,100222006,100222011,100222016,100232011,100232016,100242011,100242016,100251997,100252009,100252011,100261992,100262003,100262011,100272007,100281998,100282008,100292001,100292016,100301996,100302003,100302004,100312002,100312003,10031990,10031998,10032000,10032017,100321995,100322003,100332001,100332003,100332006,100342000,100342001,100342007,100351998,100352001,100352012,100361996,100362006,100371996,100371997,100402003,100402005,10042000,10042007,10042017,100422003,100422005,100432006,100441997,100462004,100472014,100482005,100492003,100492011,100492012,100502003,100502011,10052016,100532011,100542008,100551989,100551998,100561997,100562004,100562012,100571997,100582004,100602004,100602014,100612004,10062003,10062011,10062017,100622005,100622007,100622013,100631998,100632004,100632015,100652004,100652013,100661990,100662009,100681998,100682004,100682016,100691998,100692004,100692008,100692012,100692016,100702009,100702012,100702015,100712013,10071994,10072007,100722006,100722012,100732002,100732016,100741998,100742002,100742006,100742014,100751998,100761998,100762006,100771997,100771998,100772009,100792004,100802004,100811996,10082016,100832001,100832006,100832008,100842004,100842006,100842011,100842016,100851995,100852004,100872006,100892007,100892015,100902012,100902014,100911989,100912001,100912008,100912014,100912016,10091998,10092006,10092016,100922008,100922011,100922014,100922016,100932016,100941998,100942004,100942016,100952001,100952016,100962014,100962016,100972006,100982002,100982013,100992007,10102006,10102017,101022004,101022012,101032004,101042002,101042005,101042009,101042012,101042013,101042015,101051998,101052004,101052013,101061994,101061995,101062004,101062006,101072006,101072014,101072015,101081998,101082008,101082015,101091997,101091998,101092012,101092015,101102006,101112016,10112016,101122010,101122016,101131995,101132010,101142001,101142011,101152003,101152004,101162002,101162003,101172002,101172009,101172014,101181997,101182014,101182015,1011999,101212003,10122006,10122009,10122013,101222008,101232015,101242008,101242009,101252001,101271998,101282001,101292006,101302003,101302009,101312009,101312010,101312011,10132016,10132017,101322004,101331996,101332001,101332003,101332004,101332016,101341996,101341998,101342000,101342004,101351996,101351998,101362004,101372013,101372016,101381996,101382001,101382015,101382016,101391996,101392016,101401997,101402005,101402012,101402016,101412000,101412011,101412016,10141999,10142003,10142006,10142017,101422000,101422006,101431995,101432008,101442000,101452005,101452015,101472000,101481990,101482000,101482005,101482007,101492000,101492012,101501996,101502008,101512005,101512013,10152003,10152006,101531996,101532003,101532008,101541998,101542004,101542006,101542008,101551998,101562006,101562011,101572000,101572003,101572006,101581996,101582008,101591992,101591998,101592008,101592010,101601998,101602000,101602004,101602014,101611998,101612000,101612004,10161998,10162003,10162014,10162017,101622000,101622004,101622005,101622010,101622012,101631994,101632004,101642000,101642004,101642009,101642016,101651998,101652000,101652004,101652012,101681997,101702000,101702003,101702004,101712013,10171998,10172003,10172018,101722003,101722011,101731998,101732004,101732012,101732016,101742016,101751998,101752012,101761998,101762012,101762016,101772006,101781998,101782000,101791997,101791998,101792006,101801997,101801998,101802012,101811992,101811998,101812005,101812006,101812013,10182006,10182007,101821990,101821998,101832003,101832004,101842005,101852005,101862010,101862016]    
    inc = 1

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
                print(item.xpath(".//td/b/text()").get())
                try:
                    selector = item.xpath(".//td/b/text()").getall()
                    for label in selector:
                        label = parse_text(label)

                        if(label is not None):
                            get_corresponding_attribute(self, label, item)
                except TypeError:
                    continue
            if(self.protocolo is not ""):
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
            # except TypeError as t:
            #     print("error:")
            #     print(t)
            #     continue
            

        next_page_url = f"http://inter03.tse.jus.br/sadpPush/ExibirDadosProcesso.do?nprot={self.test_prot_codes[self.inc]}&comboTribunal=tse"
        self.inc += 1
        if next_page_url is not None:
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
    elif ('RE' in selector):
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

