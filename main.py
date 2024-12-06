from datetime import datetime
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import wolframalpha
import sys

# Speech engine initialization
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 0 is male and 1 is female
activationWord = 'atlas'  # Activation word to trigger listening
useSpeach = False  # Global flag to switch between speech and text mode

# Set the path for Chrome to open URLs
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))  # Configure browser

# WolframAlpha API Client Initialization
appId = "your_api_key"
wolframClient = wolframalpha.Client(appId)

def setToSpeach():
    global useSpeach
    useSpeach = True
    speak("Switching to speech mode.")

def setToText():
    global useSpeach
    useSpeach = False
    speak("Switching to text mode.")

def speak(text, rate = 120):
    engine.setProperty('rate',rate)
    engine.say(text)
    engine.runAndWait()

def parseCommand():
    listener = sr.Recognizer()
    if useSpeach== True:
        print('Listening for a command...')
        attempts = 3
        for _ in range(attempts):
            with sr.Microphone() as source:
                print("Adjusting for background noise... Please wait.")
                listener.adjust_for_ambient_noise(source, duration=2)
                try:
                    print("Listening...")
                    command = listener.listen(source, timeout=5)  # Adjust timeout for more flexibility
                    command_text = listener.recognize_google(command)
                    print(f"Command received: {command_text}")
                    return command_text.lower()  # Return the recognized command
                except sr.UnknownValueError:
                    speak("Sorry, I couldn't understand that. Please try again.")
                except sr.RequestError:
                    speak("Sorry, I'm having trouble connecting to the speech service.")
                except Exception as e:
                    speak(f"An error occurred: {e}")
        speak("I couldn't understand your command after multiple attempts. Please try again later.")
        return None # Return None if all attempts fail
    else: 
        speak("Text mode is currently enabled. Please type your command.")
        return input("Please enter your command: ").lower()  # Fallback to text input mode

def listOrDict(var):
    if isinstance(var, list):
        return var[0]['pliantext']
    else:
        return var['plaintext']

def search_wikipidia(query = ''):
    try:
        result = wikipedia.summary(query, sentences=1)
        return result
    except wikipedia.exceptions.DisambiguationError as e:
        result = (f"There are multiple results for {query}, please be more specific")
        return result
    except:
        return ("Sorry, there was an error connecting to Wikipedia.")

def search_wolframAplha(query = ''):
    try:
        response = wolframClient.query(query)

        # @success: Wolfram Alpha was able to selove the query
        # @numpods: number of results returned
        # pod: List of results. This can also contain subpods
        if response['@success'] == 'false':
            return 'Could not compute'
        
        # Query resolved
        else:
            result = ''
            speak("Please wait")
            # Question
            pod0 = response['pod'][0]

            pod1 = response['pod'][1]
            # May contain the answer, has the highest confidence value
            # if it's primary, or has the title of result or definition, then it's the official result
            if (('result') in pod1['@title'].lower()) or (pod1.get('@primary', 'false') == 'true') or ('definition' in pod1['@title'].lower()):
                # Get the result
                result = listOrDict(pod1['subpod'])
                # Remove the bracketed section
                return result.split('(')[0]
            else:
                question = listOrDict(pod0['subpod'])
                #Remove the bracketed section
                asked= question.split('(')[0]
                #Search wikipedia instead
                speak('Computation failed. Querying univeral databank.')
                search_wikipidia(asked)
                return question.split('(')[0]
    except:
        return None

def processCommand(query= ''):
    if query:
        #switch input mode
        if 'switch' in query:
            if 'text' in query:
                setToText()
            elif 'speach' in query :
                setToSpeach()
        #Greeting
        elif query[0] == 'say':
            if query[1] == 'hello':
                speak('Greetings, all.')
            else:
                query.pop(0) # Remove say
                speech = ' '.join(query)
                speak(speech)

        # Open website
        elif ((query[0] == 'go')and(query[1] =='to')):
                speak('Opening...')
                query = ' '.join(query[2:])
                try:
                    webbrowser.get('chrome').open_new(query)
                except:
                    print("URL Not found")
                    speak("Couldn't find URL in universal database")
        elif (query[0] =='open'):
            speak('Opening...')
            query = ' '.join(query[1:])
            try:
                    webbrowser.get('chrome').open_new(query)
            except:
                    print("URL Not found")
                    speak("Couldn't find URL in universal database")

        #Wikipedia
        elif 'wikipedia' in query and (query.index('for') > query.index('wikipedia')):
                search = ' '.join(query[query.index('for')+1:])
                speak('Querying the universal databank.')
                webbrowser.get('chrome').open_new(f"https://en.wikipedia.org/wiki/{search}")
                result = search_wikipidia(search)
                speak(result)

        #Wolframe Alpha 
        elif query[0] =='compute':
            query = " ".join(query[1:])
            print(query)
            print('Computing...')
            speak('Computing...')
            try:
                result = search_wolframAplha(query)
                speak(result)
            except:
                print('Unable to compute')
                speak("Unable to compute")

        #Note taking
        elif query[0] == 'log':
            speak('Ready to record your note')
            newNote = parseCommand().lower()
            now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            with open(f'note_%s.txt' % now, 'w') as newFile:
                newFile.write(newNote)
            speak('Note written')
    return None

#Main loop 
if __name__ == '__main__':
    speak('All systems nominal.')
    print("Begin all commands with thge activation key")
    print('Current cammand list includes:')
    print("Greeting (Command: 'Say Hello')")
    print("Repitition (Command: 'Say...' followed by what's to be repeated)")
    print("Google url search (Command: 'Go to example.com' or 'Open example.com')")
    print("Query universal Database (Command: 'Search Wikipedia for...' followed by search specific search subject e.g. Search for Python programming language)")
    print("Answer any question (Command: 'Compute...' followed by query)")
    print("Make and save logs (Command: 'log' then enter or say what needs to be logged)")
    print("To exit simply say exit")
    while True:
        #Parse Command as list
        query = parseCommand().lower().split()
        print(query)
        
        if query[0] == activationWord:
            query.pop(0)
            #List of commands
            print(query)
            processCommand(query)
        #If user wants to stop Assistant
        elif 'exit' in query:
            if query[0] == 'exit' or query.index('exit')==1:
                speak('Goodbye')
                break 