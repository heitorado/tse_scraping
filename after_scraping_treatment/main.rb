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
        data['partes']['polos']['polo_ativo'] = active_pole.dup
    
        passive_pole = data['partes']['polos']['polo_passivo'].map { |pp| pp = part_ids[sanitize_part(pp)] }
        data['partes']['polos']['polo_passivo'] = passive_pole.dup

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
                        "prot_num", "prot_data", "prot_hora", "polo_ativo_pf", "polo_ativo_entpubl", 
                        "polo_ativo_partido", "polo_ativo_colig", "polo_passivo_pf", "polo_passivo_entpubl", 
                        "polo_passivo_partido", "polo_passivo_colig", "relator", "assunto", "assunto_abuso", 
                        "assunto_captacao_ilicita_de_sufragio", "assunto_fraude", "assunto_contas", 
                        "assunto_registro_de_candidatura", "assunto_conduta_vedada", "assunto_gasto ilicito", 
                        "assunto_informacao", "assunto_pedido", "assunto_recurso", "assunto_propaganda", 
                        "assunto_solicitacao", "assunto_outro", "localizacao", "fase_atual_ultima_atualizacao_data", 
                        "fase_atual_ultima_atualizacao_hora", "fase_atual_comentario", "url"])

        
        classified_data_hash.each do |process|
            identificacao = process['identificacao'].to_s
            num_processo = process['num_processo']
            num_processo_vinculado = process['num_processo_vinculado']
            municipio = process['municipio']
            uf = process['uf']
            prot_num = process['protocolo']['numero']
            prot_data = process['protocolo']['data']
            prot_hora = process['protocolo']['hora']
            polo_ativo_pf = (process['partes']['polos']['polo_ativo'] & [99]).any?
            polo_ativo_entpubl = (process['partes']['polos']['polo_ativo'] & [36, 37, 38]).any?
            polo_ativo_partido = (process['partes']['polos']['polo_ativo'] & [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,50]).any?
            polo_ativo_colig = (process['partes']['polos']['polo_ativo'] & [1]).any?
            polo_passivo_pf = (process['partes']['polos']['polo_passivo'] & [99]).any?
            polo_passivo_entpubl = (process['partes']['polos']['polo_passivo'] & [36, 37, 38]).any?
            polo_passivo_partido = (process['partes']['polos']['polo_passivo'] & [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,50]).any?
            polo_passivo_colig =  (process['partes']['polos']['polo_passivo'] & [1]).any?
            relator = process['relator']
            assunto = process['assunto']
            assunto_abuso = (process['assunto_ids'] & [1]).any?
            assunto_captacao_ilicita_de_sufragio = (process['assunto_ids'] & [2]).any?
            assunto_fraude = (process['assunto_ids'] & [3]).any?
            assunto_contas = (process['assunto_ids'] & [4]).any?
            assunto_registro_de_candidatura = (process['assunto_ids'] & [5]).any?
            assunto_conduta_vedada = (process['assunto_ids'] & [6]).any?
            assunto_gasto_ilicito = (process['assunto_ids'] & [7]).any?
            assunto_informacao = (process['assunto_ids'] & [8]).any?
            assunto_pedido = (process['assunto_ids'] & [9]).any?
            assunto_recurso = (process['assunto_ids'] & [10]).any?
            assunto_propaganda = (process['assunto_ids'] & [11]).any?
            assunto_solicitacao = (process['assunto_ids'] & [12]).any?
            assunto_outro = (process['assunto_ids'] & [0]).any?
            localizacao = process['localizacao']
            fase_atual_ultima_atualizacao_data = process['fase_atual']['data_ultima_atualizacao']
            fase_atual_ultima_atualizacao_hora = process['fase_atual']['hora_ultima_atualizacao']
            fase_atual_comentario = process['fase_atual']['comentario']
            url = process['url']

            csv << [identificacao, num_processo, num_processo_vinculado, municipio, uf, prot_num, prot_data, prot_hora, polo_ativo_pf, polo_ativo_entpubl, polo_ativo_partido, polo_ativo_colig, polo_passivo_pf, polo_passivo_entpubl, polo_passivo_partido, polo_passivo_colig, relator, assunto, assunto_abuso, assunto_captacao_ilicita_de_sufragio, assunto_fraude, assunto_contas, assunto_registro_de_candidatura, assunto_conduta_vedada, assunto_gasto_ilicito, assunto_informacao, assunto_pedido, assunto_recurso, assunto_propaganda, assunto_solicitacao, assunto_outro, localizacao, fase_atual_ultima_atualizacao_data, fase_atual_ultima_atualizacao_hora, fase_atual_comentario, url]        
        end
    end
end


generate_parts_dictionary()
generate_subjects_dictionary()
generate_processed_json()
generate_processed_csv()