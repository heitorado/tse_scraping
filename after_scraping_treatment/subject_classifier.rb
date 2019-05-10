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
        # Here we will get the UNIQUE values of "assunto" (subject) and save in a file for later classification
        @data_hash.each do |data|
            @assunto_list << sanitize(data['assunto'])
        end

        @assunto_list.uniq.sort.each do |assunto|
            puts "\"#{assunto}\""
        end
    end

end

