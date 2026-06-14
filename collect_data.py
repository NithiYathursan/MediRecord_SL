import os
import time
import requests
import pandas as pd
import fitz
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# Create data folder if it does not exist
os.makedirs("data", exist_ok=True)


# Header tells the website who is requesting
HEADERS = {
    "User-Agent": "MediRecordSL-EducationalProject/1.0"
}


# Sri Lankan public health source pages
source_sites = [
    {
        "source_name": "Ministry of Health Sri Lanka - Manuals and Guidelines",
        "url": "https://www.health.gov.lk/moh-page/other-manuals-guidelines/"
    },
    {
        "source_name": "Epidemiology Unit Sri Lanka - Weekly Epidemiological Reports",
        "url": "https://www.epid.gov.lk/weekly-epidemiological-report"
    },
    {
        "source_name": "Ministry of Health Sri Lanka - Annual Health Bulletin",
        "url": "https://www.health.gov.lk/annual-health-bulletin/"
    },
    {
        "source_name": "Ministry of Health Sri Lanka - Health Policy Repository",
        "url": "https://www.health.gov.lk/moh-page/health-policy-repository/"
    },
    {
        "source_name": "Family Health Bureau Sri Lanka - Guidelines",
        "url": "https://fhb.health.gov.lk/guideline/"
    },
    {
        "source_name": "Private Health Services Regulatory Council - Guidelines",
        "url": "https://www.phsrc.lk/pages_e.php?id=3"
    },
    {
        "source_name": "National STD/AIDS Control Programme - Publications",
        "url": "https://aidscontrol.gov.lk/index.php?Itemid=28&id=19&lang=en&option=com_content&view=article"
    }
]


# Function 1: Get all PDF links from one webpage
def pdf_links_get(page_url):
    try:
        response = requests.get(page_url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        pdf_links = []

        for link in soup.find_all("a", href=True):
            href = link["href"]

            if ".pdf" in href.lower():
                full_url = urljoin(page_url, href)
                title = link.get_text(strip=True)

                pdf_links.append({
                    "title": title if title else "PDF Document",
                    "pdf_url": full_url
                })

        # Remove duplicate PDF links
        unique_links = []
        seen_urls = set()

        for item in pdf_links:
            if item["pdf_url"] not in seen_urls:
                unique_links.append(item)
                seen_urls.add(item["pdf_url"])

        return unique_links

    except Exception as error:
        print("Could not get PDF links from:", page_url)
        print("Error:", error)
        return []


# Function 2: Extract text from all pages of one PDF
def extract_pdf(pdf_url):
    try:
        response = requests.get(pdf_url, headers=HEADERS, timeout=60)
        response.raise_for_status()

        # Check whether downloaded file is really a PDF
        if not response.content.startswith(b"%PDF"):
            print("This file is not a valid PDF.")
            return ""

        pdf_document = fitz.open(stream=response.content, filetype="pdf")

        full_text = ""

        # Read all pages
        total_pages = pdf_document.page_count

        for page_number in range(total_pages):
            page = pdf_document.load_page(page_number)
            text = page.get_text("text")

            if text:
                full_text = full_text + text + " "

        pdf_document.close()

        return full_text.strip()

    except Exception as error:
        print("Could not extract PDF:", pdf_url)
        print("Error:", error)
        return ""


# Function 3: Collect data from all source websites
def data_collect():
    all_data = []
    skipped_data = []

    for source in source_sites:
        source_name = source["source_name"]
        page_url = source["url"]

        print("\n************************************")
        print("Scraping Source:", source_name)
        print("URL:", page_url)
        print("**************************************")

        pdf_items = pdf_links_get(page_url)

        print("PDF links found:", len(pdf_items))

        if len(pdf_items) == 0:
            print("No PDF links found in this source.")
            continue

        # Read all PDF links from this source
        for item in pdf_items:
            title = item["title"]
            pdf_url = item["pdf_url"]

            print("\nReading PDF:", title)
            print("PDF URL:", pdf_url)

            text = extract_pdf(pdf_url)

            if text:
                word_count = len(text.split())
            else:
                word_count = 0

            print("Words extracted:", word_count)

            if word_count >= 10:
                all_data.append({
                    "source_name": source_name,
                    "source_page": page_url,
                    "document_title": title,
                    "pdf_url": pdf_url,
                    "word_count": word_count,
                    "text": text
                })

                print("Saved this PDF text.")
            else:
                skipped_data.append({
                    "source_name": source_name,
                    "source_page": page_url,
                    "document_title": title,
                    "pdf_url": pdf_url,
                    "reason": "No readable text or very low word count"
                })

                print("Skipped this PDF.")

            # Delay to avoid sending too many requests quickly
            time.sleep(1)

    # Save collected data
    df = pd.DataFrame(all_data)

    if df.empty:
        print("\nNo data collected.")
    else:
        df.to_csv(
            "data/raw_srilanka_health_text.csv",
            index=False,
            encoding="utf-8"
        )

        print("\nData collection completed.")
        print("Saved file: data/raw_srilanka_health_text.csv")
        print("Total records collected:", len(df))

    # Save skipped PDF details
    skipped_df = pd.DataFrame(skipped_data)

    if not skipped_df.empty:
        skipped_df.to_csv(
            "data/skipped_pdfs.csv",
            index=False,
            encoding="utf-8"
        )

        print("Skipped PDF file saved: data/skipped_pdfs.csv")
        print("Total skipped PDFs:", len(skipped_df))


# Run the program
data_collect()