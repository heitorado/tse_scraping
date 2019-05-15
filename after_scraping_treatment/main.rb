require 'json'
require 'i18n'
require 'csv'

require_relative "parts_classifier"
require_relative "subject_classifier"
require_relative "helper_methods"

include HelperMethods

I18n.config.available_locales = :en
I18n.default_locale = :en

def generate_parts_dictionary
    pc = PartsClassifier.new("../scraped_items_rosa.json")
    pc.classify_parts
    pc.save_dictionary_as_json("parts_dict")
end

def generate_subjects_dictionary
    sc = SubjectClassifier.new("../scraped_items_rosa.json")
    sc.classify_subjects
    sc.save_dictionary_as_json("subjects_dict")
end

# Generates the main JSON for our analysis, given all the dictionaries created for the data.
def generate_processed_json
    file = File.read("../scraped_items_rosa.json")
    data_hash = JSON.parse(file)

    parts_dict = File.read("./parts_dict.json")
    part_ids = JSON.parse(parts_dict)

    subjects_dict = File.read("./subjects_dict.json")
    subject_ids = JSON.parse(subjects_dict)


    data_hash.each do |data|
        active_pole = data['partes']['polos']['polo_ativo'].map { |pa| pa = part_ids[sanitize_part(pa)] }
        data['partes']['polos']['polo_ativo_ids'] = active_pole.dup
    
        passive_pole = data['partes']['polos']['polo_passivo'].map { |pp| pp = part_ids[sanitize_part(pp)] }
        data['partes']['polos']['polo_passivo_ids'] = passive_pole.dup

        subjects = subject_ids[sanitize_subject(data['assunto'])]
        data['assunto_ids'] = subjects.dup
    end
    
    File.open("classified_scraped_items_rosa.json","w") do |f|
        f.write(data_hash.to_json)
    end
end

def generate_processed_csv
    file = File.read("classified_scraped_items_rosa.json")
    classified_data_hash = JSON.parse(file)

    CSV.open("main_processed_data.csv", "wb") do |csv|

        csv << headers(["identificacao", "num_processo", "num_processo_vinculado", "municipio", "uf", 
                        "prot_num", "prot_data", "prot_hora", 
                        'representantes','representados','apelantes','apelados','agravantes','agravados','recorrentes','recorridos','embargantes','embargados','impetrantes','impetrados','requerentes','requeridos','reclamantes','reclamados','exequentes','executados','demandantes','demandados','denunciantes','denunciados','excipientes','exceptos','querelantes','querelados','autores','reus',
                        "polo_ativo_pf", "polo_ativo_entpubl", 
                        "polo_ativo_partido", "polo_ativo_colig", "polo_passivo_pf", "polo_passivo_entpubl", 
                        "polo_passivo_partido", "polo_passivo_colig", "relator", "assunto", "assunto_abuso", 
                        "assunto_captacao_ilicita_de_sufragio", "assunto_fraude", "assunto_contas", 
                        "assunto_registro_de_candidatura", "assunto_conduta_vedada", "assunto_gasto ilicito", 
                        "assunto_informacao", "assunto_pedido", "assunto_recurso", "assunto_propaganda", 
                        "assunto_solicitacao", "assunto_outro", "localizacao", "fase_atual_ultima_atualizacao_data", 
                        "fase_atual_ultima_atualizacao_hora", "fase_atual_comentario", "url"])

        
        classified_data_hash.each do |process|
            identificacao = na_or_content process['identificacao'].to_s
            num_processo = na_or_content process['num_processo']
            num_processo_vinculado = na_or_content process['num_processo_vinculado']
            municipio = na_or_content process['municipio']
            uf = na_or_content process['uf']
            prot_num = na_or_content process['protocolo']['numero']
            prot_data = na_or_content process['protocolo']['data']
            prot_hora = na_or_content process['protocolo']['hora']
            representantes = na_or_content process['partes']['representantes'].join(",")
            representados = na_or_content process['partes']['representados'].join(",")
            apelantes = na_or_content process['partes']['apelantes'].join(",")
            apelados = na_or_content process['partes']['apelados'].join(",")
            agravantes = na_or_content process['partes']['agravantes'].join(",")
            agravados = na_or_content process['partes']['agravados'].join(",")
            recorrentes = na_or_content process['partes']['recorrentes'].join(",")
            recorridos = na_or_content process['partes']['recorridos'].join(",")
            embargantes = na_or_content process['partes']['embargantes'].join(",")
            embargados = na_or_content process['partes']['embargados'].join(",")
            impetrantes = na_or_content process['partes']['impetrantes'].join(",")
            impetrados = na_or_content process['partes']['impetrados'].join(",")
            requerentes = na_or_content process['partes']['requerentes'].join(",")
            requeridos = na_or_content process['partes']['requeridos'].join(",")
            reclamantes = na_or_content process['partes']['reclamantes'].join(",")
            reclamados = na_or_content process['partes']['reclamados'].join(",")
            exequentes = na_or_content process['partes']['exequentes'].join(",")
            executados = na_or_content process['partes']['executados'].join(",")
            demandantes = na_or_content process['partes']['demandantes'].join(",")
            demandados = na_or_content process['partes']['demandados'].join(",")
            denunciantes = na_or_content process['partes']['denunciantes'].join(",")
            denunciados = na_or_content process['partes']['denunciados'].join(",")
            excipientes = na_or_content process['partes']['excipientes'].join(",")
            exceptos = na_or_content process['partes']['exceptos'].join(",")
            querelantes = na_or_content process['partes']['querelantes'].join(",")
            querelados = na_or_content process['partes']['querelados'].join(",")
            autores = na_or_content process['partes']['autores'].join(",")
            reus = na_or_content process['partes']['reus'].join(",")
            polo_ativo_pf = binary (process['partes']['polos']['polo_ativo_ids'] & [99]).any?
            polo_ativo_entpubl = binary (process['partes']['polos']['polo_ativo_ids'] & [36, 37, 38]).any?
            polo_ativo_partido = binary (process['partes']['polos']['polo_ativo_ids'] & [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,50]).any?
            polo_ativo_colig = binary (process['partes']['polos']['polo_ativo_ids'] & [1]).any?
            polo_passivo_pf = binary (process['partes']['polos']['polo_passivo_ids'] & [99]).any?
            polo_passivo_entpubl = binary (process['partes']['polos']['polo_passivo_ids'] & [36, 37, 38]).any?
            polo_passivo_partido = binary (process['partes']['polos']['polo_passivo_ids'] & [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,50]).any?
            polo_passivo_colig = binary  (process['partes']['polos']['polo_passivo_ids'] & [1]).any?
            relator = na_or_content process['relator']
            assunto = na_or_content process['assunto']
            assunto_abuso = binary (process['assunto_ids'] & [1]).any?
            assunto_captacao_ilicita_de_sufragio = binary (process['assunto_ids'] & [2]).any?
            assunto_fraude = binary (process['assunto_ids'] & [3]).any?
            assunto_contas = binary (process['assunto_ids'] & [4]).any?
            assunto_registro_de_candidatura = binary (process['assunto_ids'] & [5]).any?
            assunto_conduta_vedada = binary (process['assunto_ids'] & [6]).any?
            assunto_gasto_ilicito = binary (process['assunto_ids'] & [7]).any?
            assunto_informacao = binary (process['assunto_ids'] & [8]).any?
            assunto_pedido = binary (process['assunto_ids'] & [9]).any?
            assunto_recurso = binary (process['assunto_ids'] & [10]).any?
            assunto_propaganda = binary (process['assunto_ids'] & [11]).any?
            assunto_solicitacao = binary (process['assunto_ids'] & [12]).any?
            assunto_outro = binary (process['assunto_ids'] & [0]).any?
            localizacao = na_or_content process['localizacao']
            fase_atual_ultima_atualizacao_data = na_or_content process['fase_atual']['data_ultima_atualizacao']
            fase_atual_ultima_atualizacao_hora = na_or_content process['fase_atual']['hora_ultima_atualizacao']
            fase_atual_comentario = na_or_content process['fase_atual']['comentario']
            url = na_or_content process['url']

            csv << [identificacao, num_processo, num_processo_vinculado, municipio, uf, prot_num, prot_data, prot_hora, representantes,representados,apelantes,apelados,agravantes,agravados,recorrentes,recorridos,embargantes,embargados,impetrantes,impetrados,requerentes,requeridos,reclamantes,reclamados,exequentes,executados,demandantes,demandados,denunciantes,denunciados,excipientes,exceptos,querelantes,querelados,autores,reus, polo_ativo_pf, polo_ativo_entpubl, polo_ativo_partido, polo_ativo_colig, polo_passivo_pf, polo_passivo_entpubl, polo_passivo_partido, polo_passivo_colig, relator, assunto, assunto_abuso, assunto_captacao_ilicita_de_sufragio, assunto_fraude, assunto_contas, assunto_registro_de_candidatura, assunto_conduta_vedada, assunto_gasto_ilicito, assunto_informacao, assunto_pedido, assunto_recurso, assunto_propaganda, assunto_solicitacao, assunto_outro, localizacao, fase_atual_ultima_atualizacao_data, fase_atual_ultima_atualizacao_hora, fase_atual_comentario, url]        
        end
    end
end


generate_parts_dictionary()
generate_subjects_dictionary()
generate_processed_json()
generate_processed_csv()