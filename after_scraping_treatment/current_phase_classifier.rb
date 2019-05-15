class CurrentPhaseClassifier
    require 'json'
    require 'i18n'
    require_relative "helper_methods"

    include HelperMethods

    def initialize(file_path)
        @file = File.read("#{file_path}")
        @data_hash = JSON.parse(@file)
        @dict_hash = Hash.new
        @phase_list = []
    end

    def classify_subjects
        
        @data_hash.each do |data|
            @phase_list << sanitize_phase(data['fase_atual']['comentario'])
        end

        # Then we filter the unique results and sort it alphabetically.
        # After that, we iterate through each item to search for our predefined matches (method 'classify')
        # that will yield us an array of identifiers for that data. This allows us to generalize strings that have the same meaning.
        @phase_list.uniq.sort.each do |phase|

            ids = classify(phase)

            # After these filters, we have the data property classified and output it in a csv-friendly format 
            puts "\"#{phase}\""#", \"#{ids}\""
            
            # After printing, we also include the classification id on our @dict_hash, that will allow us to save the classification as JSON later.
            @dict_hash[phase] = ids
        end
    end

    def save_dictionary_as_json(file_name)
        File.open("#{file_name}.json","w") do |f|
            f.write(@dict_hash.to_json)
        end
    end

    def classify(str)

        return;
    end
end