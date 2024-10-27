# Vocabase
## About
Vocabase is a Python command-line tool designed to automate the extraction of detailed information about German terms from popular online German-English dictionaries, specifically [Linguee.com](http://Linguee.com) and [wiktionary.org](http://wiktionary.org/). 

The inspiration behind Vocabase was to streamline my German language learning process by automating vocabulary collection. I use [Notion.io](http://Notion.io) as a primary platform to organize study notes, guides, and an extensive vocabulary database where I log every new German word I encounter. Initially, manually entering each term was time-consuming, prompting me to develop a tool to automate this process and improve efficiency.

After exploring various public German-English APIs, I found that they all had limitations for my use case, such as missing critical information, incomplete definitions, or access restrictions behind a paywall. Vocabase addresses these gaps by web scraping my preferred online dictionaries, providing complete control over the data collected for my Notion-based database.

Vocabase queries a German term and makes GET requests to the search functions of [Linguee.com](http://linguee.com) and [wiktionary.org](https://www.wiktionary.org/), using the `BeautifulSoup4` library to scrape and extract key details, such as sentence context, definitions, grammatical forms, articles, plurals (for nouns), and example usages.

The data is presented in a user-friendly tabular format, where each distinct result (lemma) is displayed in a separate table. Users can then utilize SQL-like commands to `insert`, `edit`, or `delete` any entries, offering a flexible and efficient way to manage vocabulary data.
## Warnings

### Data Extraction Disclaimer

This project is intended solely for personal use. [Linguee.com](http://linguee.com) and its parent company, DeepL SE, expressly prohibit unauthorized scraping of their data. Use of this tool without appropriate precautions, such as a VPN or proxy service, may lead to a permanent IP ban from Linguee and expose you to potential copyright or legal liabilities.

### API Key and Database Configuration

For security reasons, the Notion database ID and Notion API secret key have been removed from the **`Notion_API_Handler.py`** file (lines 24 and 28, respectively).

To test this tool, you’ll need to generate your own Notion API key via the [Notion API](https://developers.notion.com/) and create an integration linked to your personal Notion database. Ensure that your database is named `Vocabase` and matches the structure of the original for proper functionality.

For detailed setup information, please refer to the [Notion API Overview](https://developers.notion.com/docs/getting-started).

## Dependencies

This project relies on the following Python libraries and packages:

- `BeautifulSoup4`: For web scraping HTML content
- `requests`: For handling HTTP requests
- `prettytable`: For formatting and displaying data in a table

## Database Structure

- Vocabulary collected for each language proficiency level, or "Niveau," is organized on separate Notion pages.

  ![niveaus](https://github.com/user-attachments/assets/fd6fb62f-c950-433b-a89a-6854536d8240)

- Each level contains multiple weekly pages (e.g., `B1.1 Week 1` or `A2.1 Week 3`) where vocabulary learned that week is stored.

  ![weeks](https://github.com/user-attachments/assets/58acab94-5d80-4c3f-8ef0-cdf0382e4bb1)

- Within each weekly page, vocabulary is further categorized into distinct tables for verbs, nouns, adverbs, and adjectives to align relevant sentence structures with dedicated data columns.

  ![pos](https://github.com/user-attachments/assets/f784d6f1-eb68-4a74-8311-40870433b96b)


### Table Structure by Category

![verbs](https://github.com/user-attachments/assets/0bb1ef88-6660-4812-a53e-349e44c7588f)

- **Verbs Table**  
  - Columns: 
    - Verb
    - Meaning (Definition List)
    - PPII
    - Preterit
    - Tags (e.g., `PPII mit sein`, `Irregular`, `Reflexive`)
    - Examples

![nouns](https://github.com/user-attachments/assets/c3f6ad78-45c2-4d93-8228-b90ec121dd24)

- **Nouns Table**  
  - Columns:
    - Article (`Der`, `Die`, `Das`)
    - Noun
    - Plural
    - Meaning
    - Examples

![adjectives](https://github.com/user-attachments/assets/43f41190-aca6-409f-9b5c-db8de8fe52e9)

- **Adjectives Table**  
  - Columns:
    - Adjective
    - Meaning
    - Comparative
    - Superlative
    - Examples

![adverbs](https://github.com/user-attachments/assets/4a56e482-8db8-4245-a78b-9c61c0b408b5)

- **Adverbs Table**  
  - Columns:
    - Adverb
    - Meaning
    - Examples
