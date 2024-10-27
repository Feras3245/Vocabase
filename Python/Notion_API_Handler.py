import requests
import os
import re
import string
from bs4 import BeautifulSoup
from bs4 import Tag
import csv
import json



class Notion_API_Handler:
    class NotionError(Exception):
        def __init__(self, message: str):
            # Call the base class constructor with the error message
            super().__init__(message)


    __ACTIVE_NOMEN_DB_ID = None
    __ACTIVE_VERBEN_DB_ID = None
    __ACTIVE_ADJ_DB_ID = None
    __ACTIVE_ADV_DB_ID = None

    __VOCABASE_ID = 'Database ID removed to safely clone project to Github'

    #### AUTHENTICATION DATA: always the same across requests ##################
    __HEADERS = {
        'Authorization' : 'Secret removed to safely clone project to Github',
        'Content-Type' : 'application/json',
        'Notion-Version' : '2022-06-28'
    }
    ############################################################################

    ###### FULL LIST OF ENDPOINTS: https://developers.notion.com/reference/intro ###########################################

    def get_child_pages(self, page_id: str) -> dict:
        # if the page_id is neither 32 (unhyphenated) nor 36 (hyphenated) characters long
        # then it is invalid, return an ERROR
        if (len(page_id) != 32) and (len(page_id) != 36):
            raise Notion_API_Handler.NotionError('get_child_pages(): Invalid Page ID')
        # if it is unhyphentated 32 characters long, then add hyphens
        elif len(page_id) == 32:
            formatted_page_id = (
            page_id[:8] + '-' +
            page_id[8:12] + '-' +
            page_id[12:16] + '-' +
            page_id[16:])
            page_id = formatted_page_id
        # if it is 36 characters long then it is already hyphenated
        root_url = f'https://api.notion.com/v1/blocks/{page_id}/children?page_size=100'
        payload = {"page_size" : 200}
        response = requests.get(root_url, headers= self.__HEADERS)
        if response.status_code == 200:
            data = response.json()
            if not ('results' in data.keys()):
                raise Notion_API_Handler.NotionError('get_child_pages(): "results" key not found in response.json()')
            results = data['results']
            if len(results) == 0:
                raise Notion_API_Handler.NotionError('get_child_pages(): no child pages found response.json()')
            output = []
            # 'child_database’
            for result in results:
                meta = {}
                if result['type'] == 'child_page':
                    meta['type'] = result['type']
                    meta['title'] = result['child_page'].get('title')
                    meta['id'] = result['id']
                    meta['has_children'] = result['has_children']
                    output.append(meta)
                elif result['type'] == 'child_database':
                    meta['type'] = result['type']
                    meta['title'] = result['child_database'].get('title')
                    meta['id'] = result['id']
                    meta['has_children'] = result['has_children']
                    output.append(meta)
            if len(output) == 0:
                raise Notion_API_Handler.NotionError('get_child_pages(): no child pages found response.json()')
            return output
        else:
            raise Notion_API_Handler.NotionError('get_child_pages(): Notion API bad response')

    def insert_notion_row(self, data: dict) -> bool:
        def notionDataFormatter(data:dict) -> dict:
            def tags_formatter(tags: list) -> str:
                output = []
                for tag in tags:
                    output.append({'name':tag})
                return output

            def translationsFormatter(translations: list) -> str:
                output = ""
                translations = translations.copy()
                if len(translations) != 0:
                    output += translations.pop(0)
                    for translation in translations:
                        output += " / "
                        output += translation
                return output

            def examplesFormatter(examples: list) -> str:
                output = ""
                examples = examples.copy()
                if (examples != None) and (len(examples) != 0):
                    output += examples.pop(0)
                    for example in examples:
                        output += " / "
                        output += example
                return output

            wordclass = data.get('pos')
            if wordclass == 'noun':
                article = data.get('article')
                text = data.get('text')
                plural = data.get('plural')
                meanings = translationsFormatter(data.get('meanings'))
                examples = examplesFormatter(data.get('examples'))
                formatted_data = {
                    "Article": {"select": {"name": article}},
                    "Noun": {"title": [{"text":{"content": text}}]},
                    "Plural": {"rich_text": [{"text": {"content": plural}}]},
                    "Meaning": {"rich_text": [{"text":{"content": meanings}}]},
                    "Examples": {"rich_text": [{"text":{"content": examples}}]}
                }
                return formatted_data

            elif wordclass == 'verb':
                text = data.get('text')
                meanings = translationsFormatter(data.get('meanings'))
                pp2 = data.get('ppii')
                praet = data.get('praet')
                examples = examplesFormatter(data.get('examples'))
                tags = tags_formatter(data.get('tags'))
                formatted_data = {
                    "Verb": {"title": [{"text": {"content": text}}]},
                    "Meaning": {"rich_text": [{"text": {"content": meanings}}]},
                    "PPII": {"rich_text": [{"text": {"content": pp2}}]},
                    "Preterite": {"rich_text": [{"text": {"content": praet}}]},
                    "Tags": {"multi_select": tags},
                    "Examples": {"rich_text": [{"text": {"content": examples}}]}
                }
                return formatted_data

            elif wordclass == 'adjective':
                text = data.get('text')
                meanings = translationsFormatter(data.get('meanings'))
                comparative = data.get('comparative')
                superlative = data.get('superlative')
                examples = examplesFormatter(data.get('examples'))
                formatted_data = {
                    "Adjective": {"title": [{"text": {"content": text}}]},
                    "Meaning": {"rich_text" :[{"text": {"content": meanings}}]},
                    "Comparative": {"rich_text": [{"text": {"content": comparative}}]},
                    "Superlative": {"rich_text": [{"text": {"content": superlative}}]},
                    "Examples": {"rich_text": [{"text": {"content": examples}}]}
                }
                return formatted_data

            elif wordclass == 'adverb':
                text = data.get('text')
                meanings = translationsFormatter(data.get('meanings'))
                examples = examplesFormatter(data.get('examples'))
                formatted_data = {
                    "Adverb": {"title": [{"text": {"content": text}}]},
                    "Meaning": {"rich_text" :[{"text": {"content": meanings}}]},
                    "Examples": {"rich_text": [{"text": {"content": examples}}]}
                }
                return formatted_data

        root_url = f'https://api.notion.com/v1/pages'
        formatted_data = notionDataFormatter(data)

        payload = {}
        wordclass = data.get('pos')
        if wordclass == 'noun':
            payload["parent"] = {"database_id": self.__ACTIVE_NOMEN_DB_ID}
        elif wordclass == 'verb':
            payload["parent"] = {"database_id": self.__ACTIVE_VERBEN_DB_ID}
        elif wordclass == 'adjective':
            payload["parent"] = {"database_id": self.__ACTIVE_ADJ_DB_ID}
        elif wordclass == 'adverb':
            payload["parent"] = {"database_id": self.__ACTIVE_ADV_DB_ID}

        payload["properties"] = formatted_data
        response = requests.post(root_url, headers= self.__HEADERS, json= payload)
        if response.status_code == 200:
            return True
        else:
            print(response.text)
            return False

    def __init__(self, desired_niveau: str, desired_week: int):
        print('Initializing Notion API Handler...')
        ## Ensure data integrity
        ## standardize format of input
        if desired_niveau == 'A1.2':
            raise ValueError('Since A1.2 Data does not follow new properties standards, it is not possible to modify or read from it.')
        pattern = r'^\b[ABCabc][12].[12]\b$'
        desired_niveau = desired_niveau.strip()
        if not bool(re.match(pattern, desired_niveau)):
            raise ValueError('Invalid Niveau!')
        
        # validate week value:
        if not desired_week:
            raise ValueError('Week not provided.')
        elif (desired_week <= 0):
            raise ValueError('negative or zero week number.')
        desired_week = f"Week {desired_week}"

        # standardize desired DBs parent page title
        desired_niveau = desired_niveau.upper()
        # desired_niveau + ' Week ' + desired_week
        desired_week_title = desired_niveau + " " + desired_week

        # standardize desired DB titles
        # example:
            # Week 3 - Nomen
            # Week 3 - Verben
            # Week 3 - Adjektive
            # Week 3 - Adverbien
        desired_nomen_db_title = desired_week + ' - Nomen'
        desired_verben_db_title = desired_week + ' - Verben'
        desired_adj_db_title = desired_week + ' - Adjektive'
        desired_adv_db_title = desired_week + ' - Adverbien'

        # get Vocabase child pages
        # which are A1.2, A2.1, A2.2, etc.
        try:
            vocabase_niveaus = self.get_child_pages(self.__VOCABASE_ID)
        except Notion_API_Handler.NotionError as err:
            raise err
        
        # find the desired Niveau page info
        desired_niveau_page_info = None
        for vocabase_niveau in vocabase_niveaus:
            if vocabase_niveau['title'] == desired_niveau:
                desired_niveau_page_info = vocabase_niveau
                break
        if desired_niveau_page_info == None:
            raise Notion_API_Handler.NotionError('Requested niveau page not found')
        
        # get Week pages of the desired Niveau page
        try:
            niveau_weeks = self.get_child_pages(desired_niveau_page_info['id'])
            pass
        except Notion_API_Handler.NotionError as err:
            raise err
        
        # find rhe desired Week page in the desired Niveau page
        desired_week_page_info = None
        for niveau_week in niveau_weeks:
            if niveau_week['title'] == desired_week_title:
                desired_week_page_info = niveau_week
                break
        
        if desired_week_page_info == None:
            raise Notion_API_Handler.NotionError('Requested week page not found')
        
        # get DB pages of the desired Week page
        try:
            desired_week_db_infos = self.get_child_pages(desired_week_page_info['id'])
            with open('dump.json', 'w', encoding='utf-8') as dump_file:
                json.dump(desired_week_db_infos, dump_file)
                dump_file.close()
        except Notion_API_Handler.NotionError as err:
            raise err
        
        # find desired DBs in the desired Week page
        desired_nomen_db_info = None
        desired_verben_db_info = None
        desired_adj_db_info = None
        desired_adv_db_info = None
        for desired_week_db_info in desired_week_db_infos:
            if desired_week_db_info['title'] == desired_nomen_db_title:
                desired_nomen_db_info = desired_week_db_info
            elif desired_week_db_info['title'] == desired_verben_db_title:
                desired_verben_db_info = desired_week_db_info
            elif desired_week_db_info['title'] == desired_adj_db_title:
                desired_adj_db_info = desired_week_db_info
            elif desired_week_db_info['title'] == desired_adv_db_title:
                desired_adv_db_info = desired_week_db_info

        if desired_nomen_db_info == None:
            raise Notion_API_Handler.NotionError('Nomen DB not found')
        elif desired_verben_db_info == None:
            raise Notion_API_Handler.NotionError('Verben DB not found')
        elif desired_adj_db_info == None:
            raise Notion_API_Handler.NotionError('Adjektive DB not found')
        elif desired_adv_db_info == None:
            raise Notion_API_Handler.NotionError('Adverbien DB not found')

        self.__ACTIVE_NOMEN_DB_ID = desired_nomen_db_info['id'].replace("-", "")
        self.__ACTIVE_VERBEN_DB_ID = desired_verben_db_info['id'].replace("-", "")
        self.__ACTIVE_ADJ_DB_ID = desired_adj_db_info['id'].replace("-", "")
        self.__ACTIVE_ADV_DB_ID = desired_adv_db_info['id'].replace("-", "")

        print('Notion API Handler Initialization Successfully Completed.')
        return