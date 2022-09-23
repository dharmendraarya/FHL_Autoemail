from traceback import print_tb
from typing_extensions import Self
import openai

from keybert import KeyBERT
from keyphrase_vectorizers import KeyphraseCountVectorizer
import streamlit as st

def get_config(keyname, sectionname='SETTING'):  

    # configur = ConfigParser()
    # configur.read('config.ini')  
    # return configur[sectionname][keyname]
    return st.secrets[sectionname][keyname]

class ml_backend:
    
    openai.api_key = get_config('OPENAI_KEY')
    
    def generate_email(self, userPrompt ="Write me a professionally sounding email", slider = "150",creativity=0.5,emailVariants=2):
        """Returns a generated an email using GPT3 with a certain prompt and starting sentence"""
        response = openai.Completion.create(
            engine="davinci-instruct-beta",
            prompt=userPrompt, #+ "\n\n" + start,
            temperature=creativity,
            max_tokens=slider,
            top_p=1,
            best_of=emailVariants,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            n=emailVariants
        )
        return response.get("choices")#[0]['text']

    def replace_spaces_with_pluses(self, sample):
        """Returns a string with each space being replaced with a plus so the email hyperlink can be formatted properly"""
        changed = list(sample)
        for i, c in enumerate(changed):
            if(c == ' ' or c =='  ' or c =='   ' or c=='\n' or c=='\n\n'):
                changed[i] = '+'
        return ''.join(changed)

    def get_key_phrase(self, docs, top_cnt):
        kw_model = KeyBERT()
        response =  kw_model.extract_keywords(docs=docs, vectorizer=KeyphraseCountVectorizer(), top_n=top_cnt)
        return ','.join ([x for x,_ in response])
