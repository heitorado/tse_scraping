require 'json'
require 'i18n'

def sanitize(str)
    return I18n.transliterate(str).upcase.gsub("PC DO B", "PCDOB").gsub("_", " ").gsub("-"," ").gsub("( "," ").gsub(")"," ").gsub("."," ").gsub("\n"," ").strip.squeeze(" ").upcase
end

I18n.config.available_locales = :en
I18n.default_locale = :en

file = File.read("./scraped_items_rosa.json")

data_hash = JSON.parse(file)

dict = File.read("./parts_ids.json")

part_ids = JSON.parse(dict)

#data_hash[0]['partes']['polos']['polo_ativo']

data_hash.each do |data|
    
    a = data['partes']['polos']['polo_ativo'].map { |pa| pa = part_ids[sanitize(pa)] }
    data['partes']['polos']['polo_ativo'] = a.dup
    if a.include? 50 then puts "#{a}" end

    b = data['partes']['polos']['polo_passivo'].map { |pp| pp = part_ids[sanitize(pp)] }
    data['partes']['polos']['polo_passivo'] = b.dup
end


File.open("classified_scraped_items_rosa.json","w") do |f|
    f.write(data_hash.to_json)
end