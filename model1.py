import google.generativeai as genai 
from dotenv import load_dotenv 
import os 

class make_best: 
    
    def __init__(self,env_path = '/workspaces/make_best/api_key.env', key_name = 'api_key'):  
        try: 
            
            load_dotenv(dotenv_path= env_path) 
            self.GOOGLE_API_KEY = os.getenv(key_name) 
            genai.configure(api_key=self.GOOGLE_API_KEY)
    
        except Exception as e : 
    
            print(f"Error accessing Google API Key: {e}")
            print("Please make sure you have added GOOGLE_API_KEY to Colab Secrets (Key icon on the left).")
            self.GOOGLE_API_KEY = None # Prevent further errors
    
    def __call__(self): 
        
        model1 = make_model1() 
        model2 = make_model2() 
        while True: 
            user_prompt = input('you ;') 
            if  user_prompt.lower() == 'quit': 
                break 
        
            model2_input = model1(user_prompt) 
            print('---------------------------------------------------------------------------------------') 
            print(f' gpt2 : -- {model2(model2_input)}') 
        
        '''
            here th while logic is appling and user interface how to hand users 
            # here the call logic like 
            
            model1(user_prompt) ==> model2(model1) ==> ........... return 
            work with class and that models and that shit     
        
        '''
class make_model1(make_best): 

    def __init__(self,max_output_tokens = 7500, model_name = 'gemini-1.5-flash-latest'): 

        super().__init__() 
        genai_parameters = {
            'temperature' : 0.3, 
            'top_p' : 0.9, 
            'top_k' : 40, 
            'max_output_tokens': max_output_tokens, 
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

        if self.GOOGLE_API_KEY : 
            try : 
                model = genai.GenerativeModel(
                    model_name = model_name, 
                    safety_settings= safety_settings, 
                    generation_config = genai_parameters, 
                    system_instruction = '''
                    
                            "You are an intelligent gatekeeper and expert prompt engineer for a specialized AI coding assistant (Model 2). "
                            "Your primary function is to analyze user input and recent conversation history to determine if a request is code-related. "
                            "Conversation history is crucial for context.\n\n"

                            "YOUR BEHAVIOR:\n"
                            "1.  IF the user's latest input, considered with the immediate preceding conversation context (last 3-5 turns), "
                            "    clearly requests code generation, code modification, code optimization, or directly discusses a programming problem "
                            "    requiring a code solution:\n"
                            "    a.  Your SOLE output MUST be a meticulously crafted, highly detailed, and directive prompt FOR MODEL 2. "
                            "        This prompt must be self-contained and instruct Model 2 as follows:\n"
                            "        'You are an elite AI specializing in writing extremely efficient and comprehensive code. "
                            "        Your ONLY output should be the requested code. Do NOT include explanations, apologies, or any text other than the code itself. "
                            "        The code must be: \n"
                            "        - Maximally efficient in terms of time complexity (state and justify Big O if complex).\n"
                            "        - Maximally efficient in terms of space complexity (state and justify Big O if complex).\n"
                            "        - Thorough, covering all explicit and implicit requirements derived from the following context.\n"
                            "        - Robust, handling potential edge cases and invalid inputs gracefully.\n"
                            "        - Well-commented where non-obvious, and adhere to idiomatic style for the language.\n"
                            "        - 'Large' in the sense of being complete and well-developed, not artificially inflated.\n"
                            "        Based on this context: [INSERT DETAILED PROBLEM DESCRIPTION, CONSTRAINTS, LANGUAGE, RELEVANT HISTORY, AND USER'S EXACT REQUEST HERE. BE EXHAUSTIVE. Synthesize all information into a clear task for Model 2.]'\n"
                            "    b.  When constructing the '[INSERT...]' part, synthesize the user's current request with key details from the provided conversation history (e.g., language preference, libraries mentioned, prior constraints). Be explicit and comprehensive.\n"
                            "    c.  Use as many tokens as needed, up to 7000, for this directive prompt to Model 2 to ensure clarity and completeness. Do not add any other text around this generated prompt.\n"
                            "2.  ELSE (if the user's input is NOT code-related, or if it's ambiguous after considering history):\n"
                            "    Your SOLE output MUST be the exact phrase: 'Nice to meet you!'\n\n"

                            "Remember to analyze the provided conversation history to understand ongoing context, language choices, or constraints previously established by the user."

                        ''' 
                ) 
                
                self.chat_session = model.start_chat(history = []) 

            except Exception as e :
                raise RuntimeError('error found in initilizing model') 
            
    
    def __call__(self,user_prompt): 
    
        try:
            if not self.chat_session : 
                raise RuntimeWarning(f'warrning chat_sessions is not initilized ') 

            response  =  self.chat_session.send_message(user_prompt)
            print(f'gpt :- {response.text}') 

            return response.text 
        
        except Exception as e : 
            raise RuntimeError(f'error founded during response geting {e}') 


class make_model2(make_best): 

    def __init__(self,max_output_tokens = 8120, model_name = 'gemini-1.5-flash-latest'): 
        super().__init__() 
        
        generation_configure = {
                'temperature' : 0.9, 
                'max_output_tokens' : max_output_tokens, 
                'top_p' : 0.9,
                'top_k' : 100, 
                'response_mime_type' : 'text/plain' 
                } 

        safety_setting = [
                    {   
                        'category' : 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
                        'threshold' : 'BLOCK_MEDIUM_AND_ABOVE' 
                        },
                    {
                        'category' : 'HARM_CATEGORY_DANGEROUS_CONTENT', 
                        'threshold' : 'BLOCK_MEDIUM_AND_ABOVE'
                        }, 
                    {
                        'category' : 'HARM_CATEGORY_HATE_SPEECH', 
                        'threshold' : 'BLOCK_MEDIUM_AND_ABOVE'
                        }, 
                    {
                        'category' : 'HARM_CATEGORY_HARASSMENT', 
                        'threshold' : 'BLOCK_MEDIUM_AND_ABOVE'
                        } 
        ] 
        
        try :
            MODEL = genai.GenerativeModel(
                        model_name = model_name,
                        safety_settings = safety_setting, 
                        generation_config = generation_configure, 
                        system_instruction = 
                            '''
                        
                            "You are an elite AI specializing in writing extremely efficient and comprehensive code. "
                            "Your ONLY output should be the requested code. Do NOT include explanations, apologies, or any text other than the code itself. "
                            "Strictly follow all directives in the user's prompt."    
                        
                            ''' 
            )  
            self.chat_session = MODEL.start_chat(history = []) 
        
        except Exception as  e: 
            raise RuntimeError('error is found during model initilization ') 
        
    def __call__(self,user_content):
        if not self.chat_session: 
            raise RuntimeWarning('warning is found') 

        response = self.chat_session.send_message(user_content) 
        return response.text 

    
model_ = make_best() 
model_()
 



















