module HelperMethods
    def sanitize_part(str)
        return I18n.transliterate(str).upcase.gsub("PC DO B", "PCDOB").gsub("_", " ").gsub("-"," ").gsub("("," ").gsub(")"," ").gsub("."," ").gsub("\n"," ").strip.squeeze(" ").upcase
    end

    def sanitize_subject(str)
        return I18n.transliterate(str).upcase.gsub("\"","").gsub(",", " ").gsub("_", " ").gsub("-"," ").gsub("("," ").gsub(")"," ").gsub("."," ").gsub("\n"," ").strip.squeeze(" ").upcase
    end

    def headers(arr)
        return arr
    end

    def binary(stmt)
        return stmt ? '1' : '0'
    end

    def na_or_content(str)
        return str.gsub(",","").gsub(" ","").empty? ? "N/A" : "#{str}"
    end
end