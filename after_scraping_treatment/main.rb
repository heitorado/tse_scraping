require 'json'
require 'i18n'

require_relative "parts_classifier"
require_relative "subject_classifier"

I18n.config.available_locales = :en
I18n.default_locale = :en

pc = PartsClassifier.new("../scraped_items_rosa.json")
pc.classify_parts
pc.save_dictionary_as_json("parts_dict")

# sc = SubjectClassifier.new("../scraped_items_rosa.json")
# sc.classify_subjects