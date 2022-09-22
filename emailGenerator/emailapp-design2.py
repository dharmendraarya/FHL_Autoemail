#from turtle import back
import streamlit as st
import openai
from ml_backend import *
from scrapperutility import scrapperutility
import pandas as pd
st.set_page_config (layout="wide")
st.header("Hyperpersonalize Email Generator App")

# st.markdown(""" 

# # About
 
# ## Play around with the sliders and text fields to generate your very own emails! 
# ## At the end, you can automatically send your email to a recipient via Gmail  

# ## Business Benefits and Usecases:
# * Time saved writing medium-long sized emails
# * Mental Energy is conserved
# * Anxiety of writing a **professional sounding** email (or email with any writing style) is removed as the GPT3 Language model used is trained from a variety of many different internet sources

# """)


st.sidebar.markdown("# Generate Email")

backend = ml_backend()
scrapper = scrapperutility()

metaDatadf = pd.DataFrame(
    {
        'category': ["Sales", "Recruitment", "Recruitment"],
        'Intention' :["Product offering to a customer", "Initial email to candidate", "reply email to candidate"],
    }
)

linkedProfilesdf = pd.read_csv(get_config('JSONPROFILEDATAPATH') +'/linkedProfiles.csv')
category = st.sidebar.radio("Choose email Outreach category", metaDatadf['category'].unique())
intention = st.sidebar.selectbox("Intention", metaDatadf.where(metaDatadf['category'] == category)['Intention'].dropna().unique())
#typeofemail = st.sidebar.selectbox("Type of email", options = ["Initial", "reply"])
st.sidebar.markdown("_________")
language = st.sidebar.selectbox("Choose language", options = ["English", "Arabic"])
tone = st.sidebar.selectbox("Select tone", options = ["Funny", "Assertive", "Appreciative"])
if (category == "Sales") :
    #with st.expander("Product Detail : ") :
    st.sidebar.markdown("_________")
    productname = st.sidebar.text_input("Enter Product Name")
    productdescription = st.sidebar.text_input("Enter Product description")

col1 , col2 = st.columns(spec = [100,80])
with col1.form(key="form"):
    #with st.expander("Describe Email content: ") :
    prompt = st.text_input("Describe the Kind of Email you want to be written.")
    st.text(f"(Example: Data science opening at Contoso.com)")

    start = st.text_input("Begin writing the first few or several words of your email:")

    slider = st.slider("How many characters do you want your email to be? ", min_value=64, max_value=750)
    st.text("(A typical email is usually 100-500 characters)")
    
    key_phrases = ""
    name_of_person = ""
    #with st.expander("Personalization Section : ") :
    # linkedinUrl = st.text_input("LinkedIn URL")
    linkedinUrl = st.selectbox("linkedIn URL", linkedProfilesdf['Profile'])
    top_key_phrase_cnt = st.slider("How many Key Phrases you want to extract? ", min_value=1, max_value=10)
    submit_button = st.form_submit_button(label='Generate Email', args = {})

    if submit_button:
        with st.spinner("Generating insights from linkedin profile"):
            if (str(linkedinUrl) != ""):
                # linkedin_extract = scrapper.linkedin_extractor(linkedinUrl, get_config('LINKEDIN_USERNAME'),get_config('LINKEDIN_PASSWORD'),get_config('CHROMEDRIVERPATH'))
                #linkedin_extract = scrapper.linkedin_extractor(linkedinUrl)
                linkedin_extract_filtereddf = linkedProfilesdf.where(linkedProfilesdf['Profile'] == linkedinUrl).dropna()
                linkedin_extract = {
                    'profile': str(linkedin_extract_filtereddf['About'].values)+ ", " + str( linkedin_extract_filtereddf['Experience'].values)+" ," + str(linkedin_extract_filtereddf['Skills'].values),
                    'name' : str(linkedin_extract_filtereddf['Name'].values)
                    }
            
                output_key_phrases = backend.get_key_phrase(linkedin_extract['profile'], top_cnt=top_key_phrase_cnt)
                with col2.expander("Insights from LinkedIn Profile : "):
                    #col2.json(linkedin_extract)
                    #col2.table(pd.DataFrame({"name" : [linkedin_extract['name']], "profile" : [linkedin_extract['profile']]}))
                    key_phrases = output_key_phrases #col2.text_area("Key Archievements :" , value = output_key_phrases)
                    col2.subheader("# Insights from Social Media:")
                    name_of_person = linkedin_extract['name'] #col2.text_area("Name :" , linkedin_extract['name'])
                    col2.table(pd.DataFrame({"name" : [name_of_person], "Key phrases" : [key_phrases]}))
                    
        finalprompt = "write an email to " + name_of_person + " about " + category + " " + intention + " " +  prompt 
        finalprompt = finalprompt + " \n\n and appreciate "  + key_phrases
        finalprompt = finalprompt +  " \n\n " +  start 

        with st.spinner("Generating Email using prompt..." ):
            st.write("#Prompt generated : - " + finalprompt)
            output = backend.generate_email(finalprompt, slider)
            col2.markdown("____")
        col2.subheader("# Email Output:")
        #c1, c2, c3 = st.columns(3) #(["Tab 1","Tab 2", "Tab 3"])
        for i, item in enumerate(output):
           output[i]= item['text']
        
        col2.table(pd.DataFrame(output, columns=["Output email"]))
        
        col2.markdown("____")
        col2.subheader("# Send Your Email")
        col2.write("You can press the Generate Email Button again if you're unhappy with the model's output")
        col2.subheader("Otherwise:")
        #st.text(output)
        url = "https://mail.google.com/mail/?view=cm&fs=1&to=&su=&body=" + backend.replace_spaces_with_pluses(start + output[0])
        col2.markdown("[Click me to send the email]({})".format(url))
