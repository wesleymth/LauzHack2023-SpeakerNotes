import openai

def generate_response(prompt):

    # Need to create a file keys.txt with your OpenAI_key in it
    try:
        with open('keys.txt', 'r') as file:
            openai_key = file.read()
    except Exception as e:
            print(e)

    openai.api_key = openai_key

    messag=[{"role": "system", "content": "You are a chatbot"}]
    
    ## build a chat history: you can CONDITION the bot on the style of replies you want to see - also getting weird behaviors... such as KanyeGPT
    history_bot = ["Yes, I'm ready, I will only output the notes in bullet-points asked based only on the first text (and removing information that is already explain in the second text), without saying that it cames from the frist text."]
    
    # ask ChatGPT to return STRUCTURED, parsable answers that you can extract easily - often better providing examples of desired behavior (1-2 example often enough)
    history_user = ["I'll give you two texts for each(i.e., for each of my messages) you will take notes based on the first one wihtout repeating information that can be found in the second one. If the second has information that you explain in the summary, you can remove it from the notes. \n\nfor example:\nmy input = First Text:  I have a background in computer vision, so I played a lot with mobile apps and previous hackathon challenges. I missed there. Previous hackathon challenges used to be around computer vision. You can do a lot of cool stuff with them. You can still do them today, but surprise, you don't have to do them manually. You can just ask the API to do it for you. \n Second Text: ['##ch_internal##', 'DOCUMENT UNDERSTANDING•Classification•Field extraction (OCR + HWR)•Semantic understanding•Process automation•Videos are also documents!•Your class notes are also docs!'] \n\n your output = -Author's background: Computer vision expertise. \n -Experience with mobile apps and hackathon challenges. \n -Evolution of hackathon challenges: Shift from manual tasks to API automation. \n -Emphasis on the continued relevance of computer vision in hackathons. \nready to start?"]
    
    for user_message, bot_message in zip(history_user, history_bot):
        messag.append({"role": "user", "content": str(user_message)})
        messag.append({"role": "system", "content": str(bot_message)})
    messag.append({"role": "user", "content": str(prompt)})

    response = openai.ChatCompletion.create(
        
    # please use gtp3.5 although gpt4 is much better for $$
    model="gpt-3.5-turbo",
        messages=messag,
        temperature=0,
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content
    history_bot.append(result)
    history_user.append(str(prompt))
    
    return result