"""Rule-based intent classifier for guardrails."""
import re

# Educational links (AMFI / SEBI investor education pages)
EDUCATIONAL_LINKS = [
    "https://www.amfiindia.com/investor-corner",
    "https://www.amfiindia.com/research-information",
    "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?do=yes",
    "https://www.sebi.gov.in/regulations/act",
]

REFUSAL_TEMPLATE = (
    "I can only provide factual information from official sources, not investment advice. "
    "For educational resources on mutual funds, please visit: {link}"
)

# Patterns that indicate advice-seeking intent (all lowercase — query is lowercased before matching)
ADVICE_PATTERNS = [
    r"\bshould\s+i\s+(buy|sell|invest|put|choose|pick|go\s+for)\b",
    r"\bis\s+(it|this|that)\s+(good|bad|worth|safe|risky)\b",
    r"\bis\s+\w+(\s+\w+)*\s+a\s+good\s+(fund|scheme|investment|option|choice)\b",
    r"\bwill\s+(it|this|that|the\s+fund|the\s+scheme)\s+(go\s+up|go\s+down|rise|fall|perform|grow)\b",
    r"\bwill\s+\w+(\s+\w+)*\s+(go\s+up|go\s+down|rise|fall|perform|grow)\b",
    r"\bwhat\s+should\s+i\s+(buy|invest|do)\b",
    r"\brecommend\b",
    r"\bwhich\s+is\s+(better|best|superior)\b",
    r"\bwhich\s+should\s+i\s+(choose|pick|select|buy|invest)\b",
    r"\bwhich\s+fund\s+is\s+(better|best)\b",
    r"\bwhich\s+scheme\s+is\s+(better|best)\b",
    r"\bmy\s+portfolio\b",
    r"\bmy\s+allocation\b",
    r"\bhow\s+much\s+should\s+i\s+(invest|put)\b",
    r"\bis\s+it\s+a\s+good\s+(time|idea)\s+to\b",
    r"\bshould\s+i\s+(switch|move|shift|redeem)\b",
    r"\bwhat\s+is\s+the\s+best\s+(mutual\s+)?(fund|scheme|option)\b",
    r"\bwhich\s+is\s+the\s+best\s+(mutual\s+)?(fund|scheme|option)\b",
    r"\bcan\s+you\s+(recommend|suggest|advise)\b",
    r"\bplease\s+(recommend|suggest|advise)\b",
    r"\bworth\s+(investing|buying)\b",
    r"\bgood\s+(investment|option|choice)\b",
    r"\bshould\s+i\s+(start|stop|continue)\s+(investing|sipping|putting)\b",
]

# Patterns that indicate factual intent
FACTUAL_PATTERNS = [
    r"\bexpense\s+ratio\b",
    r"\bexit\s+load\b",
    r"\bminimum\s+(sip|investment|amount)\b",
    r"\block[-\s]?in\b",
    r"\briskometer\b",
    r"\brisk\s+(ometer|profile|level)\b",
    r"\bbenchmark\b",
    r"\bhow\s+to\s+(download|get|obtain|access)\b",
    r"\bstatement\b",
    r"\bcapital\s+gains?\b",
    r"\bnav\b",
    r"\bnet\s+asset\s+value\b",
    r"\bfactsheet\b",
    r"\bsid\b",
    r"\bkim\b",
    r"\bscheme\s+information\b",
    r"\bkey\s+information\b",
    r"\bportfolio\b",
    r"\bholdings\b",
    r"\basset\s+allocation\b",
    r"\bsector\s+allocation\b",
    r"\btop\s+holdings\b",
    r"\bfund\s+manager\b",
    r"\binception\s+date\b",
    r"\baum\b",
    r"\bassets\s+under\s+management\b",
    r"\breturns?\b",
    r"\bperformance\b",
    r"\bdividend\b",
    r"\bgrowth\s+option\b",
    r"\bdirect\s+plan\b",
    r"\bregular\s+plan\b",
    r"\belss\b",
    r"\btax\s+saver\b",
    r"\btax\s+(saving|benefit|deduction)\b",
    r"\b80c\b",
    r"\bredemption\b",
    r"\bmaturity\b",
    r"\btenure\b",
    r"\bobjective\b",
    r"\binvestment\s+objective\b",
    r"\bstrategy\b",
    r"\bcorpus\b",
    r"\bsize\b",
    r"\bvolatility\b",
    r"\bstandard\s+deviation\b",
    r"\bsharpe\s+ratio\b",
    r"\bbeta\b",
    r"\balpha\b",
    r"\bsortino\b",
    r"\btreynor\b",
    r"\bexpense\b",
    r"\bfees?\b",
    r"\bcharges?\b",
    r"\bload\b",
    r"\btransaction\s+charges?\b",
    r"\bstt\b",
    r"\bsecurities\s+transaction\s+tax\b",
    r"\bentry\s+load\b",
    r"\bcontingent\s+deferred\s+sales\s+charge\b",
    r"\bcdsc\b",
    r"\bswitch\b",
    r"\btransfer\b",
    r"\bnomination\b",
    r"\bkyc\b",
    r"\bknow\s+your\s+customer\b",
    r"\bpan\b",
    r"\baadhaar\b",
    r"\bbank\s+account\b",
    r"\bmandate\b",
    r"\bauto\s+debit\b",
    r"\bstanding\s+instruction\b",
    r"\bsip\b",
    r"\bsystematic\s+investment\s+plan\b",
    r"\bswp\b",
    r"\bsystematic\s+withdrawal\s+plan\b",
    r"\bstp\b",
    r"\bsystematic\s+transfer\s+plan\b",
    r"\bdividend\s+(reinvestment|payout|option)\b",
    r"\bface\s+value\b",
    r"\bunit\b",
    r"\ballotment\b",
    r"\bsubscription\b",
    r"\bapplication\b",
    r"\bform\b",
    r"\bprocedure\b",
    r"\bprocess\b",
    r"\bhow\s+to\s+(apply|invest|start|register|enroll)\b",
    r"\bwhere\s+to\s+(buy|invest|apply)\b",
    r"\bwho\s+can\s+invest\b",
    r"\beligibility\b",
    r"\bminimum\s+amount\b",
    r"\bmaximum\s+amount\b",
    r"\bmultiple\b",
    r"\badditional\s+purchase\b",
    r"\bminimum\s+additional\s+investment\b",
    r"\bminimum\s+balance\b",
    r"\bminimum\s+redemption\b",
    r"\bredemption\s+amount\b",
    r"\bredemption\s+period\b",
    r"\bsettlement\s+period\b",
    r"\bt\+\d+\b",
    r"\bnav\s+declaration\b",
    r"\bnav\s+availability\b",
    r"\bvaluation\b",
    r"\bpricing\b",
    r"\bfair\s+value\b",
    r"\bmark\s+to\s+market\b",
    r"\bunrealised\s+(gain|loss)\b",
    r"\brealised\s+(gain|loss)\b",
    r"\blong\s+term\s+capital\s+gains?\b",
    r"\bshort\s+term\s+capital\s+gains?\b",
    r"\bindexation\b",
    r"\bstcg\b",
    r"\bltcg\b",
    r"\bholding\s+period\b",
    r"\btax\s+(treatment|implication|consequence)\b",
    r"\btax\s+on\s+mutual\s+funds?\b",
    r"\bdividend\s+distribution\s+tax\b",
    r"\bddt\b",
    r"\bwealth\s+tax\b",
    r"\bgift\s+tax\b",
    r"\binheritance\s+tax\b",
    r"\bprobate\b",
    r"\bwill\b",
    r"\bnominee\b",
    r"\bnomination\s+facility\b",
    r"\bjoint\s+holder\b",
    r"\bguardian\b",
    r"\bminor\b",
    r"\bpower\s+of\s+attorney\b",
    r"\bpoa\b",
    r"\bnon[-\s]?resident\s+indian\b",
    r"\bnri\b",
    r"\boci\b",
    r"\bpio\b",
    r"\bperson\s+of\s+indian\s+origin\b",
    r"\boverseas\s+citizen\s+of\s+india\b",
    r"\bforeign\s+institutional\s+investor\b",
    r"\bfii\b",
    r"\bforeign\s+portfolio\s+investor\b",
    r"\bfpi\b",
    r"\bqualified\s+foreign\s+investor\b",
    r"\bqfi\b",
    r"\bforeign\s+direct\s+investment\b",
    r"\bfdi\b",
]


def classify_intent(query: str) -> str:
    """Classify query intent as FACTUAL, ADVICE, PORTFOLIO, or OPINION."""
    query_lower = query.lower()

    # Check advice patterns first (highest priority)
    for pattern in ADVICE_PATTERNS:
        if re.search(pattern, query_lower):
            # Check if it's a comparison asking for a pick
            if re.search(r"\bwhich\s+is\s+(better|best)\b", query_lower):
                return "OPINION"
            if re.search(r"\bwhich\s+should\s+i\s+(choose|pick|select|buy|invest)\b", query_lower):
                return "OPINION"
            if re.search(r"\bmy\s+(portfolio|allocation)\b", query_lower):
                return "PORTFOLIO"
            return "ADVICE"

    # Check factual patterns
    for pattern in FACTUAL_PATTERNS:
        if re.search(pattern, query_lower):
            return "FACTUAL"

    # Default to FACTUAL for unknown queries (let retrieval decide)
    return "FACTUAL"


def should_refuse(query: str) -> bool:
    """Return True if the query should be refused."""
    intent = classify_intent(query)
    return intent in ("ADVICE", "PORTFOLIO", "OPINION")


def get_refusal_message(query: str) -> str:
    """Get the refusal message with an educational link."""
    intent = classify_intent(query)
    link = EDUCATIONAL_LINKS[0]  # Default to AMFI investor corner

    if intent == "PORTFOLIO":
        link = EDUCATIONAL_LINKS[1]  # AMFI research information
    elif intent == "OPINION":
        link = EDUCATIONAL_LINKS[2]  # SEBI home

    return REFUSAL_TEMPLATE.format(link=link)


def get_educational_link() -> str:
    """Get a default educational link."""
    return EDUCATIONAL_LINKS[0]
