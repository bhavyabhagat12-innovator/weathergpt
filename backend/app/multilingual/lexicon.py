"""
Multilingual Lexicon & Glossary for Indian Meteorological & Agricultural Advisories.
Covers English, Hindi (हिन्दी), Marathi (मराठी), Tamil (தமிழ்), and Telugu (తెలుగు).
"""

from typing import Dict

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "हिन्दी (Hindi)",
    "mr": "मराठी (Marathi)",
    "ta": "தமிழ் (Tamil)",
    "te": "తెలుగు (Telugu)"
}

LEXICON: Dict[str, Dict[str, str]] = {
    # Headers
    "agro_advisory_title": {
        "en": "Agro-Meteorological Advisory",
        "hi": "कृषि मौसम परामर्श",
        "mr": "कृषी हवामान सल्लागार",
        "ta": "வேளாண் வானிலை ஆலோசனை",
        "te": "వ్యవసాయ వాతావరణ సలహా"
    },
    "aviation_advisory_title": {
        "en": "Aviation Meteorological Briefing",
        "hi": "विमानन मौसम ब्रीफिंग",
        "mr": "विमान वाहतूक हवामान माहिती",
        "ta": "விமானப் போக்குவரத்து வானிலை அறிக்கை",
        "te": "విమానయాన వాతావరణ బ్రీఫింగ్"
    },
    "marine_advisory_title": {
        "en": "Maritime & Port Advisory",
        "hi": "समुद्री एवं पत्तन मौसम चेतावनी",
        "mr": "सागरी आणि बंदर हवामान इशारा",
        "ta": "கடல் மற்றும் துறைமுக வானிலை எச்சரிக்கை",
        "te": "సముద్ర మరియు నౌకాశ్రయ వాతావరణ హెచ్చరిక"
    },
    "disaster_advisory_title": {
        "en": "Disaster Emergency Situation Report",
        "hi": "आपदा आपातकालीन स्थिति रिपोर्ट",
        "mr": "आपत्ती व्यवस्थापन परिस्थिती अहवाल",
        "ta": "பேரிடர் அவசர நிலை அறிக்கை",
        "te": "విపత్తు అత్యవసర పరిస్థితి నివేదిక"
    },
    "general_advisory_title": {
        "en": "Weather Intelligence Briefing",
        "hi": "मौसम सूचना सारांश",
        "mr": "हवामान माहिती सारांश",
        "ta": "வானிலை தகவல் சுருக்கம்",
        "te": "వాతావరణ సమాచార సారాంశం"
    },

    # Parameter labels
    "current_status": {
        "en": "Current Status",
        "hi": "वर्तमान स्थिति",
        "mr": "सद्यस्थिती",
        "ta": "தற்போதைய நிலை",
        "te": "ప్రస్తుత స్థితి"
    },
    "temp": {
        "en": "Temperature",
        "hi": "तापमान",
        "mr": "तापमान",
        "ta": "வெப்பநிலை",
        "te": "ఉష్ణోగ్రత"
    },
    "humidity": {
        "en": "Humidity",
        "hi": "आर्द्रता",
        "mr": "आर्द्रता",
        "ta": "ஈரப்பதம்",
        "te": "తేమ"
    },
    "condition": {
        "en": "Condition",
        "hi": "मौसम स्थिति",
        "mr": "हवामान स्थिती",
        "ta": "வானிலை நிலை",
        "te": "వాతావరణ పరిస్థితి"
    },
    "wind": {
        "en": "Wind Speed",
        "hi": "हवा की गति",
        "mr": "वाऱ्याचा वेग",
        "ta": "காற்றின் வேகம்",
        "te": "గాలి వేగం"
    },
    "rain_prob": {
        "en": "Rain Probability",
        "hi": "वर्षा की संभावना",
        "mr": "पावसाची शक्यता",
        "ta": "மழை வாய்ப்பு",
        "te": "వర్షపాతం సంభావ్యత"
    },
    "soil_moisture": {
        "en": "Soil Moisture (0-7cm)",
        "hi": "मृदा नमी (0-7 सेमी)",
        "mr": "जमिनीतील ओलावा (0-7 सेमी)",
        "ta": "மண் ஈரப்பதம் (0-7 செ.மீ)",
        "te": "నేలలో తేమ (0-7 సెం.మీ)"
    },

    # Advisory Directives
    "harvest_postpone": {
        "en": "⚠️ Postpone harvesting and sensitive field operations due to impending rainfall.",
        "hi": "⚠️ बारिश की संभावना को देखते हुए फसल कटाई और संवेदनशील कार्यों को स्थगित करें।",
        "mr": "⚠️ पावसाची शक्यता लक्षात घेता काढणी आणि संवेदनशील शेतीची कामे पुढे ढकला.",
        "ta": "⚠️ மழை வாய்ப்புள்ளதால் அறுவடை மற்றும் முக்கிய பணிகளை ஒத்திவைக்கவும்.",
        "te": "⚠️ వర్షం పడే అవకాశం ఉన్నందున పంట కోత పనులను వాయిదా వేయండి."
    },
    "spray_avoid": {
        "en": "🚫 DO NOT SPRAY pesticides/fertilizers: Rain or wind exceeds safe threshold.",
        "hi": "🚫 कीटनाशक या उर्वरक का छिड़काव न करें: बारिश अथवा हवा की गति सुरक्षित सीमा से अधिक है।",
        "mr": "🚫 कीटकनाशक अथवा खत फवारणी करू नका: पाऊस किंवा वाऱ्याचा वेग सुरक्षित मर्यादेपेक्षा जास्त आहे.",
        "ta": "🚫 பூச்சிக்கொல்லி தெளிக்க வேண்டாம்: மழை அல்லது காற்றின் வேகம் அதிகமாக உள்ளது.",
        "te": "🚫 పురుగుమందులను పిచికారీ చేయవద్దు: వర్షం లేదా గాలి వేగం ఎక్కువగా ఉంది."
    },
    "fishermen_warning": {
        "en": "🛑 DANGER: All fishing vessels must immediately return to port. Do not venture into deep sea.",
        "hi": "🛑 चेतावनी: सभी मछुआरे तुरंत तट पर लौट आएं। गहरे समुद्र में न जाएं।",
        "mr": "🛑 इशारा: सर्व मच्छीमारांनी तातडीने किनाऱ्यावर परत यावे. समुद्रात जाऊ नये.",
        "ta": "🛑 எச்சரிக்கை: மீனவர்கள் கடலுக்குச் செல்ல வேண்டாம். உடனடியாக கரை திரும்பவும்.",
        "te": "🛑 హెచ్చరిక: మత్స్యకారులు సముద్రంలోకి వెళ్లవద్దు. వెంటనే ఒడ్డుకు తిరిగి రండి."
    },
    "mandatory_directive": {
        "en": "Mandatory Directive",
        "hi": "अनिवार्य निर्देश",
        "mr": "सक्तीचे निर्देश",
        "ta": "கட்டாய உத்தரவு",
        "te": "తప్పనిసరి ఆదేశం"
    }
}
