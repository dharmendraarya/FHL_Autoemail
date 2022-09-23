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
col1 , col2 = st.columns(spec = [100,80])
col1.header("Hyperpersonalize Email Generator App")

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
        'category': ["Sales", "Sales", "Sales","Recruitment", "Recruitment","Recruitment", "Customer Support", "Others"],
        'Intention' :["Trial offer", "Meeting request","reply", "Initial", "reminder", "reply", "asking customer to respond","Others"],
    }
)

# text = st.text_area('text')
# text_placeholder = st.empty()
#st.session_state.promptvalue =""

is_debug = get_config('debug')

def modify_prompt():
    #st.session_state.promptvalue =  f"write {tone} {intention} email"
    if (category=="Recruitment"):
        if (intention == "Initial"):
            st.session_state.promptvalue = f"write {tone} email to {{candidate}} about {{role}} opening at {{contoso.com}} " 
        elif(intention == "reminder"):
            st.session_state.promptvalue = f"write  {tone} {intention} email to {{candidate}} to respond on preceding email " 
            st.session_state.precedingemail = f"Hello candidate, We are excited to let you know that we have a {{position}} open at {{contoso.com}}. This is a great opportunity for someone with your skills and background. The position will involve working with large data sets to find trends and insights that can help improve our products and services. If you are interested in this position, please send your resume to {{email address}}. Thank you for your time and we look forward to hearing from you. "
        elif(intention == "reply"):
            st.session_state.promptvalue = f"write  {tone} {intention} email to {{candidate}} on preceding email and use guidance from keypoints to respond.\n {{keypoints}} = role description , meeting calendar link " 
            st.session_state.precedingemail = f"Hello, I am interested in opportunity and need more information before I apply. please suggest Thanks, {{candidate Name}}"
        else :
            st.session_state.promptvalue =  f"write {tone} {intention} email"
    elif(category=="Sales"):
        if (intention == "Trial offer"):
            st.session_state.promptvalue = f"write {tone} {category} email from {{companyName}} about product [{productname}] and its benefits [{productdescription}]. 30 day trial" 
        elif (intention == "Meeting request"):
            st.session_state.promptvalue = f"write {intention} email with {tone} tone to {{customer}} from {{companyName}} about product [{productname}] and its benefits [{productdescription}]. Great to see your experience in {{keyskills}}" 
        elif (intention == "reply"):
            st.session_state.promptvalue = f"write {tone} {intention} email from {{preceding email}} about product [{productname}] and its benefits [{productdescription}]" 
            st.session_state.precedingemail = f"Hi {{companyName}}, I am interested in this product. However, I am not sure. Thank you  {{candidate Name}}"     
        else :
            st.session_state.promptvalue =  f"write {tone} {intention} email"
    elif(category=="Customer Support"):
        if (intention == "asking customer to respond"):
            st.session_state.promptvalue = f"write {tone} {intention} email to {{Customer}} asking to respond on preceding email" 
            #st.session_state.precedingemail = f"Greetings from Azure!Thank you for contacting Microsoft support. My name is {{support executive}}, and I am the Support Engineer who will be working with you on this Service Request. You may reach me using the contact information listed below, referencing the SR number #0000000.I understand that you need assistance with Quota request for Compute VM for DSv1 Series (XIO) to limit 21 in US West 2 (WUS2) region on your subscription id: 00-0000-0000-0000.As per your request I have engaged our capacity management team to review the request. And here is an update from our team:Requested prev generation sku is not available in requested region. Attaching the link Azure Products by Region | Microsoft Azure for your reference to check the available sku's in requested region.I can see your preferred contact method is phone, since it is not Business hour in your location, I have sent above email with the information on your requests.To assist you better, please let us know whether you comfortable with further communication on email. Or you require phone call.Awaiting your response. regards - {{support executive}}"
    else:
        st.session_state.promptvalue =  f"write {tone} email to {{person}} about {{appraisal discussion}}"

linkedProfilesdf = pd.read_csv(get_config('JSONPROFILEDATAPATH') +'linkedProfiles.csv')
category = st.sidebar.radio("Choose email Outreach category", metaDatadf['category'].unique(), index=1) #,on_change = modify_prompt)
intention = st.sidebar.selectbox("Intention", metaDatadf.where(metaDatadf['category'] == category)['Intention'].dropna().unique()) #, on_change = modify_prompt)


#typeofemail = st.sidebar.selectbox("Type of email", options = ["Initial", "reply"])
#template = st.sidebar.radio("choose template", )
#prompttext = st.text_area("test", f"category -{category} Intention -{intention}")
st.sidebar.markdown("_________")
language = st.sidebar.selectbox("Choose language", options = ["English"])
tone = st.sidebar.selectbox("Select tone", options = ["Assertive", "Cold","Appreciative","Funny"], index=1)
if (category == "Sales") :
    #with st.expander("Product Detail : ") :
    st.sidebar.markdown("_________")
    productname = st.sidebar.text_input("Enter Product Name", on_change= modify_prompt, value = "DeeDee", help ='Add productname to be used in email')
    productdescription = st.sidebar.text_input("Enter Product description",value = "Hyperpersonalize email writing", help ='Add main benefits/ offering about product')

# prompt = st.text_area("Describe the Kind of email you want to be written.", value= "", height=100)
# st.text(f"(Example: Data science opening at Contoso.com)")
modify_prompt()


with col1.form(key="form"):
   
    if 'promptvalue' not in st.session_state:
        st.session_state.promptvalue = modify_prompt()

    if 'precedingemail' not in st.session_state:
        st.session_state.precedingemail =""

    prompt = st.text_area("Describe the kind of email you want to be written?", value= st.session_state.promptvalue, height=100, help = " It's editable box, add detail about what kind of email you write. Example: write email to boss about appraisal followup")
    #st.text(f"(Example: Data science opening at Contoso.com)")

    if ("reply" in intention or 'reminder' in intention):
        precedingemail = st.text_area("Previous email:", value=st.session_state.precedingemail , height =150)

    slider = st.slider("How many characters do you want your email to be? ", min_value=64, max_value=750, value = 140)
    # st.text("(A typical email is usually 100-500 characters)")
    
    key_phrases = ""
    name_of_person = ""

    IsLinkedFeed = st.sidebar.radio("Do you want to personalize your email with Insights from social feeds?", options = ["Yes", "No"], index=1) 
    if (IsLinkedFeed == "Yes"):
        with st.sidebar.expander("Personalization Section: ", expanded = True) :
            linkedinUrl = st.selectbox("linkedIn URL", linkedProfilesdf['Profile'], index=0, help = "its restricted to selected profile only, until background job is sorted to get the scrapped Data for any linkedIn profile")
            top_key_phrase_cnt = st.slider("How many Key phrases you want to extract from linkedIn profile? ", min_value=1, max_value=10, value=2)

    with st.sidebar.expander("Advance Settings :") :
        creativity = st.slider("Choose to creatvitity Level? ", min_value=0.0, max_value=1.0, value=0.5)
        emailVariants = st.selectbox("No of email variants", options= [1,2,3], index=2)
        frequencyPenalty = st.slider("Repeation Penalty? ", min_value=0.0, max_value=1.0, value=0.0)

    submit_button = st.form_submit_button(label='Generate Email', args = {})

    if submit_button:
        with st.spinner("Generating insights from linkedin profile"):
            if (IsLinkedFeed == "Yes"):
                if (str(linkedinUrl) != "Select" ):
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
                        if is_debug :
                            col2.table(pd.DataFrame({"name" : [name_of_person], "Key phrases" : [key_phrases]}))

        #sample prompt # 1: Write an email to candidate about Data science opening at PinkiWriter   
        # Write an email to candidate about Data science opening at PinkiWriter and appreciate leadership role at Torus insurance award of IT honor         
        # write response email to preceding email from candidate and use guidance from keypoints to respond.            
        # finalprompt = "write " + tone +" " + intention + " email "
        # if (prompt != ""):
        #     finalprompt =  finalprompt + " about " +  prompt  

        finalprompt = prompt
        if (("reminder" in intention or "reply" in intention) and precedingemail != ""):
            finalprompt =  f"{finalprompt}  \n {{preceding email}}: {precedingemail}" 

        if (IsLinkedFeed == "Yes" and key_phrases !=""):
            if (name_of_person != ""):
                finalprompt = f"{finalprompt} \n {{To}} : {name_of_person}"
            finalprompt = f"{finalprompt} \n {{Expertize on}} :{key_phrases} "
        
        # if(productname != ""):
        #     finalprompt = f"{finalprompt}   productName: {productname} "
        # if(productdescription != ""):
        #     finalprompt = f"{finalprompt}   productdescription:  {productdescription} "
        
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
            if (is_debug):
                st.text_area("#Prompt generated :" , finalprompt)
            output = backend.generate_email(finalprompt, slider,creativity,emailVariants,frequencyPenalty)
            
        col2.subheader("Generated Emails:")
        #c1, c2, c3 = st.columns(3) #(["Tab 1","Tab 2", "Tab 3"])
        
        col2.write("You can press the Generate Email Button again if you're unhappy with the model's output")
        for i, item in enumerate(output):
           j = i+1       
           if (j>2):
            col1.markdown("[Click to send the email - {}]({})".format(str(j),"https://mail.google.com/mail/?view=cm&fs=1&to=&su=&body=" + backend.replace_spaces_with_pluses(col1.text_area("Email-" + str(j),  item['text'].strip(), height =400))))
           else:
            col2.markdown("[Click to send the email - {}]({})".format(str(j),"https://mail.google.com/mail/?view=cm&fs=1&to=&su=&body=" + backend.replace_spaces_with_pluses(col2.text_area("Email - " + str(j),  item['text'].strip(), height =400))))
           
           #send_button = col2.form(key=str(i)).form_submit_button(label='Generate Email', args = {})
        
        #col2.table(pd.DataFrame(output, columns=["Output email"]))
        
        #col2.markdown("____")
    
        #col1.subheader("# Send Your Email")
        #col1.write("You can press the Generate Email Button again if you're unhappy with the model's output")
        #col1.subheader("Otherwise:")
        #st.text(output)
        #selectoutput = col1.radio("Choose the emails you want to send " , options = range(emailVariants))
        #url = "https://mail.google.com/mail/?view=cm&fs=1&to=&su=&body=" + backend.replace_spaces_with_pluses( output[selectoutput-1])
        #col1.markdown("[Click me to send the email]({})".format(url))
