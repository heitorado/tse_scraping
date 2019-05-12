require 'json'
require 'i18n'

require_relative "helper_methods"

class SubjectClassifier
    include HelperMethods

    def initialize(file_path)
        @file = File.read("#{file_path}")
        @data_hash = JSON.parse(@file)
        @dict_hash = Hash.new
        @assunto_list = []
    end

    def classify_subjects
        
        @data_hash.each do |data|
            @assunto_list << sanitize_subject(data['assunto'])
        end

        # Then we filter the unique results and sort it alphabetically.
        # After that, we iterate through each item to search for our predefined matches (method 'classify')
        # that will yield us an array of identifiers for that data. This allows us to generalize strings that have the same meaning.
        @assunto_list.uniq.sort.each do |assunto|

            # Here we will get back an array, since the subjects can be "composite" - that is, one line of the data can be about multiple subjects.
            # this is expected - after all, a process can have multiple subjects, and rosa can't guess where a subject begins and ends (since it's formed by many words).
            # so we will filter by the subjects that we find to be more common and/or relevant to our posterior analysis
            ids = classify(assunto)

            # After these filters, we have the data property classified and output it in a csv-friendly format 
            # - note that 'ids' is an array, therefore this will need to be parsed later, since multiple data in one cell is confusing to CSV -
            puts "\"#{assunto}\", \"#{ids}\""
            
            # After printing, we also include the classification id on our @dict_hash, that will allow us to save the classification as JSON later.
            @dict_hash[assunto] = ids
        end
    end

    def save_dictionary_as_json(file_name)
        File.open("#{file_name}.json","w") do |f|
            f.write(@dict_hash.to_json)
        end
    end

    def classify(str)
        subjects_arr = []
        if(str.include? "ABUSO")
            subjects_arr << 1;
        end
        if(str.include? "CAPTACAO ILICITA DE SUFRAGIO")
            subjects_arr << 2;
        end
        if(str.include? "FRAUDE")
            subjects_arr << 3;
        end
        if(str.include? "CONTAS")
            subjects_arr << 4;
        end
        if(str.include? "REGISTRO DE CANDIDATURA")
            subjects_arr << 5;
        end
        if(str.include? "CONDUTA VEDADA")
            subjects_arr << 6;
        end
        if(str.include? "GASTO ILICITO")
            subjects_arr << 7;
        end
        if(str.include? "INFORMACAO")
            subjects_arr << 8;
        end
        if(str.include? "PEDIDO")
            subjects_arr << 9;
        end
        if(str.include? "RECURSO")
            subjects_arr << 10;
        end
        if(str.include? "PROPAGANDA")
            subjects_arr << 11;
        end
        if(str.include? "SOLICITACAO")
            subjects_arr << 12;
        end

        # This means "other subjects", that is, subjects that we are not classifying in our analysis.
        if(subjects_arr.empty?)
            subjects_arr << 0;
        end

        return subjects_arr
    end

end

