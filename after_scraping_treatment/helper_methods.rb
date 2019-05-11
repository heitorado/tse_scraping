module HelperMethods
    def sanitize_part(str)
        return I18n.transliterate(str).upcase.gsub("PC DO B", "PCDOB").gsub("_", " ").gsub("-"," ").gsub("("," ").gsub(")"," ").gsub("."," ").gsub("\n"," ").strip.squeeze(" ").upcase
    end

    def sanitize_subject(str)
        return I18n.transliterate(str).upcase.gsub("\"","").gsub(",", " ").gsub("_", " ").gsub("-"," ").gsub("("," ").gsub(")"," ").gsub("."," ").gsub("\n"," ").strip.squeeze(" ").upcase
    end
end