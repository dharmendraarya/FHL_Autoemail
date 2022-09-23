#from turtle import back
from code import interact
from email.policy import default
from operator import index
from optparse import Option
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
        'category': ["Sales", "Sales","Recruitment", "Recruitment","Recruitment", "Customer Support"],
        'Intention' :["Initial", "reply", "Initial", "reminder", "reply", "reply"],
    }
)

# text = st.text_area('text')
# text_placeholder = st.empty()
#st.session_state.promptvalue =""


def modify_prompt():
    #st.session_state.promptvalue =  f"write {tone} {intention} email"
    if (category=="Recruitment"):
        if (intention == "Initial"):
            st.session_state.promptvalue = f"write an {tone} {intention} email to candidate about [Data science manager] opening at [contoso.com] " 
        elif(intention == "reminder"):
            st.session_state.promptvalue = f"write a {tone} {intention} email to candidate to respond on preceding email " 
        elif(intention == "reply"):
            st.session_state.promptvalue = f"write a {tone} {intention} email to preceding email from [candidate]" 
        else :
            st.session_state.promptvalue =  f"write {tone} {intention} email"
    elif(category=="Sales"):
        if (intention == "Initial"):
            st.session_state.promptvalue = f"write an {tone} {intention} email and from bullet points, companyName - [companyName] , [[bullet points:]] =[Offerings - high end analytics solution - Benefits - lower cost, improve profitability with the template implementations]" 
        elif (intention == "reply"):
            st.session_state.promptvalue = f"write an {tone} {intention} email from preceding email and from  [[bullet points:]] =[Offerings - high end analytics solution - Benefits - lower cost, improve profitability with the template implementations]" 
        else :
            st.session_state.promptvalue =  f"write {tone} {intention} email"
    else:
        st.session_state.promptvalue =  f"write {tone} {intention} email"

linkedProfilesdf = pd.read_csv(get_config('JSONPROFILEDATAPATH') +'linkedProfiles.csv')
category = st.sidebar.radio("Choose email Outreach category", metaDatadf['category'].unique(), index=1) #,on_change = modify_prompt)
intention = st.sidebar.selectbox("Intention", metaDatadf.where(metaDatadf['category'] == category)['Intention'].dropna().unique()) #, on_change = modify_prompt)


#typeofemail = st.sidebar.selectbox("Type of email", options = ["Initial", "reply"])
#template = st.sidebar.radio("choose template", )
#prompttext = st.text_area("test", f"category -{category} Intention -{intention}")
st.sidebar.markdown("_________")
language = st.sidebar.selectbox("Choose language", options = ["English"])
tone = st.sidebar.selectbox("Select tone", options = ["Assertive", "Appreciative","Funny"])
if (category == "Sales") :
    #with st.expander("Product Detail : ") :
    st.sidebar.markdown("_________")
    productname = st.sidebar.text_input("Enter Product Name")
    productdescription = st.sidebar.text_input("Enter Product description")

# prompt = st.text_area("Describe the Kind of email you want to be written.", value= "", height=100)
# st.text(f"(Example: Data science opening at Contoso.com)")
modify_prompt()

col1 , col2 = st.columns(spec = [100,80])
with col1.form(key="form"):
   
    if 'promptvalue' not in st.session_state:
        st.session_state.promptvalue = modify_prompt()


    prompt = st.text_area("Describe the kind of email you want to be written.", value= st.session_state.promptvalue, height=100, help = "Example: Data science opening at Contoso.com")
    #st.text(f"(Example: Data science opening at Contoso.com)")

    if ("reply" in intention or 'reminder' in intention):
        precedingemail = st.text_area("Previous email:", value="", height =200)

    slider = st.slider("How many characters do you want your email to be? ", min_value=64, max_value=750, value = 100)
    # st.text("(A typical email is usually 100-500 characters)")
    
    key_phrases = ""
    name_of_person = ""

    IsLinkedFeed = st.sidebar.radio("Do you want to personalize your email with Insights from social feeds?", options = ["Yes", "No"], index=1) 
    with st.sidebar.expander("Personalization Section: ") :
         if (IsLinkedFeed == "Yes"):
            linkedinUrl = st.selectbox("linkedIn URL", linkedProfilesdf['Profile'], index=0)
            top_key_phrase_cnt = st.slider("How many Key Phrases you want to extract? ", min_value=1, max_value=10, value=2)

    with st.sidebar.expander("Advance Settings :") :
        creativity = st.slider("Choose to creatvitity Level? ", min_value=0.0, max_value=1.0, value=0.5)
        emailVariants = st.selectbox("No of email variants", options= [1,2,3], index=2)

    submit_button = st.form_submit_button(label='Generate Email', args = {})

    if submit_button:
        with st.spinner("Generating insights from linkedin profile"):
            if (IsLinkedFeed == "Yes"):
                if (str(linkedinUrl) != "Select" or str(linkedinUrl) != "" ):
                    # linkedin_extract = scrapper.linkedin_extractor(linkedinUrl, get_config('LINKEDIN_USERNAME'),get_config('LINKEDIN_PASSWORD'),get_config('CHROMEDRIVERPATH'))
                    #linkedin_extract = scrapper.linkedin_extractor(linkedinUrl)
                    linkedin_extract_filtereddf = linkedProfilesdf.where(linkedProfilesdf['Profile'] == linkedinUrl).dropna()
                    linkedin_extract = {
                        'profile': ' '.join(linkedin_extract_filtereddf['About'].values)+ ", " + ' '.join( linkedin_extract_filtereddf['Experience'].values)+" ," + ' '.join(linkedin_extract_filtereddf['Skills'].values),
                        'name' : ''.join(linkedin_extract_filtereddf['Name'].values)
                        }
                
                    output_key_phrases = backend.get_key_phrase(linkedin_extract['profile'], top_cnt=top_key_phrase_cnt)
                    with col2.expander("Insights from LinkedIn Profile : "):
                        #col2.json(linkedin_extract)
                        #col2.table(pd.DataFrame({"name" : [linkedin_extract['name']], "profile" : [linkedin_extract['profile']]}))
                        key_phrases = output_key_phrases #col2.text_area("Key Archievements :" , value = output_key_phrases)
                        col2.subheader("# Insights from Social Media:")
                        name_of_person = linkedin_extract['name'] #col2.text_area("Name :" , linkedin_extract['name'])
                        col2.table(pd.DataFrame({"name" : [name_of_person], "Key phrases" : [key_phrases]}))

        #sample prompt # 1: Write an email to candidate about Data science opening at PinkiWriter   
        # Write an email to candidate about Data science opening at PinkiWriter and appreciate leadership role at Torus insurance award of IT honor         
        # write response email to preceding email from candidate and use guidance from keypoints to respond.            
        # finalprompt = "write " + tone +" " + intention + " email "
        # if (prompt != ""):
        #     finalprompt =  finalprompt + " about " +  prompt  

        finalprompt = prompt
        if ("response email" in intention):
            # finalprompt = finalprompt +  " \n\n " +   " and use guidance from keypoints to respond"
            finalprompt =  f"{finalprompt}  \n [[preceding email]]: {precedingemail}" 
            # finalprompt = finalprompt + " \n [[keypoints]]: " +  prompt

        if (IsLinkedFeed == "Yes" and key_phrases !=""):
            if (name_of_person != ""):
                # finalprompt = finalprompt + " [[To]]: " + name_of_person 
                finalprompt = f"{finalprompt}  [[To]]: : {name_of_person}"
            finalprompt = f"{finalprompt}   appreciate [[experience]]:  {key_phrases} "
         

        
        #finalprompt = "write a "+ category + " " + " " + name_of_person
        # if ("Initial email" in intention):
        #     finalprompt =  finalprompt + " about " +  prompt  
        #     if (key_phrases !=""):
        #         finalprompt = finalprompt + "  and appreciate achievement in keyskills"  
        #         finalprompt = finalprompt + " \n [[keyskills]]: " +  key_phrases
        # if ("response email" in intention):
        #     finalprompt = finalprompt +  " \n\n " +   " and use guidance from keypoints to respond"
        #     finalprompt = finalprompt + " \n [[preceding email]]: " +  precedingemail
        #     finalprompt = finalprompt + " \n [[keypoints]]: " +  prompt

        with st.spinner("Generating Email using prompt..." ):
            st.text_area("#Prompt generated :" , finalprompt)
            output = backend.generate_email(finalprompt, slider,creativity,emailVariants)

        col2.subheader("# Email Output:")
        #c1, c2, c3 = st.columns(3) #(["Tab 1","Tab 2", "Tab 3"])
        for i, item in enumerate(output):
           col2.text_area("Email - " + str(i),  item['text'], height =400)
           #send_button = col2.form(key=str(i)).form_submit_button(label='Generate Email', args = {})
        
        #col2.table(pd.DataFrame(output, columns=["Output email"]))
        
        #col2.markdown("____")
    
        col1.subheader("# Send Your Email")
        col1.write("You can press the Generate Email Button again if you're unhappy with the model's output")
        col1.subheader("Otherwise:")
        #st.text(output)
        selectoutput = col1.radio("Choose the emails you want to send " , options = range(emailVariants))
        url = "https://mail.google.com/mail/?view=cm&fs=1&to=&su=&body=" + backend.replace_spaces_with_pluses( output[selectoutput-1])
        col1.markdown("[Click me to send the email]({})".format(url))
