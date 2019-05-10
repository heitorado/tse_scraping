module HelperMethods
    def sanitize(str)
        return I18n.transliterate(str).upcase.gsub("PC DO B", "PCDOB").gsub("_", " ").gsub("-"," ").gsub("( "," ").gsub(")"," ").gsub("."," ").gsub("\n"," ").strip.squeeze(" ").upcase
    end
end