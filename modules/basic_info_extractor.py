import re

def clean_links(raw_links):
    cleaned = []
    for link in raw_links:
        link = re.sub(r'[\s\)\]\.]+$', '', link)
        if "." in link and not link.endswith(("/", "-", ".")):
            candidate = link.strip()
            if candidate and candidate not in cleaned:
                cleaned.append(candidate)
    return cleaned


def extract_basic_info(text, extra_links=None):
    if extra_links is None:
        extra_links = []

    name = None
    for line in text.split("\n"):
        line = line.strip()
        if re.match(r"^[A-Z][a-z]+(\s[A-Z][a-zA-Z\.]+){1,2}$", line):
            name = line
            break
        elif re.match(r"^[A-Z][A-Z\s]+$", line) and 2 <= len(line.split()) <= 4:
            name = line.title()
            break
    name = name or "N/A"

    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    email = email_match.group() if email_match else "N/A"

    phone_match = re.search(
        r"(\+?\d{1,3}[-.\s]?)?(\(?\d{2,4}\)?[-.\s]?)?\d{6,10}", text
    )
    phone = phone_match.group().strip() if phone_match else "N/A"

    visible_links = re.findall(r"https?://[^\s\n\r\)\]]+", text)
    www_links = re.findall(r"(?:www\.[^\s\n\r\)\]]+)", text)
    bare_links = re.findall(r"(?:[a-zA-Z0-9-]+\.)+[a-z]{2,6}(?:/[^\s\n\r\)\]]+)?", text)

    combined = visible_links + www_links + bare_links + extra_links
    all_links = clean_links(combined)

    normalized_links = []
    for raw in all_links:
        link = raw.strip()
        link = re.sub(r'[\u200b\u200c\u200d\uFEFF]', '', link)
        link = re.sub(r'^[^a-zA-Z0-9]+', '', link)          
        link = re.sub(r'^[qQ](?=linkedin\.com)', '', link)  

        m = re.search(
            r'((?:[a-zA-Z0-9-]+\.)+[a-z]{2,6}(?:/[^\s\r\n\)\]]*)?)',
            link,
            flags=re.IGNORECASE
        )

        if m:
            domain_path = m.group(1)
            scheme_m = re.search(r'https?://', link, flags=re.IGNORECASE)
            scheme = scheme_m.group(0) if scheme_m else 'https://'
            link = scheme + domain_path
        else:
            link = re.sub(r'^[^\w]+', '', link)
            if not link.lower().startswith('http'):
                link = 'https://' + link

        link = re.sub(r'^[\s\)\]\.]+', '', link)
        link = re.sub(r'[\s\)\]\.]+$', '', link)

        normalized_links.append(link)

    normalized_links = list(dict.fromkeys(normalized_links))

    social_sites_map = {
        "linkedin.com": "LinkedIn",
        "github.com": "GitHub",
        "twitter.com": "Twitter",
        "facebook.com": "Facebook",
        "instagram.com": "Instagram",
        "medium.com": "Medium",
        "youtube.com": "YouTube",
        "about.me": "AboutMe",
        "behance.net": "Behance",
        "dribbble.com": "Dribbble",
        "naukri.com": "Naukri",
        "shine.com": "Shine",
        "timesjobs.com": "TimesJobs",
        "internshala.com": "Internshala",
        "apna.co": "Apna",
        "hirect.in": "Hirect",
        "angel.co": "AngelList",
        "quora.com": "Quora",
        "stackoverflow.com": "StackOverflow",
        "telegram.me": "Telegram",
        "telegram.org": "Telegram",
        "snapchat.com": "Snapchat"
    }

    social_links = {}
    for link in normalized_links:
        domain_match = re.findall(r"https?://(?:www\.)?([^/]+)", link)
        domain = domain_match[0].lower() if domain_match else ""
        for site, platform in social_sites_map.items():
            if site in domain:
                if platform not in social_links:
                    social_links[platform] = link
                break

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "social_links": social_links
    }