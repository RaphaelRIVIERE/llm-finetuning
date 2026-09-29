"""Tests des règles de noms de patients. Les exemples viennent de MediQAl, raccourcis."""

from scripts.patient_names import find_leftover_names, replace_patient_names


def anonymized(text):
    return replace_patient_names(text)[0]


def test_title_and_initial():
    assert anonymized("Monsieur B., 45 ans, consulte.") == "Monsieur [PATIENT], 45 ans, consulte."


def test_title_first_name_and_initial():
    assert anonymized("Mme Aline R., âgée de 43 ans, est hospitalisée.") == "Mme [PATIENT], âgée de 43 ans, est hospitalisée."


def test_misspelled_title():
    assert anonymized("Monsier Eric B., connu pour une cirrhose.") == "Monsier [PATIENT], connu pour une cirrhose."


def test_first_name_left_after_patient_tag():
    assert anonymized("Monsieur X.. Daniel, âgé de 38 ans, consulte.") == "Monsieur [PATIENT], âgé de 38 ans, consulte."


def test_title_and_surname():
    assert anonymized("Monsieur Durand, ouvrier de 29 ans, consulte.") == "Monsieur [PATIENT], ouvrier de 29 ans, consulte."
    assert anonymized("Madame Haz., 25 ans, mariée.") == "Madame [PATIENT], 25 ans, mariée."


def test_first_name_followed_by_age():
    assert anonymized("Damien, âgé de 6 ans, vient avec sa mère.") == "[PATIENT], âgé de 6 ans, vient avec sa mère."
    assert anonymized("L'enfant Sébastien, 4 ans, souffre depuis 15 jours.") == "L'enfant [PATIENT], 4 ans, souffre depuis 15 jours."


def test_common_words_before_age_kept():
    for text in ["Patiente, 45 ans, sans antécédent.", "Puberté 14 ans, cycle de 30 jours.", "Appendicectomie 25 ans plus tôt."]:
        assert anonymized(text) == text


def test_medical_vocabulary_kept():
    text = "Streptocoque A. retrouvé. Syndrome de Cushing chez une femme de 52 ans."
    assert replace_patient_names(text) == (text, False)


def test_initial_with_several_dots():
    assert anonymized("Monsieur C..., 29 ans, est admis.") == "Monsieur [PATIENT], 29 ans, est admis."


def test_first_name_and_initial_followed_by_age():
    assert anonymized("Noé L. 10 ans, sans antécédent notable.") == "[PATIENT] 10 ans, sans antécédent notable."


def test_capitalized_word_after_m_kept():
    text = "L'essai d'un nouveau produit M. La justification de cet essai tient au fait que..."
    assert anonymized(text) == text


def leftover_kinds(text, language):
    return [kind for kind, _ in find_leftover_names(text, language)]


def test_leftover_names_found_in_english():
    assert leftover_kinds("My name is Debbie I had bunionectomy.", "en") == ["je m'appelle"]
    assert leftover_kinds("Meet Emma, a 65-year-old woman with memory loss.", "en") == ["prénom + âge"]
    assert leftover_kinds("Mr. Jones presents with chest pain.", "en") == ["titre + nom"]


def test_no_leftover_in_anonymous_english_case():
    assert find_leftover_names("For a 54-year-old male with chest pain, what is the next step?", "en") == []


def test_no_leftover_after_french_anonymization():
    text = anonymized("Madame Françoise B., 34 ans, mariée. Son fils Marc, âgé de 5 ans, l'accompagne.")
    assert find_leftover_names(text, "fr") == []


def test_leftover_found_in_french():
    assert leftover_kinds("Mme Barbie a été percutée par un bus.", "fr") == ["titre + nom"]


def test_title_and_initial_without_dot():
    assert anonymized("Une certaine Madame P a été admise.") == "Une certaine Madame [PATIENT] a été admise."
    assert anonymized("On a porté chez Mr R 28 ans le diagnostic.") == "On a porté chez Mr [PATIENT] 28 ans le diagnostic."


def test_first_name_and_initial_anywhere():
    assert anonymized("Brigitte V. est traitée par AUGMENTIN.") == "[PATIENT] est traitée par AUGMENTIN."


def test_age_written_without_accent():
    assert anonymized("Sandrine, agée de 25 ans, est enceinte.") == "[PATIENT], agée de 25 ans, est enceinte."


def test_medical_letters_kept():
    for text in ["Se Protéine C Réactive : 178 mg/L", "avec LPS (Ag O, endotoxine)", "Vitamine B. et fer."]:
        assert anonymized(text) == text


def test_leftover_title_and_initial_without_dot():
    assert leftover_kinds("Le traitement est-il justifié pour Mr X ?", "fr") == ["titre + initiale"]


def test_initial_without_dot_after_first_name():
    assert anonymized("M. Robert D, âgé de 85 ans, diabétique.") == "M. [PATIENT], âgé de 85 ans, diabétique."
    assert anonymized("Comme dans le cas de M. Georges X).") == "Comme dans le cas de M. [PATIENT])."
    assert anonymized("Marc X, 23 ans, sous lieutenant.") == "[PATIENT], 23 ans, sous lieutenant."


def test_doctor_and_lab_values_kept():
    for text in ["Le Dr M. le revoit demain.", "Hb F. normale", "Ig E. totales élevées"]:
        assert anonymized(text) == text


def test_upper_case_surname():
    assert anonymized("Monsieur DUPONT, 35 ans, grutier.") == "Monsieur [PATIENT], 35 ans, grutier."
    assert anonymized("Depuis six mois, Mr LUC... a souffert du bras.") == "Depuis six mois, Mr [PATIENT] a souffert du bras."
    assert anonymized("Monsieur Jean-Jacques TUR., âgé de 65 ans.") == "Monsieur [PATIENT], âgé de 65 ans."
    assert anonymized("Monsieur RAT. Pierre âgé de 39 ans.") == "Monsieur [PATIENT] âgé de 39 ans."


def test_leftover_upper_case_surname_found():
    assert leftover_kinds("Mme ROB. consulte.", "fr") == ["titre + NOM"]


def test_title_dot_kept():
    assert anonymized("Mr. A, 40 ans, consulte.") == "Mr. [PATIENT], 40 ans, consulte."


def test_first_name_after_patient_tag_before_est():
    assert anonymized("Monsieur D. Jean est âgé de 41 ans.") == "Monsieur [PATIENT] est âgé de 41 ans."


def test_first_name_and_upper_case_surname_before_age():
    assert anonymized("L'enfant Kévin REN., âgé de 16 mois, est amené.") == "L'enfant [PATIENT], âgé de 16 mois, est amené."
    assert anonymized("Dosage TSH. normal.") == "Dosage TSH. normal."


def test_space_kept_before_age():
    assert anonymized("Madame D.25 ans, est hospitalisée.") == "Madame [PATIENT] 25 ans, est hospitalisée."


def test_leftover_patient_record_in_english():
    assert leftover_kinds("Patient Name: John Doe\nDate of Birth: 01/01/1960", "en") == ["fiche patient"]
