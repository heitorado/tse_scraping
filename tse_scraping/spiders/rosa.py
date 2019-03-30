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
        "uf": r'(\b[A-z]{2}\b)',
        "protocol_number": r'(^[0-9]+)',
        "date": r'(\d{1,2}\/\d{1,2}\/\d{4})',
        "time": r'(\d{1,2}:\d{1,2})',
        "anything": r'(.+)'
    }

    test_prot_codes = [100011996,100011997,100012016,10002011,10002012,10002016,100022015,100032007,100032016,100042006,100042016,100062003,100062008,100062009,100072004,100082004,100082015,100102003,100102012,100112011,10012011,100121998,100122005,100151996,100152001,100162010,100162016,100172004,100172014,100172016,100182003,100191998,1002002,100202013,10021960,10022010,10022016,100222006,100222011,100222016,100232011,100232016,100242011,100242016,100251997,100252009,100252011,100261992,100262003,100262011,100272007,100281998,100282008,100292001,100292016,100301996,100302003,100302004,100312002,100312003,10031990,10031998,10032000,10032017,100321995,100322003,100332001,100332003,100332006,100342000,100342001,100342007,100351998,100352001,100352012,100361996,100362006,100371996,100371997,100402003,100402005,10042000,10042007,10042017,100422003,100422005,100432006,100441997,100462004,100472014,100482005,100492003,100492011,100492012,100502003,100502011,10052016,100532011,100542008,100551989,100551998,100561997,100562004,100562012,100571997,100582004,100602004,100602014,100612004,10062003,10062011,10062017,100622005,100622007,100622013,100631998,100632004,100632015,100652004,100652013,100661990,100662009,100681998,100682004,100682016,100691998,100692004,100692008,100692012,100692016,100702009,100702012,100702015,100712013,10071994,10072007,100722006,100722012,100732002,100732016,100741998,100742002,100742006,100742014,100751998,100761998,100762006,100771997,100771998,100772009,100792004,100802004,100811996,10082016,100832001,100832006,100832008,100842004,100842006,100842011,100842016,100851995,100852004,100872006,100892007,100892015,100902012,100902014,100911989,100912001,100912008,100912014,100912016,10091998,10092006,10092016,100922008,100922011,100922014,100922016,100932016,100941998,100942004,100942016,100952001,100952016,100962014,100962016,100972006,100982002,100982013,100992007,10102006,10102017,101022004,101022012,101032004,101042002,101042005,101042009,101042012,101042013,101042015,101051998,101052004,101052013,101061994,101061995,101062004,101062006,101072006,101072014,101072015,101081998,101082008,101082015,101091997,101091998,101092012,101092015,101102006,101112016,10112016,101122010,101122016,101131995,101132010,101142001,101142011,101152003,101152004,101162002,101162003,101172002,101172009,101172014,101181997,101182014,101182015,1011999,101212003,10122006,10122009,10122013,101222008,101232015,101242008,101242009,101252001,101271998,101282001,101292006,101302003,101302009,101312009,101312010,101312011,10132016,10132017,101322004,101331996,101332001,101332003,101332004,101332016,101341996,101341998,101342000,101342004,101351996,101351998,101362004,101372013,101372016,101381996,101382001,101382015,101382016,101391996,101392016,101401997,101402005,101402012,101402016,101412000,101412011,101412016,10141999,10142003,10142006,10142017,101422000,101422006,101431995,101432008,101442000,101452005,101452015,101472000,101481990,101482000,101482005,101482007,101492000,101492012,101501996,101502008,101512005,101512013,10152003,10152006,101531996,101532003,101532008,101541998,101542004,101542006,101542008,101551998,101562006,101562011,101572000,101572003,101572006,101581996,101582008,101591992,101591998,101592008,101592010,101601998,101602000,101602004,101602014,101611998,101612000,101612004,10161998,10162003,10162014,10162017,101622000,101622004,101622005,101622010,101622012,101631994,101632004,101642000,101642004,101642009,101642016,101651998,101652000,101652004,101652012,101681997,101702000,101702003,101702004,101712013,10171998,10172003,10172018,101722003,101722011,101731998,101732004,101732012,101732016,101742016,101751998,101752012,101761998,101762012,101762016,101772006,101781998,101782000,101791997,101791998,101792006,101801997,101801998,101802012,101811992,101811998,101812005,101812006,101812013,10182006,10182007,101821990,101821998,101832003,101832004,101842005,101852005,101862010,101862016]    
    inc = 1

    numproc = ""
    municipio = ""
    uf = ""
    protocolo = ""
    representantes = "" 
    representados = ""
    relator = "" 
    assunto = "" 
    localizacao = "" 
    fase_atual = "" 

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
                    'uf': self.uf,
                    'protocolo': {
                        'numero': extract_literal_regex_only(self.protocolo, self.regexDict["protocol_number"]),
                        'data': extract_literal_regex_only(self.protocolo, self.regexDict["date"]),
                        'hora': extract_literal_regex_only(self.protocolo, self.regexDict["time"])
                    },
                    'representantes': self.representantes,
                    'representados': self.representados,
                    'relator': self.relator,
                    'assunto': extract_literal_regex_only(self.assunto, self.regexDict["anything"]),
                    'localizacao': extract_literal_regex_only(self.localizacao, self.regexDict["anything"]),
                    'fase_atual': {
                        'data_ultima_atualizacao': extract_literal_regex_only(self.fase_atual, self.regexDict["date"]),
                        'hora_ultima_atualizacao': extract_literal_regex_only(self.fase_atual, self.regexDict["time"]),
                        'comentario': parse_commentary(self),
                    }
                }
            except TypeError as t:
                print("error:")
                print(t)
                continue
            

        next_page_url = f'http://inter03.tse.jus.br/sadpPush/ExibirDadosProcesso.do?nprot={self.test_prot_codes[self.inc]}&comboTribunal=tse'
        self.inc += 1
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

def reset_attributes(self):
    self.numproc = None
    self.municipio = ""
    self.uf = ""
    self.protocolo = ""
    self.representantes = "" 
    self.representados = ""
    self.relator = "" 
    self.assunto = "" 
    self.localizacao = "" 
    self.fase_atual = "" 

def get_corresponding_attribute(self, selector, current_element):
    if("PROCESSO" in selector):
        self.numproc = current_element.xpath(".//td/text()").re(self.regexDict["process_number"])[0]
    elif("MUNICIPIO" in selector):
        self.municipio = current_element.xpath(".//td/text()").getall()
        self.municipio = unidecode_all(self.municipio)
        self.municipio = remove_special_characters_all(self.municipio)
        self.municipio = extract_matching_string_from_list(self.municipio, self.regexDict["municipio"])
    elif("UF" in selector):
        self.uf = current_element.xpath(".//td/text()").getall()
        self.uf = unidecode_all(self.uf)
        self.uf = remove_special_characters_all(self.uf)
        self.uf = extract_matching_string_from_list(self.uf, self.regexDict["uf"])
    elif("PROTOCOLO" in selector):
        self.protocolo = current_element.xpath(".//td/text()").getall()
        self.protocolo = remove_special_characters_all(self.protocolo)
        self.protocolo = remove_empty_strings(self.protocolo)
    elif("REPRESENTANT" in selector):
        self.representantes = current_element.xpath(".//td/text()").getall()
        self.representantes = unidecode_all(self.representantes)
        self.representantes = remove_special_characters_all(self.representantes)
        self.representantes = remove_empty_strings(self.representantes)
    elif("REPRESENTAD" in selector):
        self.representados = current_element.xpath(".//td/text()").getall()
        self.representados = unidecode_all(self.representados)
        self.representados = remove_special_characters_all(self.representados)
        self.representados = remove_empty_strings(self.representados)
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
    if(isinstance(text, list)):
        text = " ".join(text)

    if(isinstance(text, str) and text == ""):
        return ""
    
    search_results = re.search(regex, text)
    if(search_results is not None):
        text = search_results.group(0)
    else:
        text = ""

    return text

def remove_first_regex_occurrence(text, regex):
    text_to_remove = extract_literal_regex_only(text, regex)
    return text.replace(text_to_remove,"",1)

# Specific for separating date and time from the "Fase Atual" field
def parse_commentary(self):
    text_arr = self.fase_atual
    commentary = extract_literal_regex_only(text_arr, self.regexDict["anything"])
    commentary = remove_first_regex_occurrence(commentary, self.regexDict["time"])
    commentary = remove_first_regex_occurrence(commentary, self.regexDict["date"])
    return commentary.replace("-","").strip()

