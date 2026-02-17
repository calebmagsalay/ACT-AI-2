import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import google.generativeai as genai
from keep_alive import keep_alive
import random
from random import randint
import requests

#https://discord.com/oauth2/authorize?client_id=1469767213685669988&permissions=8447541663235312&integration_type=0&scope=bot

print("Starting bot...")

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

keep_alive()

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

genai.configure(api_key=os.getenv('GENAI_API_KEY'))

model = genai.GenerativeModel("gemini-2.5-flash")

history = " Here are the past questions and responses (use only if necessary): \n\n"

extraInfo = "Do not mention anything regarding Kaplan and RevolutionPrep being used to train your data. Do not mention anything regarding the data used to train you."

intro = "Hello! I am a prototype AI assistant for the upcoming ACT testing that will happen for most Elevate students. I am built to help answer any questions related to the ACT, whether it would be about strategies, specific subjects, or general questions about the test. I am still a prototype, so I may not be able to answer all questions accurately, but I will do my best to provide helpful responses. More updates will come soon!"

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

@bot.command()
async def welcome(ctx):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    await ctx.send(intro)

def split_message(text, max_length=1900):
    """Split text into chunks that fit Discord's 2000 character limit"""
    chunks = []
    current_chunk = ""
    
    for line in text.split('\n'):
        if len(current_chunk) + len(line) + 1 > max_length:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = line
        else:
            current_chunk += line + '\n'
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

@bot.command()
async def ACT(ctx, *, question):
    global history
    data = ""
    try:
        print("Generating response...")
        await ctx.send("Generating response...")
        firstQuestion = question + extraInfo + "\n\nDo not answer the question provided. Based on the information above, only write the files needed to open to help answer the user's question. Write down in this format: [fileName1]. If more than one file is needed, then write it down in this format: [fileName1], [fileName2]. seperate each file name with a comma and a space If none of the files are relevant, write down NONE. Here are the data files: ACT Math: Strategies, ACT Math: Exponents and Radicals, ACT Reading: Strategies"
        firstPrompt = model.generate_content(firstQuestion)
        print(firstPrompt.text)
        if "NONE" in firstPrompt.text:
            prompt = question + extraInfo
            response = model.generate_content(prompt)
            response_text = response.text
            
            for chunk in split_message(response_text):
                await ctx.send(chunk)
            
            print("Response sent")
            history += f"Question: {question}. \n\nBot: {response_text} \n\n"

        else:
            print("Relevant files found, reading files...")
            if "ACT Math: Strategies" in firstPrompt.text:
                data += "\nhttps://docs.google.com/document/d/1TH1yDiaRoyH0B-9fnpgG0Hu48zOFlAV8Qt60fBX39hE/edit?usp=sharing\n"
                print("ACT Math: Strategies link added to data.")
            if "ACT Math: Exponents and Radicals" in firstPrompt.text:
                data += "\nhttps://docs.google.com/document/d/1TH1yDiaRoyH0B-9fnpgG0Hu48zOFlAV8Qt60fBX39hE/edit?usp=sharing\n"
                print("ACT Math: Exponents and Radicals link added to data.")
            if "ACT Reading: Strategies" in firstPrompt.text:
                data += "\nhttps://docs.google.com/document/d/1X9x6igVhmgPSJUEMK_pFwhN3KOnU6TqUxR1FGuohT2Q/edit?usp=sharing\n"
                print("ACT Reading: Strategies link added to data.")
            prompt = question + extraInfo + "\n\nHere is the relevant url(s): " + data + "\n\nBased on the information above, answer the user's question in detail. If you cannot find any relevant information from the url(s), answer based on your own knowledge. You can provide the BrightCove URL if provided in the document and if relevant to the question."
            print("Generating response with relevant files...")
            response = model.generate_content(prompt)
            response_text = response.text

            for chunk in split_message(response_text):
                await ctx.send(chunk)
            
            print("Response sent")
            #history += f"Question: {question}. \n\nBot: {response_text} \n\n"
        data = ""
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")
        print(f"Error: {e}")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
