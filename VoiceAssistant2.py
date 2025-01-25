import os
import openai
import pyttsx3
import speech_recognition as sr
import pywhatkit
import datetime
import wikipedia
import requests

# Initialize the speech engine
engine = pyttsx3.init()
listener = sr.Recognizer()


voices = engine.getProperty('voices')
for voice in voices:
    if "female" in voice.name.lower() or "Ember" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

# Set speaking rate for a natural tone
engine.setProperty('rate', 175)

# Function to make the assistant speak
def talk(text):
    engine.say(text)
    engine.runAndWait()

# Functions take user commands via microphone
def input_command():
    try:
        with sr.Microphone() as source:
            print("Listening...")
            listener.adjust_for_ambient_noise(source)
            voice = listener.listen(source, timeout=15)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'ember' in command:
                command = command.replace('ember', '').strip()
            return command
    except sr.WaitTimeoutError:
        talk("You seem busy. I'll exit for now. Have a great day!")
        exit()
    except Exception as e:
        return ""

# weather updates functions
def get_weather(city):
    api_key = "your_openweather_api_key"  # Replace with your OpenWeather API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            weather = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            talk(f"The weather in {city} is {weather} with a temperature of {temperature} degrees Celsius.")
        else:
            talk("Sorry, I couldn't find weather details for that location.")
    except Exception as e:
        talk("I couldn't fetch the weather. Please try again later.")

# fetch news updates functions
def get_news():
    api_key = "your_news_api_key"  # Replace with your News API key
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
    try:
        response = requests.get(url)
        articles = response.json().get("articles", [])[:5]
        if articles:
            talk("Here are the top news headlines:")
            for article in articles:
                talk(article["title"])
        else:
            talk("Sorry, I couldn't fetch the news right now.")
    except Exception as e:
        talk("I encountered an issue while fetching the news.")

#integrate OpenAI's GPT API
def ask_gpt(question):
    openai.api_key = "your_openai_api_key"  # Replace with your OpenAI API key
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=question,
            max_tokens=150
        )
        answer = response.choices[0].text.strip()
        talk(answer)
    except Exception as e:
        talk("I couldn't fetch a response from GPT. Please try again later.")

# Core function to handle commands
def play_Ember():
    talk("Hello, I'm Ember, your friendly assistant. How can I help you today?")
    while True:
        command = input_command()
        if not command:
            talk("I didn't catch that. Could you please repeat?")
            continue

        if "play" in command:
            song = command.replace('play', '').strip()
            talk(f"Playing {song} on YouTube.")
            pywhatkit.playonyt(song)
        elif "time" in command:
            time = datetime.datetime.now().strftime('%I:%M %p')
            talk(f"The current time is {time}.")
        elif "date" in command:
            date = datetime.datetime.now().strftime('%A, %d %B %Y')
            talk(f"Today's date is {date}.")
        elif "weather" in command:
            talk("Please tell me the city name.")
            city = input_command()
            get_weather(city)
        elif "news" in command:
            get_news()
        elif "who is" in command:
            person = command.replace('who is', '').strip()
            info = wikipedia.summary(person, sentences=2)
            talk(info)
        elif "what is" in command or "tell me about" in command:
            ask_gpt(command)
        elif "stop" in command or "exit" in command:
            talk("Goodbye! Have a great day.")
            break
        else:
            talk("I'm not sure how to help with that. Could you rephrase?")

# Run the assistant
play_Ember()
