"""Every user-facing string, in English, Kannada and Hindi. ui.t(key, **fmt) looks them up.
Chart content (axis titles, model and algorithm names, table bodies) and the About prose stay English."""

STRINGS: dict[str, dict[str, str]] = {
    # ---------------------------------------------------------------- shell
    "nav_home": {"en": "Home", "kn": "ಮುಖಪುಟ", "hi": "होम"},
    "nav_screen": {"en": "Screen", "kn": "ತಪಾಸಣೆ", "hi": "जाँच"},
    "nav_results": {"en": "Results", "kn": "ಫಲಿತಾಂಶಗಳು", "hi": "नतीजे"},
    "nav_insights": {"en": "Insights", "kn": "ಒಳನೋಟಗಳು", "hi": "विश्लेषण"},
    "nav_about": {"en": "About", "kn": "ಕುರಿತು", "hi": "परिचय"},
    "language": {"en": "Language", "kn": "ಭಾಷೆ", "hi": "भाषा"},
    "dark": {"en": "Dark", "kn": "ಡಾರ್ಕ್", "hi": "डार्क"},
    "footer": {
        "en": "Screening aid for health workers. Not a diagnosis. Confirm with a blood Hb test.",
        "kn": "ಆರೋಗ್ಯ ಕಾರ್ಯಕರ್ತರಿಗೆ ತಪಾಸಣಾ ಸಹಾಯಕ. ಇದು ರೋಗನಿರ್ಣಯವಲ್ಲ. ರಕ್ತದ Hb ಪರೀಕ್ಷೆಯಿಂದ ಖಚಿತಪಡಿಸಿ.",
        "hi": "स्वास्थ्य कार्यकर्ताओं के लिए जाँच सहायक। यह निदान नहीं है। खून की Hb जाँच से पुष्टि करें।",
    },
    "missing": {"en": "No results yet: {path} is missing. Create it with {cmd}.",
                "kn": "ಇನ್ನೂ ಫಲಿತಾಂಶಗಳಿಲ್ಲ: {path} ಇಲ್ಲ. {cmd} ಮೂಲಕ ರಚಿಸಿ.",
                "hi": "अभी नतीजे नहीं: {path} मौजूद नहीं है। {cmd} से बनाएँ।"},
    "cutoff": {"en": "Anaemia cut-off", "kn": "ರಕ್ತಹೀನತೆ ಮಿತಿ", "hi": "एनीमिया सीमा"},
    "this_photo": {"en": "This photo", "kn": "ಈ ಫೋಟೋ", "hi": "यह फ़ोटो"},
    "strip_unit": {"en": "Hb, g/dL", "kn": "Hb, g/dL", "hi": "Hb, g/dL"},
    "strip_aria": {"en": "Haemoglobin colour scale from 6 to 15 g/dL",
                   "kn": "6 ರಿಂದ 15 g/dL ವರೆಗಿನ ಹಿಮೋಗ್ಲೋಬಿನ್ ಬಣ್ಣದ ಮಾಪಕ",
                   "hi": "6 से 15 g/dL तक हीमोग्लोबिन रंग पैमाना"},

    # ---------------------------------------------------------------- home
    "hero_title": {"en": "Needle-free anaemia screening", "kn": "ಸೂಜಿ ಇಲ್ಲದೆ ರಕ್ತಹೀನತೆ ತಪಾಸಣೆ",
                   "hi": "बिना सुई के एनीमिया जाँच"},
    "hero_lede": {
        "en": "From one phone photo of the inner eyelid, palm or nail bed, Netra-Hb suggests whether to refer a child "
              "for a blood Hb test.",
        "kn": "ಕಣ್ಣಿನ ಒಳರೆಪ್ಪೆ, ಅಂಗೈ ಅಥವಾ ಉಗುರಿನ ಒಂದು ಫೋನ್ ಫೋಟೋದಿಂದ, ಮಗುವನ್ನು ರಕ್ತದ Hb ಪರೀಕ್ಷೆಗೆ ಕಳುಹಿಸಬೇಕೇ ಎಂದು "
              "Netra-Hb ಸೂಚಿಸುತ್ತದೆ.",
        "hi": "आँख की भीतरी पलक, हथेली या नाखून की एक फ़ोन फ़ोटो से Netra-Hb बताता है कि बच्चे को खून की Hb जाँच के लिए "
              "भेजना चाहिए या नहीं।",
    },
    "start": {"en": "Start a screening", "kn": "ತಪಾಸಣೆ ಆರಂಭಿಸಿ", "hi": "जाँच शुरू करें"},
    "try_sample": {"en": "Try a sample patient", "kn": "ಮಾದರಿ ರೋಗಿಯೊಂದಿಗೆ ಪ್ರಯತ್ನಿಸಿ", "hi": "नमूना मरीज़ आज़माएँ"},
    "actions_note": {"en": "Classical machine learning on colour features. No needle, no test strips.",
                     "kn": "ಬಣ್ಣದ ಲಕ್ಷಣಗಳ ಮೇಲೆ ಸಾಂಪ್ರದಾಯಿಕ ಯಂತ್ರ ಕಲಿಕೆ. ಸೂಜಿ ಇಲ್ಲ, ಪರೀಕ್ಷಾ ಪಟ್ಟಿ ಇಲ್ಲ.",
                     "hi": "रंग की विशेषताओं पर पारंपरिक मशीन लर्निंग। न सुई, न टेस्ट स्ट्रिप।"},
    "hero_art_alt": {"en": "Line drawings of an eye, a palm and fingernails joined by the haemoglobin colour scale",
                     "kn": "ಹಿಮೋಗ್ಲೋಬಿನ್ ಬಣ್ಣದ ಮಾಪಕದಿಂದ ಜೋಡಿಸಿದ ಕಣ್ಣು, ಅಂಗೈ ಮತ್ತು ಉಗುರುಗಳ ರೇಖಾಚಿತ್ರಗಳು",
                     "hi": "हीमोग्लोबिन रंग पैमाने से जुड़े आँख, हथेली और नाखूनों के रेखाचित्र"},
    "strip_caption": {
        "en": "The haemoglobin colour scale. Paler tissue sits to the left, richer red to the right.",
        "kn": "ಹಿಮೋಗ್ಲೋಬಿನ್ ಬಣ್ಣದ ಮಾಪಕ. ಬಿಳಿಚಿದ ಅಂಗಾಂಶ ಎಡಕ್ಕೆ, ಗಾಢ ಕೆಂಪು ಬಲಕ್ಕೆ.",
        "hi": "हीमोग्लोबिन रंग पैमाना। फीका ऊतक बाईं ओर, गहरा लाल दाईं ओर।",
    },
    "how_title": {"en": "How it works", "kn": "ಇದು ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ", "hi": "यह कैसे काम करता है"},
    "step1_name": {"en": "Photograph", "kn": "ಫೋಟೋ ತೆಗೆಯಿರಿ", "hi": "फ़ोटो लें"},
    "step1_text": {
        "en": "Gently pull down the lower eyelid, or show the palm or a nail, in daylight without flash.",
        "kn": "ಕೆಳ ರೆಪ್ಪೆಯನ್ನು ನಿಧಾನವಾಗಿ ಕೆಳಗೆ ಎಳೆಯಿರಿ, ಅಥವಾ ಅಂಗೈ ಅಥವಾ ಉಗುರನ್ನು ತೋರಿಸಿ. ಹಗಲು ಬೆಳಕು, ಫ್ಲ್ಯಾಶ್ ಬೇಡ.",
        "hi": "निचली पलक को धीरे से नीचे खींचें, या हथेली या नाखून दिखाएँ। दिन की रोशनी, फ़्लैश नहीं।",
    },
    "step2_name": {"en": "Quality check", "kn": "ಗುಣಮಟ್ಟ ಪರಿಶೀಲನೆ", "hi": "गुणवत्ता जाँच"},
    "step2_text": {
        "en": "Light, glare, sharpness and makeup are checked at once. If one fails, you get one plain fix and retake.",
        "kn": "ಬೆಳಕು, ಹೊಳಪು, ಸ್ಪಷ್ಟತೆ ಮತ್ತು ಮೇಕಪ್ ಅನ್ನು ತಕ್ಷಣ ಪರಿಶೀಲಿಸಲಾಗುತ್ತದೆ. ಒಂದು ವಿಫಲವಾದರೆ, ಸರಳ ಸಲಹೆಯೊಂದಿಗೆ ಮತ್ತೆ "
              "ತೆಗೆಯಿರಿ.",
        "hi": "रोशनी, चमक, साफ़पन और मेकअप तुरंत जाँचे जाते हैं। कोई जाँच विफल हो तो एक आसान सुझाव मिलता है, फिर दोबारा लें।",
    },
    "step3_name": {"en": "Result", "kn": "ಫಲಿತಾಂಶ", "hi": "नतीजा"},
    "step3_text": {
        "en": "Refer for Hb test or Normal, with the chance, its uncertainty band and three plain reasons.",
        "kn": "Hb ಪರೀಕ್ಷೆಗೆ ಕಳುಹಿಸಿ ಅಥವಾ ಸಾಮಾನ್ಯ, ಸಾಧ್ಯತೆ, ಅದರ ಅನಿಶ್ಚಿತತೆಯ ವ್ಯಾಪ್ತಿ ಮತ್ತು ಮೂರು ಸರಳ ಕಾರಣಗಳೊಂದಿಗೆ.",
        "hi": "Hb जाँच के लिए भेजें या सामान्य, संभावना, उसकी अनिश्चितता की सीमा और तीन आसान कारणों के साथ।",
    },
    "brief_title": {"en": "Results in brief", "kn": "ಫಲಿತಾಂಶಗಳ ಸಾರಾಂಶ", "hi": "नतीजे संक्षेप में"},
    "brief_lede": {
        "en": "Eye model on 220 children, tested with repeated patient-grouped cross-validation. Numbers are the mean "
              "over 25 held-out folds, with 95% intervals.",
        "kn": "220 ಮಕ್ಕಳ ಮೇಲಿನ ಕಣ್ಣಿನ ಮಾದರಿ, ಪುನರಾವರ್ತಿತ ರೋಗಿ-ಗುಂಪು ಅಡ್ಡ-ಪರಿಶೀಲನೆಯಿಂದ ಪರೀಕ್ಷಿಸಲಾಗಿದೆ. ಸಂಖ್ಯೆಗಳು 25 ಪ್ರತ್ಯೇಕ "
              "ಭಾಗಗಳ ಸರಾಸರಿ, 95% ವ್ಯಾಪ್ತಿಯೊಂದಿಗೆ.",
        "hi": "220 बच्चों पर आँख का मॉडल, बार-बार मरीज़-समूह क्रॉस-वैलिडेशन से जाँचा गया। संख्याएँ 25 अलग रखे गए हिस्सों का "
              "औसत हैं, 95% सीमा के साथ।",
    },
    "of_100": {"en": "of 100", "kn": "100ರಲ್ಲಿ", "hi": "100 में से"},
    "stat_sens": {"en": "anaemic children are sent for a blood test (sensitivity)",
                  "kn": "ರಕ್ತಹೀನ ಮಕ್ಕಳನ್ನು ರಕ್ತ ಪರೀಕ್ಷೆಗೆ ಕಳುಹಿಸಲಾಗುತ್ತದೆ (ಸಂವೇದನಶೀಲತೆ)",
                  "hi": "एनीमिया वाले बच्चे खून की जाँच के लिए भेजे जाते हैं (संवेदनशीलता)"},
    "stat_spec": {"en": "healthy children are correctly cleared; the other {n} get a test they did not need (specificity)",
                  "kn": "ಆರೋಗ್ಯವಂತ ಮಕ್ಕಳನ್ನು ಸರಿಯಾಗಿ ಬಿಡಲಾಗುತ್ತದೆ; ಉಳಿದ {n} ಮಕ್ಕಳಿಗೆ ಅಗತ್ಯವಿಲ್ಲದ ಪರೀಕ್ಷೆ ಆಗುತ್ತದೆ (ನಿರ್ದಿಷ್ಟತೆ)",
                  "hi": "स्वस्थ बच्चे सही से छोड़े जाते हैं; बाकी {n} की ऐसी जाँच होती है जिसकी ज़रूरत नहीं थी (विशिष्टता)"},
    "stat_auc": {"en": "ROC-AUC: how often an anaemic child scores above a healthy one (0.5 is chance)",
                 "kn": "ROC-AUC: ರಕ್ತಹೀನ ಮಗು ಆರೋಗ್ಯವಂತ ಮಗುವಿಗಿಂತ ಎಷ್ಟು ಬಾರಿ ಹೆಚ್ಚು ಅಂಕ ಪಡೆಯುತ್ತದೆ (0.5 ಎಂದರೆ ಆಕಸ್ಮಿಕ)",
                 "hi": "ROC-AUC: एनीमिया वाला बच्चा कितनी बार स्वस्थ बच्चे से ऊँचा स्कोर पाता है (0.5 यानी संयोग)"},
    "stat_ci": {"en": "95% interval {lo} to {hi}", "kn": "95% ವ್ಯಾಪ್ತಿ {lo} ರಿಂದ {hi}", "hi": "95% सीमा {lo} से {hi}"},
    "note_who": {
        "en": "<strong>Who it was tested on.</strong> Children aged 6 to 59 months in Ghana (CP-AnemiC), with lab Hb "
              "and the WHO cut-off of 11 g/dL; 42% were anaemic. Not yet tested on Indian patients or adults.",
        "kn": "<strong>ಯಾರ ಮೇಲೆ ಪರೀಕ್ಷಿಸಲಾಗಿದೆ.</strong> ಘಾನಾದ 6 ರಿಂದ 59 ತಿಂಗಳ ಮಕ್ಕಳು (CP-AnemiC), ಪ್ರಯೋಗಾಲಯ Hb ಮತ್ತು "
              "WHO ಮಿತಿ 11 g/dL; 42% ರಕ್ತಹೀನರು. ಭಾರತೀಯ ರೋಗಿಗಳು ಅಥವಾ ವಯಸ್ಕರ ಮೇಲೆ ಇನ್ನೂ ಪರೀಕ್ಷಿಸಿಲ್ಲ.",
        "hi": "<strong>किन पर जाँचा गया.</strong> घाना के 6 से 59 महीने के बच्चे (CP-AnemiC), लैब Hb और WHO सीमा 11 g/dL "
              "के साथ; 42% को एनीमिया था। भारतीय मरीज़ों या वयस्कों पर अभी नहीं जाँचा गया।",
    },
    "note_sites": {
        "en": "<strong>Palm and nail.</strong> ROC-AUC {palm} for palm and {nail} for nail, on separate Ghana sets with "
              "folder labels (taken from file names, about 3% label noise). Different children, so this is not a fair "
              "head-to-head with the eye.",
        "kn": "<strong>ಅಂಗೈ ಮತ್ತು ಉಗುರು.</strong> ಅಂಗೈಗೆ ROC-AUC {palm}, ಉಗುರಿಗೆ {nail}, ಫೋಲ್ಡರ್ ಲೇಬಲ್‌ಗಳಿರುವ ಪ್ರತ್ಯೇಕ ಘಾನಾ "
              "ಸೆಟ್‌ಗಳಲ್ಲಿ (ಫೈಲ್ ಹೆಸರುಗಳಿಂದ, ಸುಮಾರು 3% ಲೇಬಲ್ ದೋಷ). ಬೇರೆ ಮಕ್ಕಳು, ಆದ್ದರಿಂದ ಕಣ್ಣಿನೊಂದಿಗೆ ನೇರ ಹೋಲಿಕೆ ನ್ಯಾಯವಲ್ಲ.",
        "hi": "<strong>हथेली और नाखून.</strong> हथेली का ROC-AUC {palm} और नाखून का {nail}, फ़ोल्डर लेबल वाले अलग घाना सेट "
              "पर (फ़ाइल नामों से, लगभग 3% लेबल त्रुटि)। अलग बच्चे हैं, इसलिए आँख से सीधी तुलना उचित नहीं।",
    },
    "note_meaning": {
        "en": "<strong>What this means.</strong> It catches most anaemic children but sends many healthy ones for a test "
              "too. That trade-off is deliberate for screening, and a blood test always decides.",
        "kn": "<strong>ಇದರ ಅರ್ಥ.</strong> ಇದು ಹೆಚ್ಚಿನ ರಕ್ತಹೀನ ಮಕ್ಕಳನ್ನು ಗುರುತಿಸುತ್ತದೆ, ಆದರೆ ಅನೇಕ ಆರೋಗ್ಯವಂತ ಮಕ್ಕಳನ್ನೂ ಪರೀಕ್ಷೆಗೆ "
              "ಕಳುಹಿಸುತ್ತದೆ. ತಪಾಸಣೆಗೆ ಈ ವಿನಿಮಯ ಉದ್ದೇಶಪೂರ್ವಕ, ಮತ್ತು ಅಂತಿಮ ನಿರ್ಧಾರ ಯಾವಾಗಲೂ ರಕ್ತ ಪರೀಕ್ಷೆಯದು.",
        "hi": "<strong>इसका मतलब.</strong> यह ज़्यादातर एनीमिया वाले बच्चों को पकड़ता है, पर कई स्वस्थ बच्चों को भी जाँच के लिए "
              "भेजता है। जाँच के लिए यह समझौता जानबूझकर है, और अंतिम फ़ैसला हमेशा खून की जाँच करती है।",
    },

    # ---------------------------------------------------------------- screen: patient and site
    "screen_title": {"en": "Screen a patient", "kn": "ರೋಗಿಯ ತಪಾಸಣೆ", "hi": "मरीज़ की जाँच"},
    "screen_lede": {
        "en": "Choose the age band and the site, add a photo, pass the photo check, read the result. Or pick a sample "
              "patient.",
        "kn": "ವಯಸ್ಸಿನ ಗುಂಪು ಮತ್ತು ಭಾಗವನ್ನು ಆರಿಸಿ, ಫೋಟೋ ಸೇರಿಸಿ, ಫೋಟೋ ಪರಿಶೀಲನೆ ಪಾಸ್ ಮಾಡಿ, ಫಲಿತಾಂಶ ಓದಿ. ಅಥವಾ ಮಾದರಿ "
              "ರೋಗಿಯನ್ನು ಆರಿಸಿ.",
        "hi": "आयु वर्ग और अंग चुनें, फ़ोटो जोड़ें, फ़ोटो जाँच पास करें, नतीजा पढ़ें। या नमूना मरीज़ चुनें।",
    },
    "step_patient": {"en": "Patient and site", "kn": "ರೋಗಿ ಮತ್ತು ಭಾಗ", "hi": "मरीज़ और अंग"},
    "age_band": {"en": "Age band", "kn": "ವಯಸ್ಸಿನ ಗುಂಪು", "hi": "आयु वर्ग"},
    "age_6_59m": {"en": "6–59 months", "kn": "6–59 ತಿಂಗಳು", "hi": "6–59 महीने"},
    "age_5_11": {"en": "5–11 years", "kn": "5–11 ವರ್ಷ", "hi": "5–11 वर्ष"},
    "age_12_14": {"en": "12–14 years", "kn": "12–14 ವರ್ಷ", "hi": "12–14 वर्ष"},
    "age_15_woman": {"en": "15+ woman", "kn": "15+ ಮಹಿಳೆ", "hi": "15+ महिला"},
    "age_15_man": {"en": "15+ man", "kn": "15+ ಪುರುಷ", "hi": "15+ पुरुष"},
    "cutoff_title": {"en": "WHO anaemia cut-off", "kn": "WHO ರಕ್ತಹೀನತೆ ಮಿತಿ", "hi": "WHO एनीमिया सीमा"},
    "cutoff_text": {"en": "Below {c} g/dL counts as anaemia for this age band.",
                    "kn": "ಈ ವಯಸ್ಸಿನ ಗುಂಪಿಗೆ {c} g/dL ಗಿಂತ ಕಡಿಮೆ ಇದ್ದರೆ ರಕ್ತಹೀನತೆ.",
                    "hi": "इस आयु वर्ग में {c} g/dL से कम को एनीमिया माना जाता है।"},
    "cutoff_note": {
        "en": "The models learned from children aged 6 to 59 months. For this age band the cut-off moves on the colour "
              "scale, which has not been validated.",
        "kn": "ಮಾದರಿಗಳು 6 ರಿಂದ 59 ತಿಂಗಳ ಮಕ್ಕಳಿಂದ ಕಲಿತಿವೆ. ಈ ವಯಸ್ಸಿನ ಗುಂಪಿಗೆ ಮಿತಿ ಬಣ್ಣದ ಮಾಪಕದಲ್ಲಿ ಸರಿಯುತ್ತದೆ; ಇದನ್ನು ಇನ್ನೂ "
              "ಪರಿಶೀಲಿಸಲಾಗಿಲ್ಲ.",
        "hi": "मॉडल 6 से 59 महीने के बच्चों से सीखे हैं। इस आयु वर्ग के लिए सीमा रंग पैमाने पर खिसकती है, जिसकी अभी पुष्टि "
              "नहीं हुई है।",
    },
    "site_eye": {"en": "Eyelid", "kn": "ಕಣ್ಣಿನ ರೆಪ್ಪೆ", "hi": "पलक"},
    "site_palm": {"en": "Palm", "kn": "ಅಂಗೈ", "hi": "हथेली"},
    "site_nail": {"en": "Nail", "kn": "ಉಗುರು", "hi": "नाखून"},
    "noun_eye": {"en": "eyelid", "kn": "ಕಣ್ಣಿನ ರೆಪ್ಪೆ", "hi": "पलक"},
    "noun_palm": {"en": "palm", "kn": "ಅಂಗೈ", "hi": "हथेली"},
    "noun_nail": {"en": "nail bed", "kn": "ಉಗುರಿನ ತಳ", "hi": "नाखून"},
    "how_eye": {"en": "Gently pull down the lower eyelid with one finger. Photograph the red inner rim.",
                "kn": "ಒಂದು ಬೆರಳಿನಿಂದ ಕೆಳ ರೆಪ್ಪೆಯನ್ನು ನಿಧಾನವಾಗಿ ಕೆಳಗೆ ಎಳೆಯಿರಿ. ಒಳಗಿನ ಕೆಂಪು ಅಂಚಿನ ಫೋಟೋ ತೆಗೆಯಿರಿ.",
                "hi": "एक उँगली से निचली पलक को धीरे से नीचे खींचें। भीतर के लाल किनारे की फ़ोटो लें।"},
    "how_palm": {"en": "Open the hand flat, palm up. Fill the frame with the centre of the palm.",
                 "kn": "ಕೈಯನ್ನು ಚಪ್ಪಟೆಯಾಗಿ ತೆರೆಯಿರಿ, ಅಂಗೈ ಮೇಲಕ್ಕೆ. ಅಂಗೈಯ ಮಧ್ಯಭಾಗ ಚೌಕಟ್ಟು ತುಂಬಲಿ.",
                 "hi": "हाथ को सीधा खोलें, हथेली ऊपर। हथेली का बीच वाला हिस्सा फ़्रेम में भरें।"},
    "how_nail": {"en": "Rest the fingers flat. Photograph the nail beds from above.",
                 "kn": "ಬೆರಳುಗಳನ್ನು ಚಪ್ಪಟೆಯಾಗಿ ಇಡಿ. ಮೇಲಿನಿಂದ ಉಗುರಿನ ತಳಗಳ ಫೋಟೋ ತೆಗೆಯಿರಿ.",
                 "hi": "उँगलियाँ सीधी रखें। ऊपर से नाखूनों की फ़ोटो लें।"},
    "tested_eye": {"en": "Tested on 220 children with lab Hb.", "kn": "ಪ್ರಯೋಗಾಲಯ Hb ಇರುವ 220 ಮಕ್ಕಳ ಮೇಲೆ ಪರೀಕ್ಷಿಸಲಾಗಿದೆ.",
                   "hi": "लैब Hb वाले 220 बच्चों पर जाँचा गया।"},
    "tested_palm": {"en": "Tested on 522 children, folder labels.", "kn": "522 ಮಕ್ಕಳ ಮೇಲೆ ಪರೀಕ್ಷಿಸಲಾಗಿದೆ, ಫೋಲ್ಡರ್ ಲೇಬಲ್‌ಗಳು.",
                    "hi": "522 बच्चों पर जाँचा गया, फ़ोल्डर लेबल।"},
    "tested_nail": {"en": "Tested on 530 children, folder labels.", "kn": "530 ಮಕ್ಕಳ ಮೇಲೆ ಪರೀಕ್ಷಿಸಲಾಗಿದೆ, ಫೋಲ್ಡರ್ ಲೇಬಲ್‌ಗಳು.",
                    "hi": "530 बच्चों पर जाँचा गया, फ़ोल्डर लेबल।"},
    "tip_daylight": {"en": "Daylight", "kn": "ಹಗಲು ಬೆಳಕು", "hi": "दिन की रोशनी"},
    "tip_noflash": {"en": "No flash", "kn": "ಫ್ಲ್ಯಾಶ್ ಬೇಡ", "hi": "फ़्लैश नहीं"},
    "tip_nomakeup": {"en": "No eye makeup", "kn": "ಕಣ್ಣಿನ ಮೇಕಪ್ ಬೇಡ", "hi": "आँखों का मेकअप नहीं"},
    "tip_flat": {"en": "Hand flat", "kn": "ಕೈ ಚಪ್ಪಟೆ", "hi": "हाथ सीधा"},
    "tip_nopolish": {"en": "No nail polish", "kn": "ನೇಲ್ ಪಾಲಿಶ್ ಬೇಡ", "hi": "नेल पॉलिश नहीं"},
    "tip_still": {"en": "Hold still", "kn": "ಸ್ಥಿರವಾಗಿ ಹಿಡಿಯಿರಿ", "hi": "स्थिर रखें"},
    "use_site": {"en": "Use {site}", "kn": "{site} ಆಯ್ಕೆಮಾಡಿ", "hi": "{site} चुनें"},
    "selected": {"en": "Selected", "kn": "ಆಯ್ಕೆಯಾಗಿದೆ", "hi": "चुना गया"},

    # ---------------------------------------------------------------- screen: photo
    "step_photo": {"en": "Photo of the {site}", "kn": "{site} ಫೋಟೋ", "hi": "{site} की फ़ोटो"},
    "step_photo_todo": {"en": "Photo", "kn": "ಫೋಟೋ", "hi": "फ़ोटो"},
    "choose_first": {"en": "Choose a site above, or pick a sample patient.",
                     "kn": "ಮೇಲೆ ಒಂದು ಭಾಗವನ್ನು ಆರಿಸಿ, ಅಥವಾ ಮಾದರಿ ರೋಗಿಯನ್ನು ಆರಿಸಿ.",
                     "hi": "ऊपर एक अंग चुनें, या नमूना मरीज़ चुनें।"},
    "tab_camera": {"en": "Camera", "kn": "ಕ್ಯಾಮೆರಾ", "hi": "कैमरा"},
    "tab_upload": {"en": "Upload", "kn": "ಅಪ್‌ಲೋಡ್", "hi": "अपलोड"},
    "tab_sample": {"en": "Sample patient", "kn": "ಮಾದರಿ ರೋಗಿ", "hi": "नमूना मरीज़"},
    "camera_label": {"en": "Take a photo", "kn": "ಫೋಟೋ ತೆಗೆಯಿರಿ", "hi": "फ़ोटो लें"},
    "upload_label": {"en": "Choose a photo (JPG or PNG)", "kn": "ಫೋಟೋ ಆರಿಸಿ (JPG ಅಥವಾ PNG)",
                     "hi": "फ़ोटो चुनें (JPG या PNG)"},
    "no_photo": {"en": "No photo yet. Take one, upload one or pick a sample patient.",
                 "kn": "ಇನ್ನೂ ಫೋಟೋ ಇಲ್ಲ. ಒಂದನ್ನು ತೆಗೆಯಿರಿ, ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಮಾದರಿ ರೋಗಿಯನ್ನು ಆರಿಸಿ.",
                 "hi": "अभी कोई फ़ोटो नहीं। एक फ़ोटो लें, अपलोड करें या नमूना मरीज़ चुनें।"},
    "bad_image": {"en": "This file could not be read as a photo. Try a JPG or PNG.",
                  "kn": "ಈ ಫೈಲನ್ನು ಫೋಟೋ ಆಗಿ ಓದಲಾಗಲಿಲ್ಲ. JPG ಅಥವಾ PNG ಪ್ರಯತ್ನಿಸಿ.",
                  "hi": "यह फ़ाइल फ़ोटो के रूप में नहीं पढ़ी जा सकी। JPG या PNG आज़माएँ।"},
    "samples_title": {"en": "Sample patients", "kn": "ಮಾದರಿ ರೋಗಿಗಳು", "hi": "नमूना मरीज़"},
    "samples_lede": {
        "en": "Real photos from the training sets, to show the flow. Each shows its out-of-fold score, from a model that "
              "did not see that child. Not a test of accuracy.",
        "kn": "ಹರಿವನ್ನು ತೋರಿಸಲು ತರಬೇತಿ ಸೆಟ್‌ಗಳ ನಿಜವಾದ ಫೋಟೋಗಳು. ಪ್ರತಿಯೊಂದೂ ಆ ಮಗುವನ್ನು ನೋಡದ ಮಾದರಿಯ ಅಂಕವನ್ನು ತೋರಿಸುತ್ತದೆ. "
              "ನಿಖರತೆಯ ಪರೀಕ್ಷೆಯಲ್ಲ.",
        "hi": "प्रक्रिया दिखाने के लिए ट्रेनिंग सेट की असली फ़ोटो। हर एक उस मॉडल का स्कोर दिखाती है जिसने उस बच्चे को नहीं देखा। "
              "सटीकता की जाँच नहीं।",
    },
    "sample_n": {"en": "Sample {n}", "kn": "ಮಾದರಿ {n}", "hi": "नमूना {n}"},
    "load_sample": {"en": "Load", "kn": "ತೆರೆಯಿರಿ", "hi": "खोलें"},
    "tissue_auto": {"en": "Tissue found automatically from the clear background.",
                    "kn": "ಖಾಲಿ ಹಿನ್ನೆಲೆಯಿಂದ ಅಂಗಾಂಶವನ್ನು ಸ್ವಯಂ ಗುರುತಿಸಲಾಗಿದೆ.",
                    "hi": "साफ़ पृष्ठभूमि से ऊतक अपने-आप पहचाना गया।"},
    "tissue_whole": {"en": "This photo is already cropped to the tissue.",
                     "kn": "ಈ ಫೋಟೋವನ್ನು ಈಗಾಗಲೇ ಅಂಗಾಂಶಕ್ಕೆ ಕತ್ತರಿಸಲಾಗಿದೆ.", "hi": "यह फ़ोटो पहले से ऊतक तक कटी हुई है।"},
    "tissue_drag": {"en": "Tap the {site}, or drag a box over it. For the eye, box only the pink inner eyelid.",
                    "kn": "{site} ಮೇಲೆ ತಟ್ಟಿ, ಅಥವಾ ಅದರ ಮೇಲೆ ಚೌಕ ಎಳೆಯಿರಿ. ಕಣ್ಣಿಗೆ, ಗುಲಾಬಿ ಒಳರೆಪ್ಪೆಯನ್ನು ಮಾತ್ರ ಚೌಕದಲ್ಲಿ ಸೇರಿಸಿ.",
                    "hi": "{site} पर टैप करें, या उस पर एक बॉक्स खींचें। आँख के लिए केवल गुलाबी भीतरी पलक पर बॉक्स बनाएँ।"},
    "tissue_selected": {"en": "Selected. Tap or drag again to change.",
                        "kn": "ಆಯ್ಕೆಯಾಗಿದೆ. ಬದಲಿಸಲು ಮತ್ತೆ ತಟ್ಟಿ ಅಥವಾ ಎಳೆಯಿರಿ.",
                        "hi": "चुना गया। बदलने के लिए फिर से टैप करें या खींचें।"},
    "tissue_small": {"en": "That area is too small. Tap the middle of the {site}, or drag a bigger box.",
                     "kn": "ಆ ಭಾಗ ತುಂಬಾ ಚಿಕ್ಕದು. {site} ಮಧ್ಯದಲ್ಲಿ ತಟ್ಟಿ, ಅಥವಾ ದೊಡ್ಡ ಚೌಕ ಎಳೆಯಿರಿ.",
                     "hi": "वह हिस्सा बहुत छोटा है। {site} के बीच में टैप करें, या बड़ा बॉक्स खींचें।"},
    "quality_title": {"en": "Photo check", "kn": "ಫೋಟೋ ಪರಿಶೀಲನೆ", "hi": "फ़ोटो जाँच"},
    "quality_wait": {"en": "Select the tissue to run the checks.", "kn": "ಪರಿಶೀಲನೆಗೆ ಅಂಗಾಂಶವನ್ನು ಆಯ್ಕೆಮಾಡಿ.",
                     "hi": "जाँच के लिए ऊतक चुनें।"},
    "quality_pass": {"en": "All checks passed.", "kn": "ಎಲ್ಲಾ ಪರಿಶೀಲನೆಗಳು ಸರಿ.", "hi": "सभी जाँच ठीक हैं।"},
    "q_light": {"en": "Light", "kn": "ಬೆಳಕು", "hi": "रोशनी"},
    "q_glare": {"en": "Glare", "kn": "ಹೊಳಪು", "hi": "चमक"},
    "q_sharp": {"en": "Sharpness", "kn": "ಸ್ಪಷ್ಟತೆ", "hi": "साफ़पन"},
    "q_makeup": {"en": "Makeup or lashes", "kn": "ಮೇಕಪ್ ಅಥವಾ ರೆಪ್ಪೆಗೂದಲು", "hi": "मेकअप या पलकें"},
    "q_ok": {"en": "ok", "kn": "ಸರಿ", "hi": "ठीक"},
    "q_retake": {"en": "retake", "kn": "ಮತ್ತೆ ತೆಗೆಯಿರಿ", "hi": "दोबारा लें"},
    "fix_light": {"en": "Too dark. Move into daylight and retake.",
                  "kn": "ತುಂಬಾ ಕತ್ತಲು. ಹಗಲು ಬೆಳಕಿಗೆ ಬನ್ನಿ ಮತ್ತು ಮತ್ತೆ ತೆಗೆಯಿರಿ.",
                  "hi": "बहुत अँधेरा है। दिन की रोशनी में आएँ और दोबारा लें।"},
    "fix_glare": {"en": "Too much glare. Turn away from the window and retake.",
                  "kn": "ಹೆಚ್ಚು ಹೊಳಪು. ಕಿಟಕಿಯಿಂದ ದೂರ ತಿರುಗಿ ಮತ್ತೆ ತೆಗೆಯಿರಿ.",
                  "hi": "बहुत चमक है। खिड़की से मुँह फेरें और दोबारा लें।"},
    "fix_sharp": {"en": "Blurred. Hold the phone still, tap to focus and retake.",
                  "kn": "ಮಸುಕಾಗಿದೆ. ಫೋನನ್ನು ಸ್ಥಿರವಾಗಿ ಹಿಡಿದು, ಫೋಕಸ್‌ಗೆ ತಟ್ಟಿ ಮತ್ತೆ ತೆಗೆಯಿರಿ.",
                  "hi": "धुंधला है। फ़ोन स्थिर रखें, फ़ोकस के लिए टैप करें और दोबारा लें।"},
    "fix_makeup": {
        "en": "Makeup or lashes in the photo. Select only the pink inner eyelid, or remove eye makeup and retake.",
        "kn": "ಫೋಟೋದಲ್ಲಿ ಮೇಕಪ್ ಅಥವಾ ರೆಪ್ಪೆಗೂದಲು ಇದೆ. ಗುಲಾಬಿ ಒಳರೆಪ್ಪೆಯನ್ನು ಮಾತ್ರ ಆಯ್ಕೆಮಾಡಿ, ಅಥವಾ ಕಣ್ಣಿನ ಮೇಕಪ್ ತೆಗೆದು ಮತ್ತೆ "
              "ತೆಗೆಯಿರಿ.",
        "hi": "फ़ोटो में मेकअप या पलकें हैं। केवल गुलाबी भीतरी पलक चुनें, या आँखों का मेकअप हटाकर दोबारा लें।",
    },
    "preview_title": {"en": "Pixels measured", "kn": "ಅಳೆದ ಪಿಕ್ಸೆಲ್‌ಗಳು", "hi": "मापे गए पिक्सेल"},
    "preview_text": {
        "en": "Blue: measured. Grey: removed as makeup, lashes or glare ({pct}% of the selection).",
        "kn": "ನೀಲಿ: ಅಳೆಯಲಾಗಿದೆ. ಬೂದು: ಮೇಕಪ್, ರೆಪ್ಪೆಗೂದಲು ಅಥವಾ ಹೊಳಪು ಎಂದು ತೆಗೆದದ್ದು (ಆಯ್ಕೆಯ {pct}%).",
        "hi": "नीला: मापा गया। धूसर: मेकअप, पलकें या चमक मानकर हटाया गया (चयन का {pct}%)।",
    },
    "analyse": {"en": "See result", "kn": "ಫಲಿತಾಂಶ ನೋಡಿ", "hi": "नतीजा देखें"},

    # ---------------------------------------------------------------- screen: result
    "step_result": {"en": "Result", "kn": "ಫಲಿತಾಂಶ", "hi": "नतीजा"},
    "refer": {"en": "Refer for Hb test", "kn": "Hb ಪರೀಕ್ಷೆಗೆ ಕಳುಹಿಸಿ", "hi": "Hb जाँच के लिए भेजें"},
    "normal": {"en": "Normal", "kn": "ಸಾಮಾನ್ಯ", "hi": "सामान्य"},
    "likely_anaemic": {"en": "Likely anaemic", "kn": "ರಕ್ತಹೀನತೆ ಇರುವ ಸಾಧ್ಯತೆ", "hi": "एनीमिया की संभावना"},
    "likely_normal": {"en": "Likely not anaemic", "kn": "ರಕ್ತಹೀನತೆ ಇಲ್ಲದಿರುವ ಸಾಧ್ಯತೆ", "hi": "एनीमिया न होने की संभावना"},
    "prob_line": {"en": "{word}, {p}% chance", "kn": "{word}, {p}% ಸಾಧ್ಯತೆ", "hi": "{word}, {p}% संभावना"},
    "band_explain": {"en": "Among children who scored like this, {lo}–{hi}% were anaemic.",
                     "kn": "ಇದೇ ರೀತಿ ಅಂಕ ಪಡೆದ ಮಕ್ಕಳಲ್ಲಿ {lo}–{hi}% ರಕ್ತಹೀನರಾಗಿದ್ದರು.",
                     "hi": "इसी तरह स्कोर करने वाले बच्चों में {lo}–{hi}% को एनीमिया था।"},
    "gauge_label": {"en": "chance of anaemia", "kn": "ರಕ್ತಹೀನತೆಯ ಸಾಧ್ಯತೆ", "hi": "एनीमिया की संभावना"},
    "low_conf": {"en": "Low confidence", "kn": "ಕಡಿಮೆ ವಿಶ್ವಾಸ", "hi": "कम भरोसा"},
    "unfamiliar": {"en": "This photo looks unlike the training photos, so the result is less reliable.",
                   "kn": "ಈ ಫೋಟೋ ತರಬೇತಿ ಫೋಟೋಗಳಂತೆ ಕಾಣುವುದಿಲ್ಲ, ಆದ್ದರಿಂದ ಫಲಿತಾಂಶ ಕಡಿಮೆ ವಿಶ್ವಾಸಾರ್ಹ.",
                   "hi": "यह फ़ोटो ट्रेनिंग फ़ोटो जैसी नहीं दिखती, इसलिए नतीजा कम भरोसेमंद है।"},
    "age_outside": {
        "en": "The models were trained on young children (eye 6–59 months, palm and nail under 5 years), so this result "
              "is less reliable for this age band.",
        "kn": "ಮಾದರಿಗಳು ಚಿಕ್ಕ ಮಕ್ಕಳಿಂದ ಕಲಿತಿವೆ (ಕಣ್ಣು 6–59 ತಿಂಗಳು, ಅಂಗೈ ಮತ್ತು ಉಗುರು 5 ವರ್ಷದೊಳಗೆ), ಆದ್ದರಿಂದ ಈ ವಯಸ್ಸಿನ "
              "ಗುಂಪಿಗೆ ಫಲಿತಾಂಶ ಕಡಿಮೆ ವಿಶ್ವಾಸಾರ್ಹ.",
        "hi": "मॉडल छोटे बच्चों से सीखे हैं (आँख 6–59 महीने, हथेली और नाखून 5 साल से कम), इसलिए इस आयु वर्ग के लिए नतीजा "
              "कम भरोसेमंद है।",
    },
    "strip_ghana_note": {"en": "Palm and nail have no Hb values: the strip position is a colour position only.",
                         "kn": "ಅಂಗೈ ಮತ್ತು ಉಗುರಿಗೆ Hb ಮೌಲ್ಯಗಳಿಲ್ಲ: ಪಟ್ಟಿಯ ಸ್ಥಾನ ಬಣ್ಣದ ಸ್ಥಾನ ಮಾತ್ರ.",
                         "hi": "हथेली और नाखून के Hb मान नहीं हैं: पट्टी पर स्थिति केवल रंग की स्थिति है।"},
    "swatch_title": {"en": "Tissue colour", "kn": "ಅಂಗಾಂಶದ ಬಣ್ಣ", "hi": "ऊतक का रंग"},
    "swatch_this": {"en": "This child", "kn": "ಈ ಮಗು", "hi": "यह बच्चा"},
    "swatch_healthy": {"en": "Typical healthy", "kn": "ಸಾಮಾನ್ಯ ಆರೋಗ್ಯವಂತ", "hi": "सामान्य स्वस्थ"},
    "swatch_anaemic": {"en": "Typical anaemic", "kn": "ಸಾಮಾನ್ಯ ರಕ್ತಹೀನ", "hi": "सामान्य एनीमिया"},
    "why": {"en": "Why", "kn": "ಏಕೆ", "hi": "क्यों"},
    "r_redness_low": {"en": "The {site} is less red than {pct}% of healthy children.",
                      "kn": "{site} {pct}% ಆರೋಗ್ಯವಂತ ಮಕ್ಕಳಿಗಿಂತ ಕಡಿಮೆ ಕೆಂಪಾಗಿದೆ.",
                      "hi": "{site} {pct}% स्वस्थ बच्चों से कम लाल है।"},
    "r_redness_high": {"en": "The {site} is redder than {pct}% of healthy children.",
                       "kn": "{site} {pct}% ಆರೋಗ್ಯವಂತ ಮಕ್ಕಳಿಗಿಂತ ಹೆಚ್ಚು ಕೆಂಪಾಗಿದೆ.",
                       "hi": "{site} {pct}% स्वस्थ बच्चों से ज़्यादा लाल है।"},
    "r_lightness_low": {"en": "The {site} is darker than {pct}% of healthy children.",
                        "kn": "{site} {pct}% ಆರೋಗ್ಯವಂತ ಮಕ್ಕಳಿಗಿಂತ ಗಾಢವಾಗಿದೆ.",
                        "hi": "{site} {pct}% स्वस्थ बच्चों से गहरा है।"},
    "r_lightness_high": {"en": "The {site} is paler than {pct}% of healthy children.",
                         "kn": "{site} {pct}% ಆರೋಗ್ಯವಂತ ಮಕ್ಕಳಿಗಿಂತ ಬಿಳಿಚಿದೆ.",
                         "hi": "{site} {pct}% स्वस्थ बच्चों से फीका है।"},
    "r_blood_index_low": {"en": "Its blood-colour index is lower than in {pct}% of healthy children.",
                          "kn": "ಇದರ ರಕ್ತ-ಬಣ್ಣ ಸೂಚ್ಯಂಕ {pct}% ಆರೋಗ್ಯವಂತ ಮಕ್ಕಳಿಗಿಂತ ಕಡಿಮೆ.",
                          "hi": "इसका रक्त-रंग सूचकांक {pct}% स्वस्थ बच्चों से कम है।"},
    "r_blood_index_high": {"en": "Its blood-colour index is higher than in {pct}% of healthy children.",
                           "kn": "ಇದರ ರಕ್ತ-ಬಣ್ಣ ಸೂಚ್ಯಂಕ {pct}% ಆರೋಗ್ಯವಂತ ಮಕ್ಕಳಿಗಿಂತ ಹೆಚ್ಚು.",
                           "hi": "इसका रक्त-रंग सूचकांक {pct}% स्वस्थ बच्चों से ज़्यादा है।"},
    "r_red_share_low": {"en": "Red makes up less of its colour than in {pct}% of healthy children.",
                        "kn": "ಇದರ ಬಣ್ಣದಲ್ಲಿ ಕೆಂಪಿನ ಪಾಲು {pct}% ಆರೋಗ್ಯವಂತ ಮಕ್ಕಳಿಗಿಂತ ಕಡಿಮೆ.",
                        "hi": "इसके रंग में लाल का हिस्सा {pct}% स्वस्थ बच्चों से कम है।"},
    "r_red_share_high": {"en": "Red makes up more of its colour than in {pct}% of healthy children.",
                         "kn": "ಇದರ ಬಣ್ಣದಲ್ಲಿ ಕೆಂಪಿನ ಪಾಲು {pct}% ಆರೋಗ್ಯವಂತ ಮಕ್ಕಳಿಗಿಂತ ಹೆಚ್ಚು.",
                         "hi": "इसके रंग में लाल का हिस्सा {pct}% स्वस्थ बच्चों से ज़्यादा है।"},
    "r_tone_low": {"en": "Its colour is less yellow than in {pct}% of healthy children.",
                   "kn": "ಇದರ ಬಣ್ಣ {pct}% ಆರೋಗ್ಯವಂತ ಮಕ್ಕಳಿಗಿಂತ ಕಡಿಮೆ ಹಳದಿ.",
                   "hi": "इसका रंग {pct}% स्वस्थ बच्चों से कम पीला है।"},
    "r_tone_high": {"en": "Its colour is more yellow than in {pct}% of healthy children.",
                    "kn": "ಇದರ ಬಣ್ಣ {pct}% ಆರೋಗ್ಯವಂತ ಮಕ್ಕಳಿಗಿಂತ ಹೆಚ್ಚು ಹಳದಿ.",
                    "hi": "इसका रंग {pct}% स्वस्थ बच्चों से ज़्यादा पीला है।"},
    "reasons_none_refer": {
        "en": "None of these measures is on the anaemic side by itself: the model combines them, so treat this result "
              "with extra care.",
        "kn": "ಇವುಗಳಲ್ಲಿ ಯಾವುದೂ ತಾನಾಗಿ ರಕ್ತಹೀನತೆಯ ಕಡೆ ಇಲ್ಲ: ಮಾದರಿ ಇವನ್ನು ಸೇರಿಸಿ ನೋಡುತ್ತದೆ, ಆದ್ದರಿಂದ ಈ ಫಲಿತಾಂಶವನ್ನು ಹೆಚ್ಚು "
              "ಎಚ್ಚರಿಕೆಯಿಂದ ನೋಡಿ.",
        "hi": "इनमें से कोई माप अकेले एनीमिया की ओर नहीं है: मॉडल इन्हें मिलाकर देखता है, इसलिए इस नतीजे को ज़्यादा सावधानी से "
              "देखें।",
    },
    "reasons_none_normal": {
        "en": "None of these measures is on the healthy side by itself: the model combines them, so treat this result "
              "with extra care.",
        "kn": "ಇವುಗಳಲ್ಲಿ ಯಾವುದೂ ತಾನಾಗಿ ಆರೋಗ್ಯದ ಕಡೆ ಇಲ್ಲ: ಮಾದರಿ ಇವನ್ನು ಸೇರಿಸಿ ನೋಡುತ್ತದೆ, ಆದ್ದರಿಂದ ಈ ಫಲಿತಾಂಶವನ್ನು ಹೆಚ್ಚು "
              "ಎಚ್ಚರಿಕೆಯಿಂದ ನೋಡಿ.",
        "hi": "इनमें से कोई माप अकेले स्वस्थ की ओर नहीं है: मॉडल इन्हें मिलाकर देखता है, इसलिए इस नतीजे को ज़्यादा सावधानी से "
              "देखें।",
    },
    "sev_title": {"en": "Rough severity", "kn": "ಅಂದಾಜು ತೀವ್ರತೆ", "hi": "अनुमानित गंभीरता"},
    "sev_mild": {"en": "Mild", "kn": "ಸೌಮ್ಯ", "hi": "हल्का"},
    "sev_moderate": {"en": "Moderate", "kn": "ಮಧ್ಯಮ", "hi": "मध्यम"},
    "sev_severe": {"en": "Severe", "kn": "ತೀವ್ರ", "hi": "गंभीर"},
    "sev_none": {"en": "None expected.", "kn": "ನಿರೀಕ್ಷಿತವಿಲ್ಲ.", "hi": "अपेक्षित नहीं।"},
    "sev_line": {"en": "{sev}: colour suggests about {hb} g/dL, give or take {mae}.",
                 "kn": "{sev}: ಬಣ್ಣದ ಪ್ರಕಾರ ಸುಮಾರು {hb} g/dL, ±{mae}.",
                 "hi": "{sev}: रंग से लगभग {hb} g/dL, ±{mae}।"},
    "sev_none_ghana": {"en": "Not available for palm or nail: those photo sets have no Hb values.",
                       "kn": "ಅಂಗೈ ಅಥವಾ ಉಗುರಿಗೆ ಲಭ್ಯವಿಲ್ಲ: ಆ ಫೋಟೋ ಸೆಟ್‌ಗಳಲ್ಲಿ Hb ಮೌಲ್ಯಗಳಿಲ್ಲ.",
                       "hi": "हथेली या नाखून के लिए उपलब्ध नहीं: उन फ़ोटो सेट में Hb मान नहीं हैं।"},
    "severity_caveat": {
        "en": "Severity is a rough guide from colour only. Only a blood test gives the Hb level.",
        "kn": "ತೀವ್ರತೆ ಬಣ್ಣದಿಂದ ಮಾತ್ರ ಅಂದಾಜು. ರಕ್ತ ಪರೀಕ್ಷೆ ಮಾತ್ರ Hb ಮಟ್ಟವನ್ನು ನೀಡುತ್ತದೆ.",
        "hi": "गंभीरता केवल रंग से एक मोटा अनुमान है। Hb स्तर केवल खून की जाँच से पता चलता है।",
    },
    "next_refer": {"en": "Next step: visit the PHC for a finger-prick Hb test within 7 days.",
                   "kn": "ಮುಂದಿನ ಹೆಜ್ಜೆ: 7 ದಿನಗಳ ಒಳಗೆ ಬೆರಳು ಚುಚ್ಚುವ Hb ಪರೀಕ್ಷೆಗಾಗಿ PHCಗೆ ಭೇಟಿ ನೀಡಿ.",
                   "hi": "अगला कदम: 7 दिनों के भीतर उँगली से Hb जाँच के लिए PHC जाएँ।"},
    "next_normal": {"en": "No referral needed today. Screen again at the next visit.",
                    "kn": "ಇಂದು ಶಿಫಾರಸು ಅಗತ್ಯವಿಲ್ಲ. ಮುಂದಿನ ಭೇಟಿಯಲ್ಲಿ ಮತ್ತೆ ತಪಾಸಣೆ ಮಾಡಿ.",
                    "hi": "आज रेफ़रल की ज़रूरत नहीं। अगली विज़िट पर फिर जाँच करें।"},
    "sample_banner": {"en": "Sample patient {n}: {site} photo from the training data.",
                      "kn": "ಮಾದರಿ ರೋಗಿ {n}: ತರಬೇತಿ ದತ್ತಾಂಶದ {site} ಫೋಟೋ.",
                      "hi": "नमूना मरीज़ {n}: ट्रेनिंग डेटा से {site} की फ़ोटो।"},
    "truth_hb": {"en": "Lab Hb {hb} g/dL.", "kn": "ಪ್ರಯೋಗಾಲಯ Hb {hb} g/dL.", "hi": "लैब Hb {hb} g/dL।"},
    "truth_folder": {"en": "Folder label: {label}.", "kn": "ಫೋಲ್ಡರ್ ಲೇಬಲ್: {label}.", "hi": "फ़ोल्डर लेबल: {label}।"},
    "word_anaemic": {"en": "anaemic", "kn": "ರಕ್ತಹೀನತೆ", "hi": "एनीमिया"},
    "word_not_anaemic": {"en": "not anaemic", "kn": "ರಕ್ತಹೀನತೆ ಇಲ್ಲ", "hi": "एनीमिया नहीं"},
    "limits_title": {"en": "Known limits", "kn": "ತಿಳಿದಿರುವ ಮಿತಿಗಳು", "hi": "ज्ञात सीमाएँ"},
    "limit_makeup": {
        "en": "Makeup: kajal, mascara and lashes darken the eyelid. Dark pixels are removed, but smudged makeup can "
              "still change the colour.",
        "kn": "ಮೇಕಪ್: ಕಾಜಲ್, ಮಸ್ಕರಾ ಮತ್ತು ರೆಪ್ಪೆಗೂದಲು ರೆಪ್ಪೆಯನ್ನು ಗಾಢಗೊಳಿಸುತ್ತವೆ. ಗಾಢ ಪಿಕ್ಸೆಲ್‌ಗಳನ್ನು ತೆಗೆಯಲಾಗುತ್ತದೆ, ಆದರೆ "
              "ಹರಡಿದ ಮೇಕಪ್ ಬಣ್ಣವನ್ನು ಬದಲಿಸಬಹುದು.",
        "hi": "मेकअप: काजल, मस्कारा और पलकें पलक को गहरा करते हैं। गहरे पिक्सेल हटाए जाते हैं, पर फैला हुआ मेकअप रंग बदल "
              "सकता है।",
    },
    "limit_adult": {"en": "Adult eyes: no adult photos were in the training data.",
                    "kn": "ವಯಸ್ಕರ ಕಣ್ಣುಗಳು: ತರಬೇತಿ ದತ್ತಾಂಶದಲ್ಲಿ ವಯಸ್ಕರ ಫೋಟೋಗಳಿರಲಿಲ್ಲ.",
                    "hi": "वयस्क आँखें: ट्रेनिंग डेटा में वयस्कों की कोई फ़ोटो नहीं थी।"},
    "limit_light": {
        "en": "Webcam and indoor light: the training photos were taken on phones, mostly in daylight. Laptop webcams "
              "and warm room lights shift the colour.",
        "kn": "ವೆಬ್‌ಕ್ಯಾಮ್ ಮತ್ತು ಒಳಾಂಗಣ ಬೆಳಕು: ತರಬೇತಿ ಫೋಟೋಗಳನ್ನು ಫೋನ್‌ಗಳಲ್ಲಿ, ಹೆಚ್ಚಾಗಿ ಹಗಲು ಬೆಳಕಿನಲ್ಲಿ ತೆಗೆಯಲಾಗಿದೆ. "
              "ಲ್ಯಾಪ್‌ಟಾಪ್ ವೆಬ್‌ಕ್ಯಾಮ್ ಮತ್ತು ಕೋಣೆಯ ಬೆಚ್ಚನೆಯ ಬೆಳಕು ಬಣ್ಣವನ್ನು ಬದಲಿಸುತ್ತವೆ.",
        "hi": "वेबकैम और घर के अंदर की रोशनी: ट्रेनिंग फ़ोटो फ़ोन से, ज़्यादातर दिन की रोशनी में ली गईं। लैपटॉप वेबकैम और "
              "कमरे की पीली रोशनी रंग बदल देती है।",
    },
    "limit_children": {"en": "Child-only training data: every training photo is of a child under 5 in Ghana.",
                       "kn": "ಮಕ್ಕಳ ದತ್ತಾಂಶ ಮಾತ್ರ: ಎಲ್ಲಾ ತರಬೇತಿ ಫೋಟೋಗಳು ಘಾನಾದ 5 ವರ್ಷದೊಳಗಿನ ಮಕ್ಕಳದ್ದು.",
                       "hi": "केवल बच्चों का डेटा: हर ट्रेनिंग फ़ोटो घाना के 5 साल से कम उम्र के बच्चे की है।"},

    # ---------------------------------------------------------------- results page
    "res_title": {"en": "Results", "kn": "ಫಲಿತಾಂಶಗಳು", "hi": "नतीजे"},
    "res_lede": {
        "en": "Eye model on 220 children with lab Hb (CP-AnemiC), tested with 5 x 5 repeated, patient-grouped "
              "cross-validation. Every number comes from children the model did not see.",
        "kn": "ಪ್ರಯೋಗಾಲಯ Hb ಇರುವ 220 ಮಕ್ಕಳ ಮೇಲಿನ ಕಣ್ಣಿನ ಮಾದರಿ (CP-AnemiC), 5 x 5 ಪುನರಾವರ್ತಿತ ರೋಗಿ-ಗುಂಪು ಅಡ್ಡ-ಪರಿಶೀಲನೆಯಿಂದ "
              "ಪರೀಕ್ಷಿಸಲಾಗಿದೆ. ಪ್ರತಿ ಸಂಖ್ಯೆ ಮಾದರಿ ನೋಡದ ಮಕ್ಕಳಿಂದ ಬಂದಿದೆ.",
        "hi": "लैब Hb वाले 220 बच्चों पर आँख का मॉडल (CP-AnemiC), 5 x 5 बार-बार मरीज़-समूह क्रॉस-वैलिडेशन से जाँचा गया। हर "
              "संख्या उन बच्चों से है जिन्हें मॉडल ने नहीं देखा।",
    },
    "res_cmp_title": {"en": "Model comparison", "kn": "ಮಾದರಿಗಳ ಹೋಲಿಕೆ", "hi": "मॉडल तुलना"},
    "res_cmp_lede": {
        "en": "Tuned inside each training fold, calibrated, with the threshold set for at least 80% sensitivity on inner "
              "folds. Mean over 25 held-out folds, 95% corrected interval.",
        "kn": "ಪ್ರತಿ ತರಬೇತಿ ಭಾಗದೊಳಗೆ ಹೊಂದಿಸಲಾಗಿದೆ, ಮಾಪನ ಮಾಡಲಾಗಿದೆ, ಒಳ ಭಾಗಗಳಲ್ಲಿ ಕನಿಷ್ಠ 80% ಸಂವೇದನಶೀಲತೆಗೆ ಮಿತಿ ನಿಗದಿ. 25 "
              "ಪ್ರತ್ಯೇಕ ಭಾಗಗಳ ಸರಾಸರಿ, 95% ತಿದ್ದಿದ ವ್ಯಾಪ್ತಿ.",
        "hi": "हर ट्रेनिंग हिस्से के अंदर ट्यून और कैलिब्रेट किया गया, अंदरूनी हिस्सों पर कम से कम 80% संवेदनशीलता के लिए सीमा "
              "तय। 25 अलग रखे गए हिस्सों का औसत, 95% सुधारी गई सीमा।",
    },
    "res_cmp_take": {
        "en": "No model is far ahead: the best ROC-AUC is {auc} ({model}), and the intervals overlap.",
        "kn": "ಯಾವ ಮಾದರಿಯೂ ಬಹಳ ಮುಂದಿಲ್ಲ: ಅತ್ಯುತ್ತಮ ROC-AUC {auc} ({model}), ಮತ್ತು ವ್ಯಾಪ್ತಿಗಳು ಒಂದರ ಮೇಲೊಂದು ಬರುತ್ತವೆ.",
        "hi": "कोई मॉडल बहुत आगे नहीं: सबसे अच्छा ROC-AUC {auc} ({model}) है, और सीमाएँ एक-दूसरे पर चढ़ी हैं।",
    },
    "res_cmp_note": {
        "en": "Small figure under each number: 95% interval over folds. Accuracy is not shown on purpose: with 42% "
              "anaemic it hides the trade-off below.",
        "kn": "ಪ್ರತಿ ಸಂಖ್ಯೆಯ ಕೆಳಗಿನ ಸಣ್ಣ ಅಂಕೆ: ಭಾಗಗಳ ಮೇಲಿನ 95% ವ್ಯಾಪ್ತಿ. ನಿಖರತೆಯನ್ನು ಉದ್ದೇಶಪೂರ್ವಕವಾಗಿ ತೋರಿಸಿಲ್ಲ: 42% "
              "ರಕ್ತಹೀನರಿರುವಾಗ ಅದು ಕೆಳಗಿನ ವಿನಿಮಯವನ್ನು ಮರೆಮಾಡುತ್ತದೆ.",
        "hi": "हर संख्या के नीचे छोटा अंक: हिस्सों पर 95% सीमा। सटीकता जानबूझकर नहीं दिखाई: 42% एनीमिया होने पर यह नीचे का "
              "समझौता छिपा देती है।",
    },
    "res_trade_title": {"en": "How sure is it?", "kn": "ಎಷ್ಟು ಖಚಿತ?", "hi": "कितना पक्का?"},
    "res_trade_lede": {
        "en": "Pick a model and move the threshold. Higher thresholds send fewer healthy children for a test, and miss "
              "more anaemic ones.",
        "kn": "ಒಂದು ಮಾದರಿಯನ್ನು ಆರಿಸಿ ಮತ್ತು ಮಿತಿಯನ್ನು ಸರಿಸಿ. ಹೆಚ್ಚಿನ ಮಿತಿ ಕಡಿಮೆ ಆರೋಗ್ಯವಂತ ಮಕ್ಕಳನ್ನು ಪರೀಕ್ಷೆಗೆ ಕಳುಹಿಸುತ್ತದೆ, "
              "ಆದರೆ ಹೆಚ್ಚು ರಕ್ತಹೀನರನ್ನು ತಪ್ಪಿಸುತ್ತದೆ.",
        "hi": "एक मॉडल चुनें और सीमा खिसकाएँ। ऊँची सीमा कम स्वस्थ बच्चों को जाँच के लिए भेजती है, और ज़्यादा एनीमिया वाले बच्चे "
              "छूट जाते हैं।",
    },
    "res_model": {"en": "Model", "kn": "ಮಾದರಿ", "hi": "मॉडल"},
    "res_threshold": {"en": "Threshold", "kn": "ಮಿತಿ", "hi": "सीमा"},
    "res_threshold_help": {
        "en": "Refer when the model's chance is at or above this. The default is the median of the thresholds the model "
              "learned inside its training folds.",
        "kn": "ಮಾದರಿಯ ಸಾಧ್ಯತೆ ಇದಕ್ಕೆ ಸಮ ಅಥವಾ ಹೆಚ್ಚಿದ್ದರೆ ಕಳುಹಿಸಿ. ಪೂರ್ವನಿಯೋಜಿತ ಮೌಲ್ಯ ತರಬೇತಿ ಭಾಗಗಳಲ್ಲಿ ಕಲಿತ ಮಿತಿಗಳ ಮಧ್ಯಮ.",
        "hi": "जब मॉडल की संभावना इसके बराबर या ज़्यादा हो तब भेजें। डिफ़ॉल्ट मान ट्रेनिंग हिस्सों में सीखी गई सीमाओं का माध्य है।",
    },
    "card_sens": {"en": "Sensitivity", "kn": "ಸಂವೇದನಶೀಲತೆ", "hi": "संवेदनशीलता"},
    "card_sens_sub": {"en": "anaemic children caught", "kn": "ಗುರುತಿಸಿದ ರಕ್ತಹೀನ ಮಕ್ಕಳು",
                      "hi": "पकड़े गए एनीमिया वाले बच्चे"},
    "card_spec": {"en": "Specificity", "kn": "ನಿರ್ದಿಷ್ಟತೆ", "hi": "विशिष्टता"},
    "card_spec_sub": {"en": "healthy children cleared", "kn": "ಬಿಡುಗಡೆಯಾದ ಆರೋಗ್ಯವಂತ ಮಕ್ಕಳು", "hi": "छोड़े गए स्वस्थ बच्चे"},
    "card_ppv": {"en": "Referrals that are anaemic", "kn": "ರಕ್ತಹೀನರಾದ ಶಿಫಾರಸುಗಳು", "hi": "भेजे गए जिनमें एनीमिया है"},
    "card_ppv_sub": {"en": "of every 100 referred", "kn": "ಪ್ರತಿ 100 ಶಿಫಾರಸುಗಳಲ್ಲಿ", "hi": "हर 100 भेजे गए में से"},
    "card_auc": {"en": "ROC-AUC", "kn": "ROC-AUC", "hi": "ROC-AUC"},
    "card_auc_sub": {"en": "for this model, any threshold", "kn": "ಈ ಮಾದರಿಗೆ, ಯಾವುದೇ ಮಿತಿ", "hi": "इस मॉडल के लिए, कोई भी सीमा"},
    "grid_take": {
        "en": "Out of 100 children screened: {n_an} anaemic, {caught} caught, {missed} missed; {healthy} healthy, {sent} "
              "sent for a test they didn't need.",
        "kn": "ತಪಾಸಣೆ ಮಾಡಿದ 100 ಮಕ್ಕಳಲ್ಲಿ: {n_an} ರಕ್ತಹೀನರು, {caught} ಗುರುತಿಸಲಾಗಿದೆ, {missed} ತಪ್ಪಿದೆ; {healthy} ಆರೋಗ್ಯವಂತರು, "
              "{sent} ಮಕ್ಕಳನ್ನು ಅಗತ್ಯವಿಲ್ಲದ ಪರೀಕ್ಷೆಗೆ ಕಳುಹಿಸಲಾಗಿದೆ.",
        "hi": "जाँचे गए 100 बच्चों में से: {n_an} को एनीमिया, {caught} पकड़े गए, {missed} छूटे; {healthy} स्वस्थ, {sent} बिना "
              "ज़रूरत जाँच के लिए भेजे गए।",
    },
    "legend_caught": {"en": "Anaemic, referred ({n})", "kn": "ರಕ್ತಹೀನ, ಕಳುಹಿಸಲಾಗಿದೆ ({n})", "hi": "एनीमिया, भेजा गया ({n})"},
    "legend_missed": {"en": "Anaemic, missed ({n})", "kn": "ರಕ್ತಹೀನ, ತಪ್ಪಿದೆ ({n})", "hi": "एनीमिया, छूटा ({n})"},
    "legend_sent": {"en": "Healthy, sent for a test ({n})", "kn": "ಆರೋಗ್ಯವಂತ, ಪರೀಕ್ಷೆಗೆ ಕಳುಹಿಸಲಾಗಿದೆ ({n})",
                    "hi": "स्वस्थ, जाँच के लिए भेजा गया ({n})"},
    "legend_cleared": {"en": "Healthy, cleared ({n})", "kn": "ಆರೋಗ್ಯವಂತ, ಬಿಡಲಾಗಿದೆ ({n})", "hi": "स्वस्थ, छोड़ा गया ({n})"},
    "grid_note": {
        "en": "Sensitivity {sens}, specificity {spec} at threshold {thr}, from the first repeat's pooled out-of-fold "
              "predictions (220 children), scaled to 100. The table above and Home report the mean over 25 folds, each "
              "at its own learned threshold, so they differ by a few points.",
        "kn": "ಮಿತಿ {thr} ನಲ್ಲಿ ಸಂವೇದನಶೀಲತೆ {sens}, ನಿರ್ದಿಷ್ಟತೆ {spec}, ಮೊದಲ ಪುನರಾವರ್ತನೆಯ ಸಂಯೋಜಿತ ಭಾಗ-ಹೊರಗಿನ ಮುನ್ಸೂಚನೆಗಳಿಂದ "
              "(220 ಮಕ್ಕಳು), 100ಕ್ಕೆ ಪ್ರಮಾಣೀಕರಿಸಲಾಗಿದೆ. ಮೇಲಿನ ಕೋಷ್ಟಕ ಮತ್ತು ಮುಖಪುಟ 25 ಭಾಗಗಳ ಸರಾಸರಿಯನ್ನು ತೋರಿಸುತ್ತವೆ, ಆದ್ದರಿಂದ "
              "ಕೆಲವು ಅಂಕಗಳ ವ್ಯತ್ಯಾಸವಿದೆ.",
        "hi": "सीमा {thr} पर संवेदनशीलता {sens}, विशिष्टता {spec}, पहली पुनरावृत्ति की जोड़ी गई आउट-ऑफ़-फ़ोल्ड भविष्यवाणियों से "
              "(220 बच्चे), 100 पर पैमाना। ऊपर की तालिका और होम 25 हिस्सों का औसत दिखाते हैं, इसलिए कुछ अंकों का फ़र्क है।",
    },
    "roc_take": {"en": "The dot is this threshold on the full trade-off curve; AUC {auc} means an anaemic child outscores a "
                       "healthy one {pct} of the time.",
                 "kn": "ಬಿಂದು ಪೂರ್ಣ ವಿನಿಮಯ ವಕ್ರರೇಖೆಯ ಮೇಲಿನ ಈ ಮಿತಿ; AUC {auc} ಎಂದರೆ ರಕ್ತಹೀನ ಮಗು {pct} ಬಾರಿ ಆರೋಗ್ಯವಂತ ಮಗುವಿಗಿಂತ "
                       "ಹೆಚ್ಚು ಅಂಕ ಪಡೆಯುತ್ತದೆ.",
                 "hi": "बिंदु पूरे समझौता वक्र पर यह सीमा है; AUC {auc} का मतलब है कि एनीमिया वाला बच्चा {pct} बार स्वस्थ बच्चे से "
                       "ऊँचा स्कोर पाता है।"},
    "cm_take": {"en": "Counts for all {n} children at this threshold: {fn} anaemic children would be missed.",
                "kn": "ಈ ಮಿತಿಯಲ್ಲಿ ಎಲ್ಲಾ {n} ಮಕ್ಕಳ ಎಣಿಕೆ: {fn} ರಕ್ತಹೀನ ಮಕ್ಕಳು ತಪ್ಪಿಹೋಗುತ್ತಾರೆ.",
                "hi": "इस सीमा पर सभी {n} बच्चों की गिनती: {fn} एनीमिया वाले बच्चे छूट जाएँगे।"},

    # ---------------------------------------------------------------- insights page
    "ins_title": {"en": "Insights", "kn": "ಒಳನೋಟಗಳು", "hi": "विश्लेषण"},
    "ins_lede": {
        "en": "What the data looks like, how the three body sites compare, what clustering finds, and what the protocol "
              "search learned.",
        "kn": "ದತ್ತಾಂಶ ಹೇಗಿದೆ, ಮೂರು ದೇಹಭಾಗಗಳು ಹೇಗೆ ಹೋಲುತ್ತವೆ, ಗುಂಪುಗಾರಿಕೆ ಏನು ಕಂಡುಹಿಡಿಯುತ್ತದೆ, ಮತ್ತು ಶೋಧನೆ ಏನು ಕಲಿಯಿತು.",
        "hi": "डेटा कैसा दिखता है, तीनों अंग कैसे तुलना करते हैं, क्लस्टरिंग क्या पाती है, और प्रोटोकॉल खोज ने क्या सीखा।",
    },
    "tab_data": {"en": "Data", "kn": "ದತ್ತಾಂಶ", "hi": "डेटा"},
    "tab_sites": {"en": "Eye vs palm vs nail", "kn": "ಕಣ್ಣು, ಅಂಗೈ, ಉಗುರು", "hi": "आँख, हथेली, नाखून"},
    "tab_clusters": {"en": "Clusters", "kn": "ಗುಂಪುಗಳು", "hi": "क्लस्टर"},
    "tab_search": {"en": "Search", "kn": "ಶೋಧನೆ", "hi": "खोज"},
    "data_title": {"en": "The eye data", "kn": "ಕಣ್ಣಿನ ದತ್ತಾಂಶ", "hi": "आँख का डेटा"},
    "data_lede": {"en": "CP-AnemiC primary set: {n} quality-clean conjunctiva photos of children aged 6–59 months in Ghana, "
                        "each with a lab Hb value.",
                  "kn": "CP-AnemiC ಮುಖ್ಯ ಸೆಟ್: ಘಾನಾದ 6–59 ತಿಂಗಳ ಮಕ್ಕಳ {n} ಗುಣಮಟ್ಟದ ಕಣ್ಣಿನ ಒಳರೆಪ್ಪೆ ಫೋಟೋಗಳು, ಪ್ರತಿಯೊಂದಕ್ಕೂ "
                        "ಪ್ರಯೋಗಾಲಯ Hb ಮೌಲ್ಯ.",
                  "hi": "CP-AnemiC मुख्य सेट: घाना के 6–59 महीने के बच्चों की {n} साफ़ गुणवत्ता वाली पलक की फ़ोटो, हर एक के "
                        "साथ लैब Hb मान।"},
    "t_balance": {"en": "{n_an} of {n} children ({pct}) are anaemic (Hb below 11 g/dL), so the classes are fairly balanced; "
                        "most anaemia is mild or moderate.",
                  "kn": "{n} ಮಕ್ಕಳಲ್ಲಿ {n_an} ({pct}) ರಕ್ತಹೀನರು (Hb 11 g/dL ಗಿಂತ ಕಡಿಮೆ), ಆದ್ದರಿಂದ ವರ್ಗಗಳು ಸಾಕಷ್ಟು ಸಮತೋಲಿತ; "
                        "ಹೆಚ್ಚಿನ ರಕ್ತಹೀನತೆ ಸೌಮ್ಯ ಅಥವಾ ಮಧ್ಯಮ.",
                  "hi": "{n} में से {n_an} बच्चों ({pct}) को एनीमिया है (Hb 11 g/dL से कम), इसलिए वर्ग काफ़ी संतुलित हैं; "
                        "ज़्यादातर एनीमिया हल्का या मध्यम है।"},
    "t_hb": {"en": "Hb runs from {lo} to {hi} g/dL; many children sit close to the cut-off, which is where colour "
                   "screening is hardest.",
             "kn": "Hb {lo} ರಿಂದ {hi} g/dL ವರೆಗೆ; ಅನೇಕ ಮಕ್ಕಳು ಮಿತಿಯ ಹತ್ತಿರ ಇದ್ದಾರೆ, ಅಲ್ಲಿ ಬಣ್ಣದ ತಪಾಸಣೆ ಅತ್ಯಂತ ಕಷ್ಟ.",
             "hi": "Hb {lo} से {hi} g/dL तक है; कई बच्चे सीमा के पास हैं, जहाँ रंग से जाँच सबसे कठिन है।"},
    "strength_weak": {"en": "weak", "kn": "ದುರ್ಬಲ", "hi": "कमज़ोर"},
    "strength_moderate": {"en": "moderate", "kn": "ಮಧ್ಯಮ", "hi": "मध्यम"},
    "strength_strong": {"en": "strong", "kn": "ಬಲವಾದ", "hi": "मज़बूत"},
    "t_scatter": {"en": "{feat} has a {strength} link with Hb (Spearman ρ = {r}): the classes overlap a lot, so no single "
                        "colour number separates them.",
                  "kn": "{feat} Hb ಜೊತೆ {strength} ಸಂಬಂಧ ಹೊಂದಿದೆ (Spearman ρ = {r}): ವರ್ಗಗಳು ಬಹಳ ಒಂದರ ಮೇಲೊಂದು ಬರುತ್ತವೆ, "
                        "ಆದ್ದರಿಂದ ಯಾವುದೇ ಒಂದು ಬಣ್ಣದ ಸಂಖ್ಯೆ ಅವನ್ನು ಬೇರ್ಪಡಿಸುವುದಿಲ್ಲ.",
                  "hi": "{feat} का Hb से {strength} संबंध है (Spearman ρ = {r}): वर्ग बहुत मिले-जुले हैं, इसलिए कोई एक रंग "
                        "संख्या उन्हें अलग नहीं करती।"},
    "t_gw": {"en": "Grey-world lighting correction weakens the link with Hb for {weaker} of {n} features, most for "
                   "{named}: it removes redness along with the light cast, so the model keeps raw colour.",
             "kn": "ಗ್ರೇ-ವರ್ಲ್ಡ್ ಬೆಳಕಿನ ತಿದ್ದುಪಡಿ {n} ಲಕ್ಷಣಗಳಲ್ಲಿ {weaker} ಕ್ಕೆ Hb ಸಂಬಂಧವನ್ನು ದುರ್ಬಲಗೊಳಿಸುತ್ತದೆ, ಹೆಚ್ಚಾಗಿ "
                   "{named}: ಇದು ಬೆಳಕಿನ ಛಾಯೆಯೊಂದಿಗೆ ಕೆಂಪನ್ನೂ ತೆಗೆಯುತ್ತದೆ, ಆದ್ದರಿಂದ ಮಾದರಿ ಮೂಲ ಬಣ್ಣವನ್ನು ಬಳಸುತ್ತದೆ.",
             "hi": "ग्रे-वर्ल्ड रोशनी सुधार {n} में से {weaker} विशेषताओं का Hb से संबंध कमज़ोर करता है, सबसे ज़्यादा {named}: "
                   "यह रोशनी की छाया के साथ लाली भी हटा देता है, इसलिए मॉडल मूल रंग रखता है।"},
    "sites_title": {"en": "Eye vs palm vs nail", "kn": "ಕಣ್ಣು, ಅಂಗೈ, ಉಗುರು ಹೋಲಿಕೆ", "hi": "आँख, हथेली और नाखून"},
    "sites_lede": {
        "en": "Each site has its own children and labels: eye uses lab Hb, palm and nail use folder labels from file "
              "names (about 3% label noise). Not a fair head-to-head.",
        "kn": "ಪ್ರತಿ ಭಾಗಕ್ಕೂ ತನ್ನದೇ ಮಕ್ಕಳು ಮತ್ತು ಲೇಬಲ್‌ಗಳು: ಕಣ್ಣು ಪ್ರಯೋಗಾಲಯ Hb ಬಳಸುತ್ತದೆ, ಅಂಗೈ ಮತ್ತು ಉಗುರು ಫೈಲ್ ಹೆಸರುಗಳ "
              "ಫೋಲ್ಡರ್ ಲೇಬಲ್‌ಗಳನ್ನು (ಸುಮಾರು 3% ಲೇಬಲ್ ದೋಷ). ನ್ಯಾಯವಾದ ನೇರ ಹೋಲಿಕೆಯಲ್ಲ.",
        "hi": "हर अंग के अपने बच्चे और लेबल हैं: आँख लैब Hb, हथेली और नाखून फ़ाइल नामों के फ़ोल्डर लेबल (लगभग 3% लेबल त्रुटि) "
              "इस्तेमाल करते हैं। सीधी तुलना उचित नहीं।",
    },
    "t_sites_table": {"en": "With all their data, {first} scores highest ({first_auc}), then {second} ({second_auc}) and "
                            "{third} ({third_auc}); palm and nail have more than twice as many photos as the eye.",
                      "kn": "ಎಲ್ಲಾ ದತ್ತಾಂಶದೊಂದಿಗೆ, {first} ಅತಿ ಹೆಚ್ಚು ({first_auc}), ನಂತರ {second} ({second_auc}) ಮತ್ತು {third} "
                            "({third_auc}); ಅಂಗೈ ಮತ್ತು ಉಗುರಿಗೆ ಕಣ್ಣಿಗಿಂತ ಎರಡು ಪಟ್ಟಿಗೂ ಹೆಚ್ಚು ಫೋಟೋಗಳಿವೆ.",
                      "hi": "पूरे डेटा के साथ {first} सबसे ऊँचा ({first_auc}), फिर {second} ({second_auc}) और {third} "
                            "({third_auc}); हथेली और नाखून के पास आँख से दोगुने से ज़्यादा फ़ोटो हैं।"},
    "t_equal": {"en": "At the same 220 photos each, the CP-AnemiC eye scores {eye}, palm {palm} and nail {nail}: palm's "
                      "lead above comes from having more data.",
                "kn": "ಪ್ರತಿಯೊಂದಕ್ಕೂ ಅದೇ 220 ಫೋಟೋಗಳಲ್ಲಿ, CP-AnemiC ಕಣ್ಣು {eye}, ಅಂಗೈ {palm} ಮತ್ತು ಉಗುರು {nail}: ಮೇಲಿನ "
                      "ಅಂಗೈಯ ಮುನ್ನಡೆ ಹೆಚ್ಚು ದತ್ತಾಂಶದಿಂದ ಬಂದಿದೆ.",
                "hi": "हर एक की उन्हीं 220 फ़ोटो पर, CP-AnemiC आँख {eye}, हथेली {palm} और नाखून {nail}: ऊपर हथेली की बढ़त "
                      "ज़्यादा डेटा से आती है।"},
    "t_equal_extra": {"en": " The secondary Ghana eye set scores {v}, but with folder labels and 66% anaemic it is not "
                            "comparable.",
                      "kn": " ದ್ವಿತೀಯ ಘಾನಾ ಕಣ್ಣಿನ ಸೆಟ್ {v} ಅಂಕ ಪಡೆಯುತ್ತದೆ, ಆದರೆ ಫೋಲ್ಡರ್ ಲೇಬಲ್‌ಗಳು ಮತ್ತು 66% ರಕ್ತಹೀನರಿಂದ ಅದು "
                            "ಹೋಲಿಸಲಾಗದು.",
                      "hi": " दूसरा घाना आँख सेट {v} पाता है, पर फ़ोल्डर लेबल और 66% एनीमिया के कारण यह तुलना योग्य नहीं।"},
    "t_curves": {"en": "Every site is still improving at its largest size, so more photos would help all three.",
                 "kn": "ಪ್ರತಿ ಭಾಗವೂ ತನ್ನ ಅತಿ ದೊಡ್ಡ ಗಾತ್ರದಲ್ಲೂ ಸುಧಾರಿಸುತ್ತಿದೆ, ಆದ್ದರಿಂದ ಹೆಚ್ಚು ಫೋಟೋಗಳು ಮೂರಕ್ಕೂ ಸಹಾಯ ಮಾಡುತ್ತವೆ.",
                 "hi": "हर अंग अपने सबसे बड़े आकार पर भी सुधर रहा है, इसलिए ज़्यादा फ़ोटो तीनों की मदद करेंगी।"},
    "clusters_title": {"en": "K-means pallor groups", "kn": "K-means ಬಿಳಿಚುವಿಕೆ ಗುಂಪುಗಳು", "hi": "K-means पीलापन समूह"},
    "clusters_lede": {"en": "K-means on {k} scaled colour features of the {n} eye photos, without labels. Then we check "
                            "whether the groups line up with anaemia.",
                      "kn": "{n} ಕಣ್ಣಿನ ಫೋಟೋಗಳ {k} ಪ್ರಮಾಣೀಕೃತ ಬಣ್ಣದ ಲಕ್ಷಣಗಳ ಮೇಲೆ ಲೇಬಲ್ ಇಲ್ಲದೆ K-means. ನಂತರ ಗುಂಪುಗಳು "
                            "ರಕ್ತಹೀನತೆಯೊಂದಿಗೆ ಹೊಂದುತ್ತವೆಯೇ ಎಂದು ಪರಿಶೀಲಿಸುತ್ತೇವೆ.",
                      "hi": "{n} आँख की फ़ोटो की {k} मानकीकृत रंग विशेषताओं पर बिना लेबल K-means। फिर हम देखते हैं कि समूह "
                            "एनीमिया से मेल खाते हैं या नहीं।"},
    "t_elbow": {"en": "The error curve bends at k = {k}, so we keep {k} groups.",
                "kn": "ದೋಷ ವಕ್ರರೇಖೆ k = {k} ನಲ್ಲಿ ಬಾಗುತ್ತದೆ, ಆದ್ದರಿಂದ {k} ಗುಂಪುಗಳನ್ನು ಇಡುತ್ತೇವೆ.",
                "hi": "त्रुटि वक्र k = {k} पर मुड़ता है, इसलिए हम {k} समूह रखते हैं।"},
    "t_sil": {"en": "Silhouette peaks at k = {k} and stays low: the colours form a continuum, not clean islands.",
              "kn": "ಸಿಲೂಯೆಟ್ k = {k} ನಲ್ಲಿ ಗರಿಷ್ಠ, ನಂತರ ಕಡಿಮೆ: ಬಣ್ಣಗಳು ನಿರಂತರ ಸರಣಿ, ಸ್ಪಷ್ಟ ದ್ವೀಪಗಳಲ್ಲ.",
              "hi": "सिल्हूट k = {k} पर सबसे ऊँचा और फिर कम: रंग एक निरंतर क्रम हैं, अलग-अलग द्वीप नहीं।"},
    "t_cl_differ": {"en": "Mean Hb does differ between the groups ({p}): {hi_pct} anaemic in the {hi_name} group vs {lo_pct} "
                          "in the {lo_name} group.",
                    "kn": "ಗುಂಪುಗಳ ನಡುವೆ ಸರಾಸರಿ Hb ಬೇರೆಯಾಗಿದೆ ({p}): {hi_name} ಗುಂಪಿನಲ್ಲಿ {hi_pct} ರಕ್ತಹೀನರು, {lo_name} "
                          "ಗುಂಪಿನಲ್ಲಿ {lo_pct}.",
                    "hi": "समूहों के बीच औसत Hb अलग है ({p}): {hi_name} समूह में {hi_pct} को एनीमिया, {lo_name} समूह में "
                          "{lo_pct}।"},
    "t_cl_nodiffer": {"en": "Mean Hb does not differ clearly between the groups ({p}).",
                      "kn": "ಗುಂಪುಗಳ ನಡುವೆ ಸರಾಸರಿ Hb ಸ್ಪಷ್ಟವಾಗಿ ಬೇರೆಯಾಗಿಲ್ಲ ({p}).",
                      "hi": "समूहों के बीच औसत Hb साफ़ तौर पर अलग नहीं है ({p})।"},
    "t_cl_purity_same": {"en": " But no group is clean: severity purity {pur} equals the majority baseline {base}, so "
                               "clusters alone cannot screen.",
                         "kn": " ಆದರೆ ಯಾವ ಗುಂಪೂ ಶುದ್ಧವಲ್ಲ: ತೀವ್ರತೆಯ ಶುದ್ಧತೆ {pur} ಬಹುಮತದ ಆಧಾರ {base} ಗೆ ಸಮ, ಆದ್ದರಿಂದ "
                               "ಗುಂಪುಗಳು ಮಾತ್ರ ತಪಾಸಣೆ ಮಾಡಲಾರವು.",
                         "hi": " पर कोई समूह साफ़ नहीं: गंभीरता शुद्धता {pur} बहुमत आधार {base} के बराबर है, इसलिए केवल "
                               "समूह जाँच नहीं कर सकते।"},
    "t_cl_purity": {"en": " Severity purity {pur} vs majority baseline {base}.",
                    "kn": " ತೀವ್ರತೆಯ ಶುದ್ಧತೆ {pur}, ಬಹುಮತದ ಆಧಾರ {base}.",
                    "hi": " गंभीरता शुद्धता {pur}, बहुमत आधार {base}।"},
    "t_cl_sites": {"en": "With folder labels, the same 5-group K-means beats the majority baseline on {beat}, and only by "
                         "a few points.",
                   "kn": "ಫೋಲ್ಡರ್ ಲೇಬಲ್‌ಗಳೊಂದಿಗೆ, ಅದೇ 5-ಗುಂಪಿನ K-means {beat} ನಲ್ಲಿ ಬಹುಮತದ ಆಧಾರವನ್ನು ಮೀರುತ್ತದೆ, ಅದೂ "
                         "ಕೆಲವೇ ಅಂಕಗಳಿಂದ.",
                   "hi": "फ़ोल्डर लेबल के साथ वही 5-समूह K-means {beat} पर बहुमत आधार से आगे है, और वह भी कुछ ही अंकों से।"},
    "t_cl_sites_but": {"en": "{beat} but not on {miss}", "kn": "{beat}, ಆದರೆ {miss} ನಲ್ಲಿ ಅಲ್ಲ",
                       "hi": "{beat} पर, पर {miss} पर नहीं"},
    "t_cl_sites_none": {"en": "neither site", "kn": "ಯಾವ ಭಾಗದಲ್ಲೂ ಅಲ್ಲ", "hi": "किसी अंग पर नहीं"},
    "search_title": {"en": "Cheapest screening protocol", "kn": "ಅತ್ಯಂತ ಕಡಿಮೆ ವೆಚ್ಚದ ತಪಾಸಣಾ ವಿಧಾನ",
                     "hi": "सबसे सस्ता जाँच तरीका"},
    "search_lede": {"en": "Search over site plus up to 3 colour features. Score = specificity at 80% sensitivity, minus a "
                          "cost per photo and per feature.",
                    "kn": "ಭಾಗ ಮತ್ತು 3ರವರೆಗೆ ಬಣ್ಣದ ಲಕ್ಷಣಗಳ ಮೇಲೆ ಶೋಧನೆ. ಅಂಕ = 80% ಸಂವೇದನಶೀಲತೆಯಲ್ಲಿ ನಿರ್ದಿಷ್ಟತೆ, ಪ್ರತಿ ಫೋಟೋ ಮತ್ತು "
                          "ಲಕ್ಷಣದ ವೆಚ್ಚ ಕಳೆದು.",
                    "hi": "अंग और 3 तक रंग विशेषताओं पर खोज। स्कोर = 80% संवेदनशीलता पर विशिष्टता, हर फ़ोटो और विशेषता की "
                          "लागत घटाकर।"},
    "t_search_table": {"en": "Exhaustive BFS checks {n} protocols to find the best ({opt}); {algo} finds the same protocol "
                             "in a run of {evals} evaluations.",
                       "kn": "ಸಂಪೂರ್ಣ BFS ಅತ್ಯುತ್ತಮವನ್ನು ({opt}) ಕಂಡುಹಿಡಿಯಲು {n} ವಿಧಾನಗಳನ್ನು ಪರಿಶೀಲಿಸುತ್ತದೆ; {algo} ಅದೇ ವಿಧಾನವನ್ನು "
                             "{evals} ಮೌಲ್ಯಮಾಪನಗಳ ಓಟದಲ್ಲಿ ಕಂಡುಹಿಡಿಯುತ್ತದೆ.",
                       "hi": "पूरा BFS सबसे अच्छा ({opt}) खोजने के लिए {n} तरीके जाँचता है; {algo} वही तरीका {evals} मूल्यांकनों "
                             "की एक दौड़ में पाता है।"},
    "t_conv": {"en": "Local beam reaches the exhaustive optimum after {n} evaluations, {pct} of BFS's {bfs}; hill climbing, "
                     "annealing and the genetic algorithm stop slightly below it.",
               "kn": "ಲೋಕಲ್ ಬೀಮ್ {n} ಮೌಲ್ಯಮಾಪನಗಳ ನಂತರ ಸಂಪೂರ್ಣ ಶೋಧನೆಯ ಅತ್ಯುತ್ತಮವನ್ನು ತಲುಪುತ್ತದೆ, BFS ನ {bfs} ರಲ್ಲಿ {pct}; "
                     "ಹಿಲ್ ಕ್ಲೈಂಬಿಂಗ್, ಅನೀಲಿಂಗ್ ಮತ್ತು ಜೆನೆಟಿಕ್ ಅಲ್ಗಾರಿದಮ್ ಸ್ವಲ್ಪ ಕೆಳಗೆ ನಿಲ್ಲುತ್ತವೆ.",
               "hi": "लोकल बीम {n} मूल्यांकनों के बाद पूरी खोज के सबसे अच्छे तक पहुँचता है, BFS के {bfs} का {pct}; हिल "
                     "क्लाइंबिंग, एनीलिंग और जेनेटिक एल्गोरिदम थोड़ा नीचे रुकते हैं।"},
    "t_conv_none": {"en": "Local beam does not reach the exhaustive optimum on this seed; the other local searches stop "
                          "slightly below it.",
                    "kn": "ಈ ಬೀಜದಲ್ಲಿ ಲೋಕಲ್ ಬೀಮ್ ಸಂಪೂರ್ಣ ಅತ್ಯುತ್ತಮವನ್ನು ತಲುಪುವುದಿಲ್ಲ; ಇತರ ಸ್ಥಳೀಯ ಶೋಧನೆಗಳು ಸ್ವಲ್ಪ ಕೆಳಗೆ "
                          "ನಿಲ್ಲುತ್ತವೆ.",
                    "hi": "इस बीज पर लोकल बीम पूरी खोज के सबसे अच्छे तक नहीं पहुँचता; बाकी स्थानीय खोजें थोड़ा नीचे रुकती हैं।"},
    "t_nested": {"en": "Rerun inside each training fold and scored on held-out children, the winning protocol drops from "
                       "{inner} to {outer}: picking the best of thousands flatters the score.",
                 "kn": "ಪ್ರತಿ ತರಬೇತಿ ಭಾಗದೊಳಗೆ ಮತ್ತೆ ನಡೆಸಿ ಪ್ರತ್ಯೇಕ ಮಕ್ಕಳ ಮೇಲೆ ಅಂಕ ನೀಡಿದಾಗ, ಗೆದ್ದ ವಿಧಾನ {inner} ರಿಂದ {outer} ಗೆ "
                       "ಇಳಿಯುತ್ತದೆ: ಸಾವಿರಾರಲ್ಲಿ ಅತ್ಯುತ್ತಮವನ್ನು ಆರಿಸುವುದು ಅಂಕವನ್ನು ಉಬ್ಬಿಸುತ್ತದೆ.",
                 "hi": "हर ट्रेनिंग हिस्से के अंदर दोबारा चलाकर अलग रखे बच्चों पर आँकने से विजेता तरीका {inner} से {outer} पर आ "
                       "जाता है: हज़ारों में से सबसे अच्छा चुनना स्कोर को बढ़ा-चढ़ा देता है।"},

    # ---------------------------------------------------------------- about page
    "about_title": {"en": "About", "kn": "ಕುರಿತು", "hi": "परिचय"},
    "about_lede": {"en": "Netra-Hb: needle-free anaemia screening from smartphone photos with classical machine learning. "
                         "RVCE IS353IA (AIML) Lab Part-B.",
                   "kn": "Netra-Hb: ಸಾಂಪ್ರದಾಯಿಕ ಯಂತ್ರ ಕಲಿಕೆಯೊಂದಿಗೆ ಸ್ಮಾರ್ಟ್‌ಫೋನ್ ಫೋಟೋಗಳಿಂದ ಸೂಜಿ ಇಲ್ಲದ ರಕ್ತಹೀನತೆ ತಪಾಸಣೆ. "
                         "RVCE IS353IA (AIML) ಲ್ಯಾಬ್ ಭಾಗ-B.",
                   "hi": "Netra-Hb: पारंपरिक मशीन लर्निंग से स्मार्टफ़ोन फ़ोटो द्वारा बिना सुई एनीमिया जाँच। RVCE IS353IA "
                         "(AIML) लैब भाग-B।"},
    "pipeline_title": {"en": "How a photo becomes a result", "kn": "ಫೋಟೋ ಫಲಿತಾಂಶವಾಗುವ ಬಗೆ",
                       "hi": "फ़ोटो नतीजा कैसे बनती है"},
    "t_pipeline": {"en": "Six steps, all classical: the photo is masked to tissue, reduced to colour numbers, scored by a "
                         "soft vote of three models and compared with a threshold chosen for 80% sensitivity.",
                   "kn": "ಆರು ಹಂತಗಳು, ಎಲ್ಲವೂ ಸಾಂಪ್ರದಾಯಿಕ: ಫೋಟೋವನ್ನು ಅಂಗಾಂಶಕ್ಕೆ ಮರೆಮಾಡಿ, ಬಣ್ಣದ ಸಂಖ್ಯೆಗಳಾಗಿ ಮಾಡಿ, ಮೂರು ಮಾದರಿಗಳ "
                         "ಮೃದು ಮತದಿಂದ ಅಂಕ ನೀಡಿ, 80% ಸಂವೇದನಶೀಲತೆಗೆ ಆರಿಸಿದ ಮಿತಿಯೊಂದಿಗೆ ಹೋಲಿಸಲಾಗುತ್ತದೆ.",
                   "hi": "छह कदम, सब पारंपरिक: फ़ोटो को ऊतक तक सीमित कर, रंग संख्याओं में बदलकर, तीन मॉडलों के सॉफ़्ट वोट से "
                         "आँककर, 80% संवेदनशीलता के लिए चुनी गई सीमा से तुलना की जाती है।"},
    "units_title": {"en": "Syllabus map", "kn": "ಪಠ್ಯಕ್ರಮ ನಕ್ಷೆ", "hi": "पाठ्यक्रम मानचित्र"},
    "t_units": {"en": "All five IS353IA units are used, and only syllabus algorithms: no deep learning.",
                "kn": "IS353IA ನ ಎಲ್ಲಾ ಐದು ಘಟಕಗಳನ್ನು ಬಳಸಲಾಗಿದೆ, ಪಠ್ಯಕ್ರಮದ ಅಲ್ಗಾರಿದಮ್‌ಗಳು ಮಾತ್ರ: ಡೀಪ್ ಲರ್ನಿಂಗ್ ಇಲ್ಲ.",
                "hi": "IS353IA की पाँचों इकाइयाँ इस्तेमाल हुई हैं, और केवल पाठ्यक्रम के एल्गोरिदम: कोई डीप लर्निंग नहीं।"},

    # ---------------------------------------------------------------- words used inside takeaways
    "feat_lab_a_med": {"en": "redness (a*)", "kn": "ಕೆಂಪು (a*)", "hi": "लाली (a*)"},
    "feat_lab_L_med": {"en": "lightness (L*)", "kn": "ಬೆಳಕು (L*)", "hi": "हल्कापन (L*)"},
    "feat_erythema_index_med": {"en": "erythema index", "kn": "ಎರಿಥೀಮಾ ಸೂಚ್ಯಂಕ", "hi": "एरिथीमा सूचकांक"},
    "feat_chrom_r_med": {"en": "red share", "kn": "ಕೆಂಪಿನ ಪಾಲು", "hi": "लाल का हिस्सा"},
    "feat_a_over_L_med": {"en": "redness per lightness (a*/L*)", "kn": "ಬೆಳಕಿಗೆ ಕೆಂಪು (a*/L*)",
                          "hi": "हल्केपन के अनुपात में लाली (a*/L*)"},
    "feat_R_med": {"en": "red channel", "kn": "ಕೆಂಪು ಚಾನೆಲ್", "hi": "लाल चैनल"},
    "feat_hsv_s_med": {"en": "saturation", "kn": "ಸ್ಯಾಚುರೇಶನ್", "hi": "संतृप्ति"},
    "feat_lab_b_med": {"en": "yellowness (b*)", "kn": "ಹಳದಿ (b*)", "hi": "पीलापन (b*)"},
    "feat_chrom_g_med": {"en": "green share", "kn": "ಹಸಿರಿನ ಪಾಲು", "hi": "हरे का हिस्सा"},
    "feat_hsv_h_med": {"en": "hue", "kn": "ವರ್ಣ", "hi": "रंगत"},
    "cl_pink": {"en": "pink", "kn": "ಗುಲಾಬಿ", "hi": "गुलाबी"},
    "cl_pale": {"en": "pale", "kn": "ಬಿಳಿಚಿದ", "hi": "फीका"},
    "cl_very_pale": {"en": "very pale", "kn": "ತುಂಬಾ ಬಿಳಿಚಿದ", "hi": "बहुत फीका"},
    "cl_red": {"en": "red", "kn": "ಕೆಂಪು", "hi": "लाल"},
    "cl_intermediate": {"en": "intermediate", "kn": "ಮಧ್ಯಮ", "hi": "बीच का"},
    "and": {"en": " and ", "kn": " ಮತ್ತು ", "hi": " और "},

    # ---------------------------------------------------------------- cleaner screen (P10f)
    "gallery_title": {"en": "Try a sample patient", "kn": "ಮಾದರಿ ರೋಗಿಯನ್ನು ಪ್ರಯತ್ನಿಸಿ", "hi": "नमूना मरीज़ आज़माएँ"},
    "gallery_lede": {"en": "Pick a child to see a full screening, from photo to result. These are real photos from the "
                           "training data.",
                     "kn": "ಫೋಟೋದಿಂದ ಫಲಿತಾಂಶದವರೆಗೆ ಪೂರ್ಣ ತಪಾಸಣೆ ನೋಡಲು ಒಂದು ಮಗುವನ್ನು ಆರಿಸಿ. ಇವು ತರಬೇತಿ ದತ್ತಾಂಶದ ನಿಜವಾದ ಫೋಟೋಗಳು.",
                     "hi": "फ़ोटो से नतीजे तक पूरी जाँच देखने के लिए एक बच्चा चुनें। ये ट्रेनिंग डेटा की असली फ़ोटो हैं।"},
    "own_title": {"en": "Or screen with your own photo", "kn": "ಅಥವಾ ನಿಮ್ಮ ಸ್ವಂತ ಫೋಟೋದೊಂದಿಗೆ ತಪಾಸಣೆ ಮಾಡಿ",
                  "hi": "या अपनी फ़ोटो से जाँच करें"},
    "own_lede": {"en": "Choose the age band and where to photograph, then take or upload a photo.",
                 "kn": "ವಯಸ್ಸಿನ ಗುಂಪು ಮತ್ತು ಎಲ್ಲಿಯ ಫೋಟೋ ಎಂದು ಆರಿಸಿ, ನಂತರ ಫೋಟೋ ತೆಗೆಯಿರಿ ಅಥವಾ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.",
                 "hi": "आयु वर्ग और किसकी फ़ोटो लेनी है चुनें, फिर फ़ोटो लें या अपलोड करें।"},
    "rank_eye": {"en": "Best first choice: works across skin tones.", "kn": "ಮೊದಲ ಆಯ್ಕೆ: ಎಲ್ಲಾ ಚರ್ಮದ ಬಣ್ಣಗಳಿಗೂ ಸೂಕ್ತ.",
                 "hi": "पहली पसंद: हर त्वचा के रंग पर काम करता है।"},
    "rank_nail": {"en": "Good second choice.", "kn": "ಉತ್ತಮ ಎರಡನೇ ಆಯ್ಕೆ.", "hi": "अच्छी दूसरी पसंद।"},
    "rank_palm": {"en": "Use when the eyelid and nails are not possible.",
                  "kn": "ಕಣ್ಣಿನ ರೆಪ್ಪೆ ಮತ್ತು ಉಗುರು ಸಾಧ್ಯವಿಲ್ಲದಾಗ ಬಳಸಿ.",
                  "hi": "जब पलक और नाखून संभव न हों तब इस्तेमाल करें।"},
    "recommended": {"en": "Recommended", "kn": "ಶಿಫಾರಸು", "hi": "सुझाया गया"},
    "crop_eye": {"en": "Drag a tight box over only the pink inner eyelid. Only the oval inside the box is measured.",
                 "kn": "ಗುಲಾಬಿ ಒಳರೆಪ್ಪೆಯ ಮೇಲೆ ಮಾತ್ರ ಬಿಗಿಯಾದ ಚೌಕ ಎಳೆಯಿರಿ. ಚೌಕದೊಳಗಿನ ಅಂಡಾಕಾರ ಮಾತ್ರ ಅಳೆಯಲಾಗುತ್ತದೆ.",
                 "hi": "केवल गुलाबी भीतरी पलक पर एक कसा हुआ बॉक्स खींचें। बॉक्स के अंदर का अंडाकार ही मापा जाता है।"},
    "crop_nail": {"en": "Drag a tight box over only one nail bed. Only the oval inside the box is measured.",
                  "kn": "ಒಂದು ಉಗುರಿನ ತಳದ ಮೇಲೆ ಮಾತ್ರ ಬಿಗಿಯಾದ ಚೌಕ ಎಳೆಯಿರಿ. ಚೌಕದೊಳಗಿನ ಅಂಡಾಕಾರ ಮಾತ್ರ ಅಳೆಯಲಾಗುತ್ತದೆ.",
                  "hi": "केवल एक नाखून पर कसा हुआ बॉक्स खींचें। बॉक्स के अंदर का अंडाकार ही मापा जाता है।"},
    "crop_palm": {"en": "Drag a tight box over only the centre of the palm. Only the oval inside the box is measured.",
                  "kn": "ಅಂಗೈಯ ಮಧ್ಯಭಾಗದ ಮೇಲೆ ಮಾತ್ರ ಬಿಗಿಯಾದ ಚೌಕ ಎಳೆಯಿರಿ. ಚೌಕದೊಳಗಿನ ಅಂಡಾಕಾರ ಮಾತ್ರ ಅಳೆಯಲಾಗುತ್ತದೆ.",
                  "hi": "केवल हथेली के बीच वाले हिस्से पर कसा हुआ बॉक्स खींचें। बॉक्स के अंदर का अंडाकार ही मापा जाता है।"},
    "crop_done": {"en": "Measured area marked. Drag again to change it.", "kn": "ಅಳೆಯುವ ಭಾಗ ಗುರುತಿಸಲಾಗಿದೆ. ಬದಲಿಸಲು ಮತ್ತೆ ಎಳೆಯಿರಿ.",
                  "hi": "मापा जाने वाला हिस्सा चिह्नित है। बदलने के लिए फिर से खींचें।"},
    "measured_title": {"en": "Measured area", "kn": "ಅಳೆಯುವ ಭಾಗ", "hi": "मापा जाने वाला हिस्सा"},
    "retake_eye": {"en": "Please retake: daylight, no eye makeup, show only the inner eyelid.",
                   "kn": "ದಯವಿಟ್ಟು ಮತ್ತೆ ತೆಗೆಯಿರಿ: ಹಗಲು ಬೆಳಕು, ಕಣ್ಣಿನ ಮೇಕಪ್ ಬೇಡ, ಒಳರೆಪ್ಪೆ ಮಾತ್ರ ತೋರಿಸಿ.",
                   "hi": "कृपया दोबारा लें: दिन की रोशनी, आँखों का मेकअप नहीं, केवल भीतरी पलक दिखाएँ।"},
    "retake_nail": {"en": "Please retake: daylight, no nail polish, show only the nail bed.",
                    "kn": "ದಯವಿಟ್ಟು ಮತ್ತೆ ತೆಗೆಯಿರಿ: ಹಗಲು ಬೆಳಕು, ನೇಲ್ ಪಾಲಿಶ್ ಬೇಡ, ಉಗುರಿನ ತಳ ಮಾತ್ರ ತೋರಿಸಿ.",
                    "hi": "कृपया दोबारा लें: दिन की रोशनी, नेल पॉलिश नहीं, केवल नाखून दिखाएँ।"},
    "retake_palm": {"en": "Please retake: daylight, no flash, show only the centre of the palm.",
                    "kn": "ದಯವಿಟ್ಟು ಮತ್ತೆ ತೆಗೆಯಿರಿ: ಹಗಲು ಬೆಳಕು, ಫ್ಲ್ಯಾಶ್ ಬೇಡ, ಅಂಗೈಯ ಮಧ್ಯಭಾಗ ಮಾತ್ರ ತೋರಿಸಿ.",
                    "hi": "कृपया दोबारा लें: दिन की रोशनी, फ़्लैश नहीं, केवल हथेली का बीच वाला हिस्सा दिखाएँ।"},
    "photo_ok": {"en": "The photo looks good.", "kn": "ಫೋಟೋ ಚೆನ್ನಾಗಿದೆ.", "hi": "फ़ोटो ठीक है।"},
    "result_footer": {"en": "Screening aid only. Confirm with a blood Hb test.",
                      "kn": "ಕೇವಲ ತಪಾಸಣಾ ಸಹಾಯಕ. ರಕ್ತದ Hb ಪರೀಕ್ಷೆಯಿಂದ ಖಚಿತಪಡಿಸಿ.",
                      "hi": "केवल जाँच सहायक। खून की Hb जाँच से पुष्टि करें।"},
    "home_results_link": {"en": "How well does it work? See the results", "kn": "ಇದು ಎಷ್ಟು ಚೆನ್ನಾಗಿ ಕೆಲಸ ಮಾಡುತ್ತದೆ? ಫಲಿತಾಂಶಗಳನ್ನು ನೋಡಿ",
                          "hi": "यह कितना अच्छा काम करता है? नतीजे देखें"},
    "home_results_lede": {"en": "The Results page compares every model on held-out children, with honest intervals.",
                          "kn": "ಫಲಿತಾಂಶಗಳ ಪುಟ ಪ್ರತಿ ಮಾದರಿಯನ್ನು ಪ್ರತ್ಯೇಕ ಮಕ್ಕಳ ಮೇಲೆ ಪ್ರಾಮಾಣಿಕ ವ್ಯಾಪ್ತಿಗಳೊಂದಿಗೆ ಹೋಲಿಸುತ್ತದೆ.",
                          "hi": "नतीजे पेज हर मॉडल की तुलना अलग रखे गए बच्चों पर ईमानदार सीमाओं के साथ करता है।"},
    "screen_lede_samples": {"en": "Start with a sample patient, or screen a child with your own photo.",
                            "kn": "ಮಾದರಿ ರೋಗಿಯಿಂದ ಆರಂಭಿಸಿ, ಅಥವಾ ನಿಮ್ಮ ಸ್ವಂತ ಫೋಟೋದೊಂದಿಗೆ ಮಗುವಿನ ತಪಾಸಣೆ ಮಾಡಿ.",
                            "hi": "नमूना मरीज़ से शुरू करें, या अपनी फ़ोटो से बच्चे की जाँच करें।"},

    # ---------------------------------------------------------------- story (P10g)
    "why_title": {"en": "Why Netra-Hb", "kn": "ಏಕೆ Netra-Hb", "hi": "Netra-Hb क्यों"},
    "why1_title": {"en": "Health workers screen, not doctors", "kn": "ತಪಾಸಣೆ ಮಾಡುವವರು ಆರೋಗ್ಯ ಕಾರ್ಯಕರ್ತರು, ವೈದ್ಯರಲ್ಲ",
                   "hi": "जाँच स्वास्थ्य कार्यकर्ता करते हैं, डॉक्टर नहीं"},
    "why1_text": {"en": "In villages, most screening is done by community health workers on home visits, often far from a "
                        "doctor or a lab.",
                  "kn": "ಹಳ್ಳಿಗಳಲ್ಲಿ ಹೆಚ್ಚಿನ ತಪಾಸಣೆಯನ್ನು ಮನೆ ಭೇಟಿಗಳಲ್ಲಿ ಸಮುದಾಯ ಆರೋಗ್ಯ ಕಾರ್ಯಕರ್ತರು ಮಾಡುತ್ತಾರೆ, ಹೆಚ್ಚಾಗಿ ವೈದ್ಯರು "
                        "ಅಥವಾ ಪ್ರಯೋಗಾಲಯದಿಂದ ದೂರ.",
                  "hi": "गाँवों में ज़्यादातर जाँच समुदाय स्वास्थ्य कार्यकर्ता घर-घर जाकर करते हैं, अक्सर डॉक्टर या लैब से दूर।"},
    "why2_title": {"en": "The same answer every time", "kn": "ಪ್ರತಿ ಬಾರಿಯೂ ಒಂದೇ ಉತ್ತರ", "hi": "हर बार एक ही जवाब"},
    "why2_text": {"en": "A visual pallor check is subjective and varies between examiners. Netra-Hb measures colour, so the "
                        "same photo always gives the same result.",
                  "kn": "ಕಣ್ಣಿನಿಂದ ಬಿಳಿಚುವಿಕೆ ನೋಡುವುದು ವ್ಯಕ್ತಿನಿಷ್ಠ ಮತ್ತು ಪರೀಕ್ಷಕರ ನಡುವೆ ಬದಲಾಗುತ್ತದೆ. Netra-Hb ಬಣ್ಣವನ್ನು ಅಳೆಯುತ್ತದೆ, "
                        "ಆದ್ದರಿಂದ ಅದೇ ಫೋಟೋ ಯಾವಾಗಲೂ ಅದೇ ಫಲಿತಾಂಶ ನೀಡುತ್ತದೆ.",
                  "hi": "आँख से पीलापन देखना व्यक्तिपरक है और जाँचने वालों में बदलता है। Netra-Hb रंग मापता है, इसलिए वही फ़ोटो "
                        "हमेशा वही नतीजा देती है।"},
    "why3_title": {"en": "Spend scarce test strips well", "kn": "ಕಡಿಮೆ ಪರೀಕ್ಷಾ ಪಟ್ಟಿಗಳನ್ನು ಸರಿಯಾಗಿ ಬಳಸಿ",
                   "hi": "कम टेस्ट स्ट्रिप का सही इस्तेमाल"},
    "why3_text": {"en": "When finger-prick strips run short, it helps decide which children should get a blood test first.",
                  "kn": "ಬೆರಳು ಚುಚ್ಚುವ ಪಟ್ಟಿಗಳು ಕಡಿಮೆಯಾದಾಗ, ಯಾವ ಮಕ್ಕಳಿಗೆ ಮೊದಲು ರಕ್ತ ಪರೀಕ್ಷೆ ಬೇಕು ಎಂದು ನಿರ್ಧರಿಸಲು ಇದು "
                        "ಸಹಾಯ ಮಾಡುತ್ತದೆ.",
                  "hi": "जब उँगली की जाँच वाली स्ट्रिप कम हों, तो यह तय करने में मदद करता है कि किन बच्चों की खून की जाँच पहले "
                        "हो।"},
    "found_title": {"en": "What we found", "kn": "ನಾವು ಕಂಡುಕೊಂಡದ್ದು", "hi": "हमने क्या पाया"},
    "f_sites_title": {"en": "Eye, palm or nail?", "kn": "ಕಣ್ಣು, ಅಂಗೈ ಅಥವಾ ಉಗುರು?", "hi": "आँख, हथेली या नाखून?"},
    "f_sites": {"en": "At the same 220 photos each, the eye scores {eye}, palm {palm} and nail {nail} (ROC-AUC). With more "
                      "data, palm and nail improve.",
                "kn": "ಪ್ರತಿಯೊಂದಕ್ಕೂ ಅದೇ 220 ಫೋಟೋಗಳಲ್ಲಿ ಕಣ್ಣು {eye}, ಅಂಗೈ {palm}, ಉಗುರು {nail} (ROC-AUC). ಹೆಚ್ಚು ದತ್ತಾಂಶದೊಂದಿಗೆ "
                      "ಅಂಗೈ ಮತ್ತು ಉಗುರು ಸುಧಾರಿಸುತ್ತವೆ.",
                "hi": "हर एक की उन्हीं 220 फ़ोटो पर आँख {eye}, हथेली {palm} और नाखून {nail} (ROC-AUC)। ज़्यादा डेटा से हथेली "
                      "और नाखून सुधरते हैं।"},
    "f_honest_title": {"en": "Honest evaluation lowers scores", "kn": "ಪ್ರಾಮಾಣಿಕ ಮೌಲ್ಯಮಾಪನ ಅಂಕಗಳನ್ನು ಇಳಿಸುತ್ತದೆ",
                       "hi": "ईमानदार जाँच स्कोर घटाती है"},
    "f_honest": {"en": "Dropping blurred, upscaled and glare-heavy photos takes the best eye score from {q_before} to "
                       "{q_after}; the protocol search falls from {s_before} to {s_after} on held-out children.",
                 "kn": "ಮಸುಕಾದ, ದೊಡ್ಡದಾಗಿಸಿದ ಮತ್ತು ಹೆಚ್ಚು ಹೊಳಪಿನ ಫೋಟೋಗಳನ್ನು ತೆಗೆದಾಗ ಅತ್ಯುತ್ತಮ ಕಣ್ಣಿನ ಅಂಕ {q_before} ರಿಂದ "
                       "{q_after} ಗೆ ಇಳಿಯುತ್ತದೆ; ಶೋಧನೆ ಪ್ರತ್ಯೇಕ ಮಕ್ಕಳ ಮೇಲೆ {s_before} ರಿಂದ {s_after} ಗೆ ಇಳಿಯುತ್ತದೆ.",
                 "hi": "धुंधली, बड़ी की गई और ज़्यादा चमक वाली फ़ोटो हटाने पर सबसे अच्छा आँख स्कोर {q_before} से {q_after} पर "
                       "आता है; खोज अलग रखे बच्चों पर {s_before} से {s_after} पर आती है।"},
    "f_safe_title": {"en": "Makeup and webcams fool colour models", "kn": "ಮೇಕಪ್ ಮತ್ತು ವೆಬ್‌ಕ್ಯಾಮ್ ಬಣ್ಣದ ಮಾದರಿಗಳನ್ನು ತಪ್ಪಿಸುತ್ತವೆ",
                     "hi": "मेकअप और वेबकैम रंग मॉडल को भटकाते हैं"},
    "f_safe": {"en": "So we added safeguards: dark makeup and lash pixels are removed (only {fp} of real eyelid pixels are "
                     "lost), and photos unlike the training set are marked low confidence.",
               "kn": "ಆದ್ದರಿಂದ ಸುರಕ್ಷತೆಗಳನ್ನು ಸೇರಿಸಿದೆವು: ಗಾಢ ಮೇಕಪ್ ಮತ್ತು ರೆಪ್ಪೆಗೂದಲಿನ ಪಿಕ್ಸೆಲ್‌ಗಳನ್ನು ತೆಗೆಯಲಾಗುತ್ತದೆ (ನಿಜವಾದ "
                     "ರೆಪ್ಪೆಯ {fp} ಪಿಕ್ಸೆಲ್‌ಗಳು ಮಾತ್ರ ಕಳೆದುಹೋಗುತ್ತವೆ), ಮತ್ತು ತರಬೇತಿ ಸೆಟ್‌ನಂತೆ ಇಲ್ಲದ ಫೋಟೋಗಳನ್ನು ಕಡಿಮೆ ವಿಶ್ವಾಸ "
                     "ಎಂದು ಗುರುತಿಸಲಾಗುತ್ತದೆ.",
               "hi": "इसलिए हमने सुरक्षा जोड़ी: गहरे मेकअप और पलकों के पिक्सेल हटाए जाते हैं (असली पलक के केवल {fp} पिक्सेल "
                     "खोते हैं), और ट्रेनिंग सेट से अलग दिखने वाली फ़ोटो को कम भरोसा चिह्नित किया जाता है।"},
    "f_search_title": {"en": "Cheapest screening protocol", "kn": "ಅತ್ಯಂತ ಕಡಿಮೆ ವೆಚ್ಚದ ತಪಾಸಣಾ ವಿಧಾನ",
                       "hi": "सबसे सस्ता जाँच तरीका"},
    "f_search": {"en": "BFS, IDDFS, hill climbing, simulated annealing, local beam, a genetic algorithm and A* searched site "
                       "and feature choices; local beam found the exhaustive optimum after {beam} of {bfs} evaluations.",
                 "kn": "BFS, IDDFS, ಹಿಲ್ ಕ್ಲೈಂಬಿಂಗ್, ಸಿಮ್ಯುಲೇಟೆಡ್ ಅನೀಲಿಂಗ್, ಲೋಕಲ್ ಬೀಮ್, ಜೆನೆಟಿಕ್ ಅಲ್ಗಾರಿದಮ್ ಮತ್ತು A* ಭಾಗ ಮತ್ತು "
                       "ಲಕ್ಷಣಗಳ ಆಯ್ಕೆಯನ್ನು ಶೋಧಿಸಿದವು; ಲೋಕಲ್ ಬೀಮ್ {bfs} ರಲ್ಲಿ {beam} ಮೌಲ್ಯಮಾಪನಗಳ ನಂತರ ಸಂಪೂರ್ಣ ಅತ್ಯುತ್ತಮವನ್ನು "
                       "ಕಂಡುಹಿಡಿಯಿತು.",
                 "hi": "BFS, IDDFS, हिल क्लाइंबिंग, सिम्युलेटेड एनीलिंग, लोकल बीम, जेनेटिक एल्गोरिदम और A* ने अंग और विशेषताओं "
                       "के विकल्प खोजे; लोकल बीम ने {bfs} में से {beam} मूल्यांकनों के बाद पूरी खोज का सबसे अच्छा पाया।"},
    "limit_skin": {"en": "Not yet validated across skin tones; the eyelid is the most skin-tone-robust site.",
                   "kn": "ಎಲ್ಲಾ ಚರ್ಮದ ಬಣ್ಣಗಳ ಮೇಲೆ ಇನ್ನೂ ಪರಿಶೀಲಿಸಲಾಗಿಲ್ಲ; ಕಣ್ಣಿನ ರೆಪ್ಪೆ ಚರ್ಮದ ಬಣ್ಣಕ್ಕೆ ಅತ್ಯಂತ ಸ್ಥಿರವಾದ ಭಾಗ.",
                   "hi": "अभी हर त्वचा के रंग पर नहीं जाँचा गया; पलक त्वचा के रंग से सबसे कम प्रभावित होने वाला अंग है।"},
    "future_title": {"en": "Future work", "kn": "ಮುಂದಿನ ಕೆಲಸ", "hi": "आगे का काम"},
}
