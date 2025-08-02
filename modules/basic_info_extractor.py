import re
import fitz  # PyMuPDF

def clean_links(raw_links):
    cleaned = []
    for link in raw_links:
        link = re.sub(r'[\s\)\]\.]+$', '', link)
        if "." in link and not link.endswith(("/", "-", ".")):
            cleaned.append(link.strip())
    return list(set(cleaned))

def extract_basic_info(text, extra_links=None):
    if extra_links is None:
        extra_links = []

    name = None
    for line in text.split("\n"):
        line = line.strip()
        if re.match(r"^[A-Z][a-z]+\s[A-Z][a-z]+$", line):
            name = line
            break
        elif re.match(r"^[A-Z][A-Z\s]+$", line) and 2 <= len(line.split()) <= 4:
            name = line.title()
            break
    name = name or "N/A"

    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    email = match.group() if match else "N/A"

    match = match = re.search(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3,5}\)?[-.\s]?)?\d{6,10}', text)
    phone = match.group().strip() if match else "N/A"

    visible_links = re.findall(r"https?://[^\s\n\r\)\]]+", text)
    bare_links = re.findall(r"\b(?:www\.)?(?:[a-zA-Z0-9-]+\.)+[a-z]{2,6}/[^\s\n\r]+", text)
    for link in bare_links:
        if not link.startswith("http"):
            link = "https://" + link
        visible_links.append(link)

    all_links = clean_links(visible_links + extra_links)

    known_social_sites = [
        "linkedin.com", "github.com", "twitter.com", "facebook.com",
        "instagram.com", "medium.com", "youtube.com", "about.me",
        "behance.net", "dribbble.com", "naukri.com", "shine.com",
        "timesjobs.com", "internshala.com", "apna.co", "hirect.in",
        "angel.co", "quora.com", "stackoverflow.com", "telegram.me",
        "telegram.org", "snapchat.com"
    ]

    social_links = {}
    for link in all_links:
        domain_match = re.findall(r"https?://(?:www\.)?([^/]+)", link)
        domain = domain_match[0].lower() if domain_match else ""
        for site in known_social_sites:
            if site in domain:
                platform = site.split(".")[0]
                if platform not in social_links:
                    social_links[platform] = link
                break

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "social_links": social_links
    }