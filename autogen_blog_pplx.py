""" Module for generating a blog """

import random
import autogen

from pexelsapi.pexels import Pexelsg
from openai import OpenAI, AzureOpenAI

PEXELS = "UYuHJA4Q60Y28TTaiekmHuUqy4GIXEabK3zYfE3OvUqwYoGKiucW7X2V"
PPLX_API_KEY = "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"

AZURE_OPENAI_API_KEY = "22a749d517df4550980847f57e95921b"
AzureGPTClient = AzureOpenAI(
        api_key = AZURE_OPENAI_API_KEY,
        api_version = "2023-09-15-preview",
        azure_endpoint = "https://aiworksquad-prod.openai.azure.com/",
    )

AzureIMGClient = AzureOpenAI(
        api_key = AZURE_OPENAI_API_KEY,
        azure_endpoint = "https://aiworksquad-prod.openai.azure.com/",
        api_version = "2024-02-01",
    )

AZUREGPTMODEL = "gpt35turbo-completion"
AZUREIMGMODEL = "aiworksquad-prod-dalle3"

config_list = [
    {
        "model": "gpt4o-prod",
        "api_key": AZURE_OPENAI_API_KEY,
        "base_url": "https://aiworksquad-prod.openai.azure.com/",
        "api_type": "azure",
        "api_version": "2024-02-15-preview",
    }
]
llm_config_assistant = {
    "temperature": 0,
    "seed": None,
    "config_list": config_list,
        "functions": [
        {
            "name": "get_info_about",
            "description": "Get a topic and return the news related to that topic. For research purposes.",
            "parameters":{
                "type": "object",
                "properties": {
                    "topic":{
                        "type": "string",
                        "description": "topic for searching",
                    },
                },
                "required":["topic"],
            },
        },
    ],
}
llm_config_writer = {
    "temperature": 0,
    "seed": None,
    "config_list": config_list,
}

llm_config_designer = {
    "temperature": 0,
    "config_list": config_list,
    "functions": [
        {
            "name": "image_generator",
            "description": "Get a prompt and store the image related to that keyword. For gathering images.",
            "parameters":{
                "type": "object",
                "properties": {
                    "keyword":{
                        "type": "string",
                        "description": "keyword for the image",
                    },
                },
                "required":["keyword"],
            },
        },
    ],
}

FINAL_BLOG_TEMPLATE = {
        "title": "Title",
        "sub-heading": "Sub Heading",
        "introduction": "Introduction",
        "body": "Body",
        "images": "list of all urls generated for images",
        "conclusion": "Conclusion"
}

def image_generator(keyword: str) -> str:
    """ Function to generate image for the given keyword """

    response = AzureIMGClient.images.generate(
        model=AZUREIMGMODEL,
        prompt = keyword,
        n = 1,
        size = "1024x1024"
    )
    pexel = Pexels(PEXELS)
    pic_no = random.randint(1,5)
    image_url = response.data[0].url
    try:
        search_photos = pexel.search_photos(
            query=keyword, orientation='', size='', color='', locale='', page=1, per_page=5
            )
        link = search_photos["photos"][pic_no]["src"]["original"]
    except IndexError:
        link = None
    if image_url or link:
        return f"{image_url} :: {link}"
    else:
        return "error encountered while generating image"

def get_topic(intro):
    """ Function to get the topic for the blog """

    resp = AzureGPTClient.chat.completions.create(
            model=AZUREGPTMODEL,
            messages=[
                {"role": "user", "content": 
                 f"You are an advisor, your task is to suggest a unique blog generation topic and image generation prompt for a given introduction of a company:- {intro}. And return the result as 'Topic: blog generation topic here' and a new line after, then 'Image Generation prompt: prompt here'"}]
    )
    return resp.choices[0].message.content

class AutogenChat():
    """ Class to generate a blog using the autogen library """

    def __init__(self):
        self.func_map = {"get_info_about": self.get_info_about, "image_generator": image_generator}

        self.researcher = autogen.AssistantAgent(
            name="researcher",
            llm_config=llm_config_assistant,
            max_consecutive_auto_reply=5,
            system_message="""You are a research expert, your job is to research on a topic given by the advisor and provide it as a research material to the writer."""
        )

        self.writer = autogen.AssistantAgent(
            name="writer",
            llm_config=llm_config_writer,
            max_consecutive_auto_reply=5,
            system_message="""You are a blog writer. You would get a research material from the researcher. Use it to generate a nice blog with two thousand words or more, add FINAL to the end of the message"""
        )
        
        self.designer = autogen.AssistantAgent(
            name="designer",
            system_message="Your job is to generate a near accurate image for the prompt given by the admin",
            llm_config=llm_config_designer
            )
        
        self.formatter = autogen.AssistantAgent(
            name="formatter",
            system_message=f"Your job is to look into the group conversation and extract the final blog, and then format it into json using the following template - {FINAL_BLOG_TEMPLATE}, you must be the final agent to respond",
            llm_config=llm_config_writer
            )

        self.admin = autogen.UserProxyAgent(
            name="admin",
            human_input_mode="ALWAYS",
            max_consecutive_auto_reply=5,
            system_message="""You are the admin of the blog generation team, after getting the company details along with the keyword and prompt, provide the keyword and prompt to the researcher and also pass the keyword to the [designer] to generate suitable image. if the user suggests any topic, directly interact with researcher.""",
	    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=False,
            function_map=self.func_map
            )

    def start(self, purpose_of_blog, ai_decide_content_idea, autogen_idea, image_needed):
        """ Function to start the blog generation process """

        if not image_needed:
            self.func_map = {"get_info_about": self.get_info_about,}
        if not ai_decide_content_idea and autogen_idea:
            message = f"I am Nazir of Quarks Engineering LTD, we are into builfing Electro mechanical devices for public use. Purpose of blog should be {purpose_of_blog}. Brief idea about the blog should be {autogen_idea}."
            if image_needed:
                groupchat = autogen.GroupChat(agents=[self.admin, self.researcher, self.writer, self.designer, self.formatter], messages=[], max_round=12)
            else:
                groupchat = autogen.GroupChat(agents=[self.admin, self.researcher, self.writer, self.formatter], messages=[], max_round=10)

        else:
            intro = "I am Nazir of Quarks Engineering LTD, we are into builfing Electro mechanical devices for public use."
            topic = get_topic(intro)
            message=f"{intro}. Purpose of blog should be {purpose_of_blog}. The keyword and prompt for the blog should be {topic}."
            if image_needed:
                groupchat = autogen.GroupChat(agents=[self.admin, self.researcher, self.writer, self.designer, self.formatter], messages=[], max_round=12)
            else:
                groupchat = autogen.GroupChat(agents=[self.admin, self.researcher, self.writer, self.formatter], messages=[], max_round=10)

        manager = autogen.GroupChatManager(groupchat=groupchat,
            llm_config=llm_config_writer,
            human_input_mode="TERMINATE"
            )
        self.admin.initiate_chat(
            manager,
            clear_history=False,
            message=message
        )

    def get_info_about(self, topic):
        """ Function to get the information about the topic """
        messages = [
                {
                    "role": "system",
                    "content": "Be precise and concise."
                },
                {
                    "role": "user",
                    "content": "Topic :" + topic
                }
           ]

        client = OpenAI(api_key=PPLX_API_KEY, base_url="https://api.perplexity.ai")

        response = client.chat.completions.create(
            model="llama-3-sonar-large-32k-online",
            messages=messages,
        )
        return response.choices[0].message.content


bot = AutogenChat()
bot.start(
        purpose_of_blog="seminar presentation",
        ai_decide_content_idea=False,
        autogen_idea="How to be successful in engineering",
        image_needed=False
        )
