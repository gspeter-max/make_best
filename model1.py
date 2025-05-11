import google.generativeai as genai 
from dotenv import load_dotenv 
import os 

try: 
    load_dotenv(dotenv_path= '/workspaces/make_best/api_key.env') 
    GOOGLE_API_KEY = os.getenv('api_key') 
    genai.configure(api_key=GOOGLE_API_KEY)
    
except Exception as e : 
    
    print(f"Error accessing Google API Key: {e}")
    print("Please make sure you have added GOOGLE_API_KEY to Colab Secrets (Key icon on the left).")
    GOOGLE_API_KEY = None # Prevent further errors
    
genai_parameters = {
    'temperature' : 0.7, 
    'top_p' : 0.7, 
    'top_k' : 65, 
    'max_output_tokens': 17000, 
    'response_mime_type': 'text/plain'
}

safety_settings = [
    {
        'category' : 'HARM_CATEGORY_HARASSMENT', 
        'threshold' : 'BLOCK_MEDIUM_AND_ABOVE'
    }, 
    {
        'category' : 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 
        'threshold' :'BLOCK_MEDIUM_AND_ABOVE'
    }, 
    {
        'category' : 'HARM_CATEGORY_DANGEROUS_CONTENT', 
        'threshold' : 'BLOCK_MEDIUM_AND_ABOVE'
    }, 
    {
        'category' : 'HARM_CATEGORY_HATE_SPEECH', 
        'threshold' : 'BLOCK_MEDIUM_AND_ABOVE'
  
    }
        ] 


if GOOGLE_API_KEY : 
    try : 
        model = genai.GenerativeModel(
            model_name = 'gemini-1.5-flash-latest', 
            safety_settings= safety_settings, 
            generation_config = genai_parameters, 
            system_instruction = 'your are best ai for discribe user input you just only decribe user inputs and decribe all about that in maximum tokens that you have  tokens and if that about codes you assume that user is talking about make efficient extremly efficient code and discribe input in maximum tokens or 7000 and add information about last conversation and input and you also discribe how to extremly extremly efficiently make that how to do that and you just discribe that user input and explain well this input how to another model do that and best ' )
        chat_session = model.start_chat(history = []) 

    except Exception as e :
        raise RuntimeError('error found in initilizing model') 

def get_response(): 
    global chat_session 

    try:
        if not chat_session : 
            raise RuntimeWarning(f'warrning chat_sessions is not initilized ') 
        
        while True: 
            user_input = input('you :- ') 

            if user_input.lower() == 'quit': 
                print(f'nice to meet you') 
                break 

            response  =  chat_session.send_message(user_input)
            print(f'gpt :- {response.text}') 

    except Exception as e : 
        print(f'error founded during response geting {e}') 

get_response() 
























