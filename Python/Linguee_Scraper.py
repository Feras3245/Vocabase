import requests
import os
import re
import string
from bs4 import BeautifulSoup
from bs4 import Tag
import csv
import json
from prettytable import *
from textwrap import fill


os.system("")

def bold_text(txt: str) -> str:
    # '\033[1m'
    # '\033[0m'
    return '\033[1m' + txt + '\033[0m'

def change_text_color(txt: str, foreground: str, background: str) -> str:
    # Foreground colors:
        # Black: \u001b[30m
        # Red: \u001b[31m
        # Green: \u001b[32m
        # Yellow: \u001b[33m
        # Blue: \u001b[34m
        # Magenta: \u001b[35m
        # Cyan: \u001b[36m
        # White: \u001b[37m
        # Reset: \u001b[0m

    # Background colors:
        # Black: \u001b[40m
        # Red: \u001b[41m
        # Green: \u001b[42m
        # Yellow: \u001b[43m
        # Blue: \u001b[44m
        # Magenta: \u001b[45m
        # Cyan: \u001b[46m
        # White: \u001b[47m
        # Reset: \u001b[0m
    output = ''
    foreground = foreground.lower()
    if foreground in ('leave', 'keep'):
        foreground = ''
    elif foreground in ('black', '\u001b[30m'):
        foreground = '\u001b[30m'
    elif foreground in ('red', '\u001b[31m'):
        foreground = '\u001b[31m'
    elif foreground in ('green', '\u001b[32m'):
        foreground = '\u001b[32m'
    elif foreground in ('yellow', '\u001b[33m'):
        foreground = '\u001b[33m'
    elif foreground in ('blue', '\u001b[34m'):
        foreground = '\u001b[34m'
    elif foreground in ('magenta', '\u001b[35m'):
        foreground = '\u001b[35m'
    elif foreground in ('cyan', '\u001b[36m'):
        foreground = '\u001b[36m'
    elif foreground in ('white', '\u001b[37m'):
        foreground = '\u001b[37m'
    elif foreground in ('reset', '\u001b[0m'):
        foreground = '\u001b[0m'
    else:
        raise ValueError('invalid or unknown color')
    
    background = background.lower()
    if background in ('leave', 'keep'):
        background = ''
    elif background in ('black', '\u001b[40m'):
        background = '\u001b[40m'
    elif background in ('red', '\u001b[41m'):
        background = '\u001b[41m'
    elif background in ('green', '\u001b[42m'):
        background = '\u001b[42m'
    elif background in ('yellow', '\u001b[43m'):
        background = '\u001b[43m'
    elif background in ('blue', '\u001b[44m'):
        background = '\u001b[44m'
    elif background in ('magenta', '\u001b[45m'):
        background = '\u001b[45m'
    elif background in ('cyan', '\u001b[46m'):
        background = '\u001b[46m'
    elif background in ('white', '\u001b[47m'):
        background = '\u001b[47m'
    elif background in ('reset', '\u001b[0m'):
        background = '\u001b[0m'
    else:
        raise ValueError('invalid or unknown color')

    output = foreground + background + txt + '\u001b[0m'
    return output


def print_result(result: dict):
    keys = []
    vals = []
    for key in result.keys():
        keys.append(key)
        if not isinstance(result[key], list):
            vals.append(result[key])
        else:
            if len(result[key]) != 0:
                combined_val = '(1) ' + result[key][0]
                for i, entry in enumerate(result[key][1:]):
                    combined_val += ' / '
                    combined_val += f'({i+2}) ' + entry
                combined_val = fill(combined_val, width=50)
                vals.append(combined_val)
                pass
            else:
                vals.append('__')
            pass
    table = PrettyTable(field_names=keys)
    table.add_row(vals)
    print(table)
    return

def lemmaScraper(query: str, get_first_only: bool, suppress_errors: bool) -> list:
    print("Scraping For " + change_text_color(f"'{query}'".capitalize(), 'cyan', 'keep') + " Lemmas...")
    def get_pos(word_type: str) -> str:
        pattern = r'^([a-zA-ZäöüÄÖÜß]+)'
        p = re.search(pattern, word_type)
        p = p.group(0)
        return p

    def find_reflexive(exact: Tag):
        reflexive = {}
        non_reflexive = []
        ref_list = []
        lds = exact.find_all('h2', class_='line lemma_desc')
        # search the entire 'exact' section for any verbs
        for ld in lds:
            tl = ld.find('span', class_="tag_lemma")
            wt = tl.find('span', class_="tag_wordtype")
            if wt == None:
                continue
            wt = wt.text.strip()
            p = get_pos(wt)
            if p != 'verb':
                continue
            # for each verb, get the full context of the tag_lemma
            a = tl.find('a', class_='dictLink')
            spans = a.find_all('span')
            if spans:
                for span in spans:
                    span.decompose()
            spanless_text = a.text.strip()
            if bool(re.match(r'sich', spanless_text)):
                pattern = r'^.*\b([a-zA-ZäöüÄÖÜß]+(?:-[a-zA-ZäöüÄÖÜß]+)*)$'
                v = re.search(pattern, spanless_text)
                v = v.group(1)
                div = ld.find_parent('div')
                ref_list.append(div)
                reflexive[v] = ref_list
            else:
                v = spanless_text
                div = ld.find_parent('div')
                non_reflexive.append({v : div})
        output = {}
        if len(reflexive) == 0:
            return False, None
        if len(non_reflexive) == 0:
            for key in reflexive.keys():
                output[key] = reflexive[key]
            return True, output
        for non_ref in non_reflexive:
            non_ref_key = next(iter(non_ref))
            for ref_key in reflexive.keys():
                if ref_key == non_ref_key:
                    ref_list = reflexive[ref_key]
                    ref_list.append(non_ref[non_ref_key])
                    reflexive[ref_key] = ref_list
        # add reflexive dictionary to output
        for key in reflexive.keys():
            output[key] = reflexive[key]
        return True, output
    
    def verb_handler(div: Tag) -> list:
        is_ref = False
        tags = []
        meanings = []
        # get text
        ld = div.find('h2', class_='line lemma_desc')
        tl = ld.find('span', class_="tag_lemma")
        a = tl.find('a', class_='dictLink')
        # get pos before continuing

        pos = 'verb'
        # extract verb text
        spans = a.find_all('span')
        if spans:
            for span in spans:
                span.decompose()
        spanless_text = a.text.strip()
        # if 'sich' is found in spanless_text the word is reflexive
        if bool(re.match(r'sich', spanless_text)):
            # if verb is reflexive append property to tags
            is_ref = True
            pattern = r'^.*\b([a-zA-ZäöüÄÖÜß]+(?:-[a-zA-ZäöüÄÖÜß]+)*)$'
            verb = re.search(pattern, spanless_text)
            verb = verb.group(1)
        else:
            # if no 'sich' is found in spanless_text
            # the verb is not reflexive
            verb = spanless_text
        
        # get meanings list
        meanings = get_translations(div, 'verb')
        if (len(meanings) == 0) or (meanings == None):
            return None

        # if it is reflexive, add (sich) to each meaning
        if is_ref:
            ref_meanings = []
            for meaning in meanings:
                meaning += " (sich)"
                ref_meanings.append(meaning)
            meanings = ref_meanings
        
        # get pp2 and praeteritum
        # verb's meta data are made available by scraping wikitionary
        # and not through the "Linguee API"
        # for that reason, i am using BS4 library
        bs4_response = requests.get(f"https://de.wiktionary.org/wiki/{verb}")
        if bs4_response.status_code == 200:
            soup = BeautifulSoup(bs4_response.text, 'html.parser')
            # get metadata table
            target_class = "wikitable inflection-table float-right flexbox hintergrundfarbe2"
            table = soup.find('table', class_=target_class)
            if table:
                # get praeteritum
                a_element = table.find('a', {'title': 'Hilfe:Präteritum'})
                if a_element:
                    th_element = a_element.find_parent('th')
                    td_element = th_element.find_next('td')
                    td_element = td_element.find_next('td')
                    praet = td_element.text.strip()
                    # get pp2
                    a_element = table.find('a', {'title': 'Hilfe:Hilfsverb'})
                    if a_element:
                        th_element = a_element.find_parent('th')
                        tr_element = th_element.find_parent('tr')
                        tr_element = tr_element.find_next('tr')
                        td_element = tr_element.find('td')
                        pp2_form = td_element.text.strip()
                        # get hilfsverb
                        td_element = td_element.find_next('td')
                        hilfsverb = td_element.text.strip()
                        # if hilfsverb is sein, then add "PZII Mit Sein" tag
                        if hilfsverb == 'sein':
                            tags.append('PPII Mit Sein')
                        pp2 = hilfsverb + ' ' + pp2_form
                    else:
                        if not suppress_errors:
                            print(change_text_color('SCRAPING ERROR:', 'white', 'red') + ' PP2 tag in verb form table not found. Lemma discarded')
                        return None
                else:
                    if not suppress_errors:
                        print(change_text_color('SCRAPING ERROR:', 'white', 'red') + ' Praeteritum tag in verb form table not found. Lemma discarded')
                    return None
            else:
                if not suppress_errors:
                    print(change_text_color('SCRAPING ERROR:', 'white', 'red') + ' Verb form table not found. Cannot retrieve pp2 and pret forms. Lemma discarded')
                return None
        else:
            if not suppress_errors:
                print(change_text_color('SCRAPING ERROR:', 'white', 'red') + ' Wiktionary server bad response. Cannot retrieve pp2 and pret forms. Lemma discarded')
            return None

        # get regular or irregular
        # to determine whether a verb is regular or irregular
        # a GET request to wiktionary is necessary
        # specifically to the verb's flexion page
        # at the end of the page, there is a link
        # if the link or <a> tag is regular
        # it will contain:
        # <a> with href="/wiki/Kategorie:Verbkonjugation_regelm%C3%A4%C3%9Fig_(Deutsch)"
        # if it is irregular it will contain:
        # <a> with href="/wiki/Kategorie:Verbkonjugation_unregelm%C3%A4%C3%9Fig_(Deutsch)"
        bs4_response = requests.get(f"https://de.wiktionary.org/wiki/Flexion:{verb}")
        if bs4_response.status_code == 200:
            soup = BeautifulSoup(bs4_response.text, 'html.parser')
            regularity = soup.find('a', {'href' : '/wiki/Kategorie:Verbkonjugation_regelm%C3%A4%C3%9Fig_(Deutsch)'})
            if regularity:
                tags.append('Regular')
            else:
                regularity = soup.find('a', {'href': '/wiki/Kategorie:Verbkonjugation_unregelm%C3%A4%C3%9Fig_(Deutsch)'})
                if regularity:
                    tags.append('Irregular')
                else:
                    if not suppress_errors:
                        print(change_text_color('SCRAPING ERROR:', 'white', 'red') + ' Could not retrieve verb\'s regularity. Regularity discarded')
        else:
            if not suppress_errors:
                print(change_text_color('SCRAPING ERROR:', 'white', 'red') + ' Wiktionary server: bad response. Discarding "regularity"')
        
        # find out if verb can come with dative or not
        ld = div.find('h2', class_='line lemma_desc')
        tl = ld.find('span', class_="tag_lemma")
        grammar_infos = tl.find_all('span', class_='grammar_info')
        if grammar_infos:
            is_dat = False
            for grammar_info in grammar_infos:
                if grammar_info.text == 'Dat':
                    is_dat = True
            if is_dat:
                tags.append('Dative')

        # get examples
        examples = get_examples(div)
        # combine results and return
        output = [pos, verb, meanings, pp2, praet, tags, examples]
        return output
    
    def reflexive_verb_handler(reflexive: dict) -> list:
        pos = 'verb'
        meanings = []
        tags = []
        examples = []
        combinedInfo = []
        output = []
        for key in reflexive.keys():
            got_general = False
            divs = reflexive[key]
            for div in divs:
                verbInfo = verb_handler(div)
                if verbInfo == None:
                   if not suppress_errors:
                    print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " cannot handle reflexive verb")
                   return None
                if not got_general:
                    got_general = True
                    verb = verbInfo[1]
                    pp2 = verbInfo[3]
                    praet = verbInfo[4]
               # get 3 translations from each lemma
                if len(verbInfo[2]) > 3:
                    verbInfo[2] =verbInfo[2][:3]
                # only combine unique entries with combined meanings
                meanings = list(set(meanings + verbInfo[2]))
                # get 2 examples from each lemma
                if len(verbInfo[6]) > 2:
                    verbInfo[6] = verbInfo[6][:2]
                # only combine unique entries with combined examples
                examples = list(set(examples + verbInfo[6]))
                # only combine unique entries with tags
                tags = list(set(tags + verbInfo[5]))
            # add 'Reflexive' to tags
            tags.append('Reflexive')
            combinedInfo = [pos, verb, meanings, pp2, praet, tags, examples]
            output.append(combinedInfo)
        return output

    def get_translations(div: Tag, pos: str) -> list:
        entries = []
        translation_lines = div.find('div', class_='translation_lines')
        if not translation_lines:
            if not suppress_errors:
                print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " cannot retrieve translations")
            return None
        # translation sortablemg featured
        translations = translation_lines.find_all('div', {'class': ['translation', 'sortablemg']})
        if not translations:
            if not suppress_errors:
                print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " cannot retrieve translations")
            return None
        for translation in translations:
            # dictLink featured
            entry = translation.find('a', class_='dictLink')
            if not entry:
                continue
            spans = entry.find_all('span')
            if spans:
                for span in spans:
                    span.decompose()
            entries.append(entry.text.strip().capitalize())
        if pos == 'verb':
            verb_formatted_entries = []
            for entry in entries:
                verb_formatted_entry = 'To ' + entry
                verb_formatted_entries.append(verb_formatted_entry.capitalize())
            entries = verb_formatted_entries
        if (len(entries) == 0) or (entries == None):
            if not suppress_errors:
                print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " cannot retrieve translations")
            return None
        if len(entries) > 6:
            entries = entries[:6]
        return entries

    def get_examples(div: Tag) -> list:
        examples = []
        example_lines = div.find_all('div', class_='example line')
        if not example_lines:
            if not suppress_errors:
                print(change_text_color('SCRAPING ERROR:', 'white', 'red') + ' No Examples Found')
            return []
        for example_line in example_lines:
            tag_e = example_line.find('span', class_= 'tag_e')
            if not tag_e:
                continue
            example = tag_e.find('span', class_= 'tag_s')
            if not example:
                continue
            examples.append(example.text)
        if (len(examples) == 0) or (examples == None):
            if not suppress_errors:
                print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " cannot retrieve translations")
            return []
        if len(examples) > 3:
            examples = examples[:3]
        return examples

    def noun_handler(div: Tag) -> list:
        ld = div.find('h2', class_='line lemma_desc')
        tl = ld.find('span', class_="tag_lemma")
        noun = tl.find('a', class_='dictLink')
        spans = noun.find_all('span')
        if spans:
            for span in spans:
                span.decompose()
        noun = noun.text.strip()
        # get word_type
        word_type = tl.find('span', class_="tag_wordtype").text
        # get pos
        pos = 'noun'
        # get gender of noun
        pattern = r'\b(feminine|neuter|masculine|plural)\s*$'
        gender = re.search(pattern, word_type)
        if not gender:
            if not suppress_errors:
                print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " cannot find noun gender. Lemma discarded")
            return None
        gender = gender.group(0)
        if gender == 'feminine' or gender == 'plural':
            article = 'Die'
        elif gender == 'masculine':
            article = 'Der'
        elif gender == 'neuter':
            article = 'Das'
        else:
            if not suppress_errors:
                print(change_text_color('SCRAPING ERROR:', 'white', 'red') + ' Unkown Gender')
            return None
        # linguee sometimes has the noun's plural form in the lemma_desc
        # but most times it won't be there
        # for that reason, i will need to check if linguee has plural form
        # but if it is not found, we will scrap the plural form (if possible)
        # from wiktionary

        # try to get the plural form from linguee
        lemma_desc = div.find('h2', class_='line lemma_desc')
        plural_form = lemma_desc.find('span', class_='tag_forms forms_plural')
        if plural_form:
            plural = plural_form.find('span', class_='tag_s').text
        # if you can't try to get from wiktionary
        else:
            # make get request to wiktionary
            response = requests.get(f"https://de.wiktionary.org/wiki/{noun}")
            if not response.status_code == 200:
                if not suppress_errors:
                    print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " Wiktionary server bad response")
                return None
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', class_='wikitable float-right inflection-table flexbox hintergrundfarbe2')
            if not table:
                if not suppress_errors:
                    print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " Wiktionary metadata table not found")
                return None
            plural_hilfe = table.find('a', {'title':'Hilfe:Plural'})
            if not plural_hilfe:
                if not suppress_errors:
                    print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " Wiktionary metadata table not found")
                return None
            nominativ_hilfe = table.find('a', {'title': 'Hilfe:Nominativ'})
            if not nominativ_hilfe:
                if not suppress_errors:
                    print(change_text_color('SCRAPING ERROR:', 'white', 'red') + "Wiktionary metadata table not found")
                return None
            # if both keywords 'plural' and 'nominativ' are found in the table
            # then we are looking at a noun's forms table
            # in that case, we will find the nominative plural form
            # of the noun in the 'nominativ' row at the second table data
            nominativ_hilfe = nominativ_hilfe.find_parent('th')
            nominativ_plural = nominativ_hilfe.find_next('td')
            nominativ_plural = nominativ_plural.find_next('td').text
            if nominativ_plural == '—\n':
                plural = '__'
            else:
                pattern = r'^.*\b([a-zA-ZäöüÄÖÜß]+(?:-[a-zA-ZäöüÄÖÜß]+)*)$'
                nominativ_plural = re.search(pattern, nominativ_plural)
                plural = nominativ_plural.group(1)
        # get translations list
        meanings = get_translations(div, 'noun')
        if (len(meanings) == 0) or (meanings == None):
            return None
        examples = get_examples(div)
        output = [pos, noun, article, plural, meanings, examples]
        return output
    
    def adj_handler(div: Tag) -> list:
        pos = 'adjective'

        # get text
        ld = div.find('h2', class_='line lemma_desc')
        tl = ld.find('span', class_="tag_lemma")
        adj = tl.find('a', class_='dictLink')
        spans = adj.find_all('span')
        if spans:
            for span in spans:
                span.decompose()
        adj = adj.text.strip()
        
        #get meanings
        meanings = get_translations(div, 'adjective')
        if (len(meanings) == 0) or (meanings == None):
            return None

        # get comparative and superaltive
        # adjective's meta data are also made available by scraping wikitionary
        # and not through the "Linguee API"
        bs4_response = requests.get(f"https://de.wiktionary.org/wiki/{text}")
        if bs4_response.status_code == 200:
            soup = BeautifulSoup(bs4_response.text, 'html.parser')
            # get metadata table
            target_class = "wikitable inflection-table float-right flexbox hintergrundfarbe2"
            table = soup.find('table', class_=target_class)
            # get comparative form
            if table:
                a_element = table.find('a', {'title': 'Hilfe:Komparativ'})
                if a_element:
                    # get comparative form
                    tr_element = a_element.find_parent('tr')
                    tr_element = tr_element.find_next('tr')
                    td_element = tr_element.find('td')
                    td_element = td_element.find_next('td')
                    comparative = td_element.text.strip()
                    # get superlative form
                    td_element = td_element.find_next('td')
                    superlative = td_element.text.strip()
                else:
                    if not suppress_errors:
                        print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " Incorrect Wiktionary table. Cannot retrieve comparative and superlative forms")
                    return None
            else:
                if not suppress_errors:
                    print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " Wiktionary's adjective forms table not found. Cannot retrieve comparative and superlative forms")
                return None
        else:
            if not suppress_errors:
                print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " Wiktionary bad server response. Cannot retrieve comparative and superlative forms")
            return None
        
        examples = get_examples(div)

        # prepare data for return
        output = [pos, adj, meanings, comparative, superlative, examples]
        return output
    
    def adv_handler(div: Tag) -> list:
        pos = 'adverb'

        # get text
        ld = div.find('h2', class_='line lemma_desc')
        tl = ld.find('span', class_="tag_lemma")
        adv = tl.find('a', class_='dictLink')
        spans = adv.find_all('span')
        if spans:
            for span in spans:
                span.decompose()
        adv = adv.text.strip()

        meanings = get_translations(div, 'adverb')
        if (len(meanings) == 0) or (meanings == None):
            return None
        
        examples = get_examples(div)

        # prepare data for return
        output = [pos, adv, meanings, examples]
        return output

    # prepare to send request
    url = f"https://www.linguee.com/german-english/translation/{query}.html"
    response = requests.get(url)
    if not (response.status_code == 200):
        if not suppress_errors:
            print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " Linguee server did not respond with status_code: OK")
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    # In case a word is common to both german and english
    # ensure that only the german dictionary is selected
    german_dictionary = soup.find('div', {'data-source-lang': "DE"})
    if not german_dictionary:
        if not suppress_errors:
            print(change_text_color('SCRAPING ERROR:', 'white', 'red') + ' no german dictionary found on query\'s page')
        return None
    # find <div> inside the german dictionary where class="exact"
    # all desired content is located here
    exact = german_dictionary.find('div', class_='exact')
    output = []
    if not exact:
        return None
    # get reflexive verbs
    # reflexive verbs need to be processed separately
    # since reflexive verbs contain multi-word texts
    # and are stored in a separate lemma
    # if they have a non-reflexive version.
    is_ref, reflexive = find_reflexive(exact)
    if is_ref:
        # since reflexive verbs and their non reflexive versions will
        # be stored in reflexive, they need to be removed from exact
        # to avoid data duplication.
        for key in reflexive.keys():
            divs = reflexive[key]
            for div in divs:
                h2 = div.find('h2', class_='line lemma_desc')
                lid = h2.attrs['lid']
                in_exact = exact.find('h2', {'lid':lid})
                in_exact = in_exact.find_parent('div')
                in_exact.extract()
        ref_infos = reflexive_verb_handler(reflexive)
        for ref_info in ref_infos:
            data = {}
            # [pos, verb, meanings, pp2, praet, tags, examples]
            if ref_info == None:
                if not suppress_errors:
                    print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " Could not retrieve verb '"+text+"' Info")
                continue
            data['pos'] = ref_info[0]
            data['text'] = ref_info[1].capitalize()
            data['meanings'] = ref_info[2]
            data['ppii'] = ref_info[3].capitalize()
            data['praet'] = ref_info[4].capitalize()
            data['tags'] = ref_info[5]
            data['examples'] = ref_info[6]
            print(change_text_color("SUCCESS!", 'black', 'green') + change_text_color(" Reflexive Verb ", 'magenta', 'keep') + "Lemma Found!")
            output.append(data)

    
    lemma_descs = exact.find_all('h2', class_='line lemma_desc')
    if len(lemma_descs) == 0 or lemma_descs == None:
        if len(output) == 0:
            if not suppress_errors:
                print(change_text_color('SCRAPING ERROR:', 'white', 'red') + ' No translations found on Linguee page')
            return []
        else:
            return output
    
    for lemma_desc in lemma_descs:
        data = {}
        # get 'text', 'pos', and (if noun) 'gender'
        tag_lemma = lemma_desc.find('span', class_="tag_lemma")
        # get text
        text = tag_lemma.find('a', class_='dictLink').text.strip()
        # if the lemma text contains more than one word
        # then discard lemma
        if (not (bool(re.match(r"^[a-zA-ZäöüÄÖÜß-]+$", text)))):
            if not suppress_errors:
                print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " multi-word definition detected. Lemma discarded")
            continue
        # get 'pos'
        word_type = tag_lemma.find('span', class_="tag_wordtype")
        if not word_type:
            continue
        word_type = word_type.text
        pos = get_pos(word_type)
        parent_div = lemma_desc.find_parent('div')
        if pos == 'noun':
            nounInfo = noun_handler(parent_div)
            if nounInfo == None:
                if not suppress_errors:
                    print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " Could not retrieve noun '"+text+"' Info")
                continue
            data['pos'] = nounInfo[0]
            data['text'] = nounInfo[1].capitalize()
            data['article'] = nounInfo[2]
            data['plural'] = nounInfo[3].capitalize()
            data['meanings'] = nounInfo[4]
            data['examples'] = nounInfo[5]

            print(change_text_color("SUCCESS!", 'black', 'green') + change_text_color(" Noun ", 'magenta', 'keep') + "Lemma Found!")
            output.append(data)
        elif pos == 'verb':
            verbInfo = verb_handler(parent_div)
            if verbInfo == None:
                if not suppress_errors:
                    print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " Could not retrieve verb '"+text+"' Info")
                continue
            data['pos'] = verbInfo[0]
            data['text'] = verbInfo[1].capitalize()
            data['meanings'] = verbInfo[2]
            data['ppii'] = verbInfo[3].capitalize()
            data['praet'] = verbInfo[4].capitalize()
            data['tags'] = verbInfo[5]
            data['examples'] = verbInfo[6]

            print(change_text_color("SUCCESS!", 'black', 'green') + change_text_color(" Verb ", 'magenta', 'keep') + "Lemma Found!")
            output.append(data)
        elif pos == 'adjective':
            adjInfo = adj_handler(parent_div)
            if adjInfo == None:
                if not suppress_errors:
                    print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " Could not retrieve adjective '"+text+"' Info")
                continue
            data['pos'] = adjInfo[0]
            data['text'] = adjInfo[1].capitalize()
            data['meanings'] = adjInfo[2]
            data['comparative'] = adjInfo[3].capitalize()
            data['superlative'] = adjInfo[4].capitalize()
            data['examples'] = adjInfo[5]

            print(change_text_color("SUCCESS!", 'black', 'green') + change_text_color(" Adjective ", 'magenta', 'keep') + "Lemma Found!")
            output.append(data)
        elif pos == 'adverb':
            advInfo = adv_handler(parent_div)
            if advInfo == None:
                print(change_text_color('SCRAPING ERROR:', 'white', 'red') + " Could not retrieve adverb '"+text+"' Info")
                continue
            data['pos'] = advInfo[0]
            data['text'] = advInfo[1].capitalize()
            data['meanings'] = advInfo[2]
            data['examples'] = advInfo[3]

            print(change_text_color("SUCCESS!", 'black', 'green') + change_text_color(" Adverb ", 'magenta', 'keep') + "Lemma Found!")
            output.append(data)
    if (not (len(output) == 0)) and (not (output == None)):
        if get_first_only:
            output = [output.pop(0)]
    return output


        


