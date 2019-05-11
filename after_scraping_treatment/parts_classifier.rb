require 'json'
require 'i18n'

require_relative "helper_methods"


class PartsClassifier
    include HelperMethods

    def initialize(file_path)
        @file = File.read("#{file_path}")
        @data_hash = JSON.parse(@file)
        @dict_hash = Hash.new
        @parts_list = []
    end
    
    def classify_parts
        # Here we will get the values of both poles and put in the @parts_list array
        @data_hash.each do |data|
            data['partes']['polos']['polo_ativo'].each do |pa|
                @parts_list << sanitize(pa)
            end
            
            data['partes']['polos']['polo_passivo'].each do |pp|
                @parts_list << sanitize(pp)
            end
        end

        # Then we filter the unique results and sort it alphabetically.
        # After that, we iterate through each item to search for our predefined matches (method 'classify')
        # that will yield us an identifier for that data. This allows us to generalize strings that have the same meaning.
        @parts_list.uniq.sort.each do |part|

            word_splitted_part = part.scan(/\w*/)

            # The classify() method classifies parties by their initials, which are unique.
            id = classify(word_splitted_part)

            # If the first call to 'classify' was unsucessful (That is, yielded the code 99 - meaning it is a physical or juridical person)
            # it may be wrong (maybe it was the party's full name) So we need to run a second filter, that instead of
            # searching for the initials, it will search by the full name of the party.
            if(id == 99)
                id = classify_by_full_name(part)
            end

            # And still, it is possible that we are iterating throug a party that doesn't exist anymore, but it can't be classified as a person.
            # then we run a third filter, checking if the data hasn't got the tile "PARTIDO" (party).
            if(id == 99)
                id = search_for_missing_parties(part)
            end

            # After these filters, we have the data property classified and output it in a csv-friendly format:
            puts "\"#{part}\",#{id}"

            # After printing, we also include the classification id on our @dict_hash, that will allow us to save the classification as JSON later.
            @dict_hash[part] = id
        end
    end

    def save_dictionary_as_json(file_name)
        File.open("#{file_name}.json","w") do |f|
            f.write(@dict_hash.to_json)
        end
    end

    def classify(str)
        # if(str.include? "MINISTERIO PUBLICO")
        #     return 0
        if(str.include? "COLIGACAO")
            return 1
        elsif(str.include? "MDB" or str.include? "PMDB") 
            return 2
        elsif(str.include? "PTB") 
            return 3
        elsif(str.include? "PDT") 
            return 4
        elsif(str.include? "PT") 
            return 5
        elsif(str.include? "DEM") 
            return 6
        elsif(str.include? "PCDOB") 
            return 7
        elsif(str.include? "PSB") 
            return 8
        elsif(str.include? "PSDB") 
            return 9
        elsif(str.include? "PTC") 
            return 10
        elsif(str.include? "PSC") 
            return 11
        elsif(str.include? "PMN") 
            return 12
        elsif(str.include? "PPS") 
            return 13
        elsif(str.include? "PV") 
            return 14
        elsif(str.include? "AVANTE") 
            return 15
        elsif(str.include? "PP") 
            return 16
        elsif(str.include? "PSTU") 
            return 17
        elsif(str.include? "PCB") 
            return 18
        elsif(str.include? "PRTB") 
            return 19
        elsif(str.include? "PHS") 
            return 20
        elsif(str.include? "DC") 
            return 21
        elsif(str.include? "PCO") 
            return 22
        elsif(str.include? "PODE") 
            return 23
        elsif(str.include? "PSL") 
            return 24
        elsif(str.include? "PRB") 
            return 25
        elsif(str.include? "PSOL") 
            return 26
        elsif(str.include? "PR") 
            return 27
        elsif(str.include? "PSD") 
            return 28
        elsif(str.include? "PPL") 
            return 29
        elsif(str.include? "PATRIOTA") 
            return 30
        elsif(str.include? "PROS") 
            return 31
        elsif(str.include? "SOLIDARIEDADE") 
            return 32
        elsif(str.include? "NOVO") 
            return 33
        elsif(str.include? "REDE") 
            return 34
        elsif(str.include? "PMB") 
            return 35
        elsif(str.include? "TRIBUNAL" or str.include? "TRIBUNAIS")
            return 36
        elsif(str.include? "MINISTERIO")
            return 37
        elsif(str.include? "CONGRESSO NACIONAL")
            return 38
        else
            return 99
        end

        return "UNCLASSIFIED"
    end

    def classify_by_full_name(str)
    if(str.include? "MOVIMENTO DEMOCRATICO BRASILEIRO" or str.include? "PARTIDO DO MOVIMENTO DEMOCRATICO BRASILEIRO") 
            return 2
        elsif(str.include? "PARTIDO TRABALHISTA BRASILEIRO") 
            return 3
        elsif(str.include? "PARTIDO DEMOCRATICO TRABALHISTA") 
            return 4
        elsif(str.include? "PARTIDO DOS TRABALHADORES") 
            return 5
        elsif(str.include? "DEMOCRATAS") 
            return 6
        elsif(str.include? "PARTIDO COMUNISTA DO BRASIL") 
            return 7
        elsif(str.include? "PARTIDO SOCIALISTA BRASILEIRO") 
            return 8
        elsif(str.include? "PARTIDO DA SOCIAL DEMOCRACIA BRASILEIRA") 
            return 9
        elsif(str.include? "PARTIDO TRABALHISTA CRISTAO") 
            return 10
        elsif(str.include? "PARTIDO SOCIAL CRISTAO") 
            return 11
        elsif(str.include? "PARTIDO DA MOBILIZACAO NACIONAL") 
            return 12
        elsif(str.include? "PARTIDO POPULAR SOCIALISTA") 
            return 13
        elsif(str.include? "PARTIDO VERDE") 
            return 14
        elsif(str.include? "AVANTE" or str.include? "PARTIDO AVANTE") 
            return 15
        elsif(str.include? "PROGRESSISTAS" or str.include? "PARTIDO PROGRESSISTA") 
            return 16
        elsif(str.include? "PARTIDO SOCIALISTA DOS TRABALHADORES UNIFICADO") 
            return 17
        elsif(str.include? "PARTIDO COMUNISTA BRASILEIRO") 
            return 18
        elsif(str.include? "PARTIDO RENOVADOR TRABALHISTA BRASILEIRO") 
            return 19
        elsif(str.include? "PARTIDO HUMANISTA DA SOLIDARIEDADE") 
            return 20
        elsif(str.include? "DEMOCRACIA CRISTA") 
            return 21
        elsif(str.include? "PARTIDO DA CAUSA OPERARIA") 
            return 22
        elsif(str.include? "PODEMOS" or str.include? "PARTIDO PODEMOS") 
            return 23
        elsif(str.include? "PARTIDO SOCIAL LIBERAL") 
            return 24
        elsif(str.include? "PARTIDO REPUBLICANO BRASILEIRO") 
            return 25
        elsif(str.include? "PARTIDO SOCIALISMO E LIBERDADE") 
            return 26
        elsif(str.include? "PARTIDO DA REPUBLICA") 
            return 27
        elsif(str.include? "PARTIDO SOCIAL DEMOCRATICO") 
            return 28
        elsif(str.include? "PARTIDO PATRIA LIVRE") 
            return 29
        elsif(str.include? "PATRIOTA" or str.include? "PARTIDO PATRIOTA") 
            return 30
        elsif(str.include? "PARTIDO REPUBLICANO DA ORDEM SOCIAL") 
            return 31
        elsif(str.include? "SOLIDARIEDADE" or str.include? "PARTIDO DA SOLIDARIEDADE") 
            return 32
        elsif(str.include? "PARTIDO NOVO") 
            return 33
        elsif(str.include? "REDE SUSTENTABILIDADE" or str.include? "PARTIDO REDE SUSTENTABILIDADE") 
            return 34
        elsif(str.include? "PARTIDO DA MULHER BRASILEIRA") 
            return 35
        else
            return 99
        end
    end

    def search_for_missing_parties(str)
        if(str.include? "PARTIDO")
            return 50
        else
            return 99
        end
    end
end

