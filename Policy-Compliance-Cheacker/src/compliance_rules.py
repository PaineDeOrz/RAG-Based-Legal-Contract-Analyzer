# compliance_rules.py
# Multilingual rental contract compliance rules (DE/EN)
# Output always in English, works with German/English contracts

COMPLIANCE_RULES = {
    "modes": {
        "rent": {
            "description": "Student dorm / residential rental agreements (Austria, DE/EN)",
            "rules": [
                {
                    "rule_id": "contract_duration",
                    "title": "Start/End Date + Extension",
                    "description": "Contract period and renewal options",
                    "keywords": [
                        # English
                        "start date", "end date", "duration", "term", "from", "to", "period",
                        # German
                        "von", "bis", "Vertragsdauer", "Vertragszeitraum", "Studienjahr",
                        # Other
                        "Verlängerung", "extension", "renewal", "automatisch"
                    ],
                    "prompt": """Multilingual legal analyst. Contract may be German/English. 
Analyze in source language. RESPOND ENTIRELY IN ENGLISH JSON: 
{"start_date": "DD.MM.YYYY or description", "end_date": "DD.MM.YYYY or description", 
 "extension": "none/manual/auto/description", "risk_level": "low/medium/high"}"""
                },
                {
                    "rule_id": "rent_amount",
                    "title": "Rent Price + Increases",
                    "description": "Monthly rent, due date, increases, included costs",
                    "keywords": [
                        # English
                        "rent", "monthly rent", "price", "fee", "payment", "due", "increase",
                        # German
                        "Benützungsentgelt", "Miete", "monatlich", "€", "Euro", "Erhöhung",
                        # Other
                        "SEPA", "Lastschrift", "invoice", "MwSt"
                    ],
                    "prompt": """Multilingual analyst. **ENGLISH JSON**: 
{"monthly_amount": "€XXX", "due_date": "Nth of month", "increases": "description/none", 
 "included": ["utilities", "internet", "etc"], "risk_level": "low/medium/high"}"""
                },
                {
                    "rule_id": "deposit_details",
                    "title": "Deposit Amount + Refund",
                    "description": "Security deposit terms and conditions",
                    "keywords": [
                        # English
                        "deposit", "security deposit", "refund", "retention",
                        # German
                        "Kaution", "Sicherheit", "Rückerstattung", "Einbehalt",
                        # Other
                        "Schäden", "damages", "reinigung", "cleaning"
                    ],
                    "prompt": """Multilingual analyst. **ENGLISH JSON**: 
{"amount": "€XXX", "refund_timeline": "days/months after move-out", 
 "withholding_conditions": ["damages", "cleaning", "unpaid rent"], "risk_level": "low/medium"}"""
                },
                {
                    "rule_id": "auxiliary_costs",
                    "title": "Extra Fees (Bills, Parking, Cleaning)",
                    "description": "Utilities, parking, cleaning, other mandatory fees",
                    "keywords": [
                        # English
                        "utilities", "bills", "parking", "cleaning fee", "laundry",
                        # German
                        "Betriebskosten", "Parkplatz", "Reinigung", "Waschküchen", 
                        "Heimvertretungsbeitrag", "Strom", "Wasser", "Heizung",
                        # Other
                        "Internet", "Müll", "Abwasser"
                    ],
                    "prompt": """Multilingual analyst. **ENGLISH list**: 
{"extra_fees": [{"name": "...", "amount": "€XXX/month/year", "mandatory": true/false}]}"""
                },
                {
                    "rule_id": "exact_location",
                    "title": "Room + Building Address",
                    "description": "Precise location and room specifications",
                    "keywords": [
                        # English
                        "address", "room", "apartment", "building", "single room",
                        # German
                        "Adresse", "Zimmer", "Einbettzimmer", "Wohnung", "Haus",
                        # Other
                        "Wehlistraße", "Handelskai"
                    ],
                    "prompt": """Multilingual analyst. **ENGLISH**: 
{"full_address": "street, number, postal code, city", 
 "room_type": "single/double/shared/studio", "building_name": "..."}"""
                },
                {
                    "rule_id": "landlord_details",
                    "title": "Landlord/Operator Information",
                    "description": "Legal operator and contact details",
                    "keywords": [
                        # English
                        "landlord", "owner", "operator", "lessor", "management",
                        # German
                        "Vermieter", "Heimbetreiber", "Wihast", "Akademikerhilfe",
                        # Other
                        "Vertragspartner", "Kontoinhaber"
                    ],
                    "prompt": """Multilingual analyst. **ENGLISH**: 
{"landlord_name": "...", "address": "...", "contact": "phone/email", 
 "sub_operator": "yes/no (name if yes)"}"""
                },
                {
                    "rule_id": "termination_tenant",
                    "title": "Tenant Termination Rights",
                    "description": "Notice period and penalties for tenant",
                    "keywords": [
                        # English
                        "termination", "notice period", "cancel", "end tenancy",
                        # German
                        "Kündigung", "Kündigungsfrist", "Rücktritt", "zweimonatig",
                        # Other
                        "Frist", "Monatsende"
                    ],
                    "prompt": """Multilingual analyst. **ENGLISH**: 
{"notice_period": "X months/weeks", "to_month_end": true/false, 
 "penalties": "description/none", "risk_level": "low/medium/high"}"""
                },
                {
                    "rule_id": "termination_landlord",
                    "title": "Landlord Termination Rights",
                    "description": "Conditions under which landlord can terminate",
                    "keywords": [
                        # English
                        "landlord termination", "eviction", "breach",
                        # German
                        "Kündigung Vermieter", "Zahlungsverzug", "StudHG §12",
                        # Other
                        "Missbrauch", "Schäden"
                    ],
                    "prompt": """Multilingual analyst. **ENGLISH**: 
{"grounds": ["payment delay", "misconduct", "statutory"], "notice_required": "yes/no"}"""
                },
                {
                    "rule_id": "house_rules",
                    "title": "Key House Rules",
                    "description": "Quiet hours, guests, subletting, pets, smoking",
                    "keywords": [
                        # English
                        "guests", "visitors", "quiet hours", "subletting", "pets", "smoking",
                        # German
                        "Besucher", "Nachtruhe", "Untervermietung", "Haustiere", "Rauchen"
                    ],
                    "prompt": """Multilingual analyst. **ENGLISH bullets**: 
- Guests: rules/duration
- Subletting: allowed/forbidden
- Quiet hours: times
- Pets/smoking: rules"""
                },
                {
                    "rule_id": "move_out_procedure",
                    "title": "Move-Out Process",
                    "description": "Key return, cleaning, inspection requirements",
                    "keywords": [
                        # English
                        "move out", "key return", "final cleaning", "inspection",
                        # German
                        "Räumung", "Schlüsselübergabe", "Endreinigung", "besenrein"
                    ],
                    "prompt": """Multilingual analyst. **ENGLISH**: 
{"deadline": "date/time", "cleaning_required": "broom clean/full", "inspection": "yes/no"}"""
                }
            ]
        }
    }
}


def get_rules(mode="rent"):
    """Return rules for specific contract mode"""
    if mode not in COMPLIANCE_RULES["modes"]:
        raise ValueError(f"Unknown mode '{mode}'. Available: {list(COMPLIANCE_RULES['modes'].keys())}")
    return COMPLIANCE_RULES["modes"][mode]["rules"]


def get_all_rules():
    """Return ALL rules across all modes (for backward compatibility)"""
    all_rules = {}
    for mode_rules in COMPLIANCE_RULES["modes"].values():
        for rule in mode_rules["rules"]:
            all_rules[rule["rule_id"]] = rule
    return all_rules


def get_rule(rule_id, mode="rent"):
    """Get specific rule by ID within mode"""
    rules = get_rules(mode)
    for rule in rules:
        if rule["rule_id"] == rule_id:
            return rule
    return None


def get_all_keywords(mode="rent"):
    """Get all keywords for a mode (for TF-IDF search)"""
    rules = get_rules(mode)
    keywords = []
    for rule in rules:
        keywords.extend(rule["keywords"])
    return list(set(keywords))


if __name__ == "__main__":
    # Test the new structure
    print("Available modes:", list(COMPLIANCE_RULES["modes"].keys()))
    print("\nRent rules count:", len(get_rules("rent")))
    print("\nSample rent keywords:", get_all_keywords("rent")[:10])
    print("\nSample rule:", get_rule("deposit_details"))