from datetime import datetime
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import wolframalpha

#Speech engine initialization
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice',voices[0].id) # 0 is male and 1 is for female
activationWord = 'atlas' #Single word

# Configure browser
# Set the path
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))


def speak(text, rate = 120):
    engine.setProperty('rate',rate)
    engine.say(text)
    engine.runAndWait()

def parseCommand():
    listener = sr.Recognizer()
    print('Listening for a command')

    with sr.Microphone() as source:
        listener.pause_threshold = 2
        input_speech  = listener.listen(source)

    try:
        print('Recognizing speech...')
        query = listener.recognize_google(input_speech, language='en_gb')
        print(f'The input speech was: {query}')
    except Exception as exception:
        print('I did not quite catch that')
        speak('I did not quite catch that')
        print(exception)
        return 'None'
    return query

def search_wikipidia(query = ''):
    searchResults = wikipedia.search(query)
    if not searchResults:
        print('No wikipedia result')
        return 'No reult recieved'
    try:
        wikiPage = wikipedia.page(searchResults[0])
    except wikipedia.DisamiguationError as error:
        wikiPage = wikipedia.page(error.options[0])
    print(wikiPage.title)
    wikiSummary = str(wikiPage.summary)
    return wikiSummary

#Main loop 
if __name__ == '__main__':
    speak('All systems nominal.')

    while True:
        #Parse Command as list
        query = parseCommand().lower().split()
        print(query)
        '''query = query.pop()
        print(query)'''
        #if query[0] == activationWord:
            #List commands
        if 'say' in query:
            if 'hello' in query:
                speak('Greetings, all.')
            else:
                query.pop(0) # Remove say
                speech = ' '.join(query)
                speak(speech)

        if ('go' in query):
            if (query.index('go')<query.index('to'))and('to' in query):
                speak('Opening...')
                start_index = (query.index('to'))+1
                query = ' '.join(query[start_index:])
                webbrowser.get('chrome').open_new(query)

        #Wikipedia
        if 'wikipedia' in query:
            query = ' '.join(query[query.index('wikipedia')+1:])
            speak('Querying the universal databank.')
            webbrowser.get('chrome').open_new(f"https://en.wikipedia.org/wiki/{query}")
            result = search_wikipidia(query)
            speak(result)