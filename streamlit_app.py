import streamlit as st
import json
import re
import sys
from io import StringIO # To capture print statements if necessary
from model1 import make_model1, make_model2, make_model3, make_model4, make_model5 # Your classes

# --- Page Configuration ---
st.set_page_config(page_title="AI Super Assistant", layout="wide", initial_sidebar_state="collapsed")

# --- Custom CSS for ChatGPT-like appearance (Optional but recommended) ---
# You can expand this significantly
st.markdown("""
    <style>
    .stChatMessage {
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        display: flex;
    }
    .stChatMessage[data-testid="stChatMessageContentUser"] {
        background-color: #2b313e; /* User message background */
    }
    .stChatMessage[data-testid="stChatMessageContentAssistant"] {
        background-color: #40414f; /* Assistant message background */
    }
    .stCodeBlock {
        border-radius: 8px;
        border: 1px solid #555;
    }
    /* Add more styles for scrollbars, input box, etc. */
    </style>
""", unsafe_allow_html=True)


# --- Backend Model Initialization ---
# Initialize models once and store them in session state to preserve their internal state (like chat_session)
if 'model1_instance' not in st.session_state:
    try:
        st.session_state.model1_instance = make_model1() # Orchestrator
        st.session_state.model2_instance = make_model2() # Code Generator (as per your model1.py's make_model2)
        st.session_state.model3_instance = make_model3() # Apex Code Synthesizer
        st.session_state.model4_instance = make_model4() # Code Physician
        st.session_state.model5_instance = make_model5() # Iterative Refiner
        st.session_state.models_initialized = True
        print("INFO: All AI models initialized successfully.")
    except Exception as e:
        st.error(f"Fatal Error: Could not initialize AI models: {e}")
        st.stop() # Halt app execution if models can't load
        st.session_state.models_initialized = False

# --- Helper Function to Parse Multi-Part AI Responses ---
# (As discussed before, this needs to handle your models' specific output formats)
def parse_and_display_ai_response(response_string_from_model, container):
    """
    Parses the AI's string output which might contain a JSON block and then a code block,
    or raw code with setup instructions. Displays them in the given Streamlit container.
    """
    if not response_string_from_model:
        container.markdown("Received an empty response from the AI.")
        return

    # Attempt to handle Model4/Model5 type output (JSON report + Markdown Code Block)
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_string_from_model, re.DOTALL)
    code_block_after_json_match = None
    remaining_text_after_json = response_string_from_model

    if json_match:
        try:
            json_data = json.loads(json_match.group(1))
            container.json(json_data)
            # Remove the JSON part to look for subsequent code
            remaining_text_after_json = response_string_from_model.replace(json_match.group(0), "", 1).strip()
        except json.JSONDecodeError as e:
            container.warning(f"Could not parse JSON report: {e}")
            # Fall through to treat the whole thing as potential code or markdown

    # Now check remaining_text_after_json (or original string if no JSON) for a markdown code block
    # This regex captures optional language and the code content
    code_match = re.search(r"```(\w*)\s*\n(.*?)\n```", remaining_text_after_json, re.DOTALL)
    if code_match:
        language = code_match.group(1).lower() if code_match.group(1) else "plaintext"
        code_content = code_match.group(2)
        container.code(code_content, language=language)
        # Remove the code part to see if any conversational text remains
        remaining_text_after_code = remaining_text_after_json.replace(code_match.group(0), "", 1).strip()
        if remaining_text_after_code:
            container.markdown(remaining_text_after_code)
        return # Successfully parsed JSON and/or markdown code block

    # If no markdown code block found after potential JSON,
    # check if the *entire remaining string* is Model3-style raw code output
    # (setup instructions + pure code)
    # This part is tricky because Model3 output is raw. We assume it's code.
    # A better way would be if Model1 told us which model was invoked.
    # For now, if no JSON and no markdown code block, assume it might be raw code.
    if not json_match and not code_match and remaining_text_after_json.strip():
        # Heuristic: If it contains typical setup comment lines or common code keywords
        if remaining_text_after_json.strip().startswith(("#", "//")) or \
           "def " in remaining_text_after_json or "class " in remaining_text_after_json or \
           "import " in remaining_text_after_json:
            container.code(remaining_text_after_json, language="python") # Assuming Python for now
            return

    # If nothing specific was parsed, display as markdown
    if remaining_text_after_json.strip():
        container.markdown(remaining_text_after_json)
    elif not json_match and not code_match: # If original string was empty or only whitespace
         container.markdown("AI response processed (might be empty or only formatting).")


# --- Streamlit UI ---
st.title("💬 AI Super Assistant")
st.caption("Your advanced AI partner for coding, ML, and more. Powered by Gemini.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I assist you today with your coding or machine learning tasks?"}
    ]

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        parse_and_display_ai_response(message["content"], st) # Use st as the container

# --- Main Chat Input Logic ---
if user_input := st.chat_input("Ask me anything about code, ML, or a general query..."):
    if not st.session_state.get("models_initialized", False):
        st.error("Models are not initialized. Please check the console for errors.")
        st.stop()

    # Add user message to history and display
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Assistant's turn: This is where the pipeline is invoked
    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("🧠 Thinking...")

        # Capture stdout for streaming from models if they print directly
        # This is a workaround. Ideally, models should return strings/streams.
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        try:
            # 1. Call Model1 (Orchestrator)
            # model1 uses its internal chat_session for its own context
            model1_raw_output_text = st.session_state.model1_instance(user_input) # Pass only the current user input

            # Restore stdout
            sys.stdout = old_stdout
            printed_during_model1 = captured_output.getvalue()
            if printed_during_model1: # Display anything model1 printed (if any)
                thinking_placeholder.markdown(f"```log\n{printed_during_model1}\n```")


            # Parse Model1's JSON output
            # (Your model1.py currently does this splitting, but it's better if model1_instance returns clean JSON or a dict)
            try:
                # Assuming model1_raw_output_text is the string containing the JSON block
                json_str_match = re.search(r"```json\s*(\{.*?\})\s*```", model1_raw_output_text, re.DOTALL)
                if not json_str_match:
                    # If model1 did not return the JSON in markdown, maybe it returned raw JSON
                    # This is less ideal as it mixes with potential conversational text from model1
                    try:
                        model1_output_json = json.loads(model1_raw_output_text.strip())
                    except json.JSONDecodeError:
                         raise ValueError(f"Model1 output was not valid JSON nor wrapped in ```json: {model1_raw_output_text}")
                else:
                    model1_output_json = json.loads(json_str_match.group(1))

            except (json.JSONDecodeError, AttributeError, ValueError) as e:
                thinking_placeholder.error(f"Error parsing Model 1's decision: {e}\nModel1 Raw Output:\n{model1_raw_output_text}")
                st.session_state.messages.append({"role": "assistant", "content": f"Sorry, I had trouble understanding the initial request structure. Error: {e}"})
                st.stop()


            assistant_final_response_str = ""

            if model1_output_json.get("is_code_related", False):
                user_ack = model1_output_json.get("response_for_user", "Processing your code-related request...")
                if user_ack: # Display acknowledgement if model1 provided one
                     thinking_placeholder.markdown(user_ack + " Working on it...")
                else: # Default thinking message
                    thinking_placeholder.markdown("Processing your code-related request... This may take a moment.")


                prompt_for_model2 = model1_output_json.get("prompt_for_model2", "")
                if not prompt_for_model2.strip():
                    err_msg = "Model 1 indicated a code task but provided no instructions for the next model."
                    thinking_placeholder.error(err_msg)
                    assistant_final_response_str = f"Internal Error: {err_msg}"
                else:
                    # --- Execute the pipeline as per your make_best.__call__ ---
                    # We need to capture output from each step if they stream/print
                    # For simplicity, this example will call them and assume they return a final string.
                    # You'll need to adapt this if you want to show intermediate model outputs.

                    # Reset captured_output for the specialized models
                    sys.stdout = captured_output = StringIO()

                    # Call Model2 (Code Generator, as per your original model1.py's Model2 definition)
                    # This model in your code uses generate_content with stream=True and prints
                    thinking_placeholder.markdown(user_ack + " (Stage 2/5: Generating initial code...)")
                    # The __call__ for your make_model2 already handles streaming and returns full_content
                    output_from_model2 = st.session_state.model2_instance(prompt_for_model2)
                    # output_from_model2 is now the raw code text

                    # Call Model3 (Apex Code Synthesizer - refines Model2's output or works from Model1's prompt)
                    # For this pipeline, let's assume Model3 refines Model2's output
                    thinking_placeholder.markdown(user_ack + " (Stage 3/5: Refining code structure...)")
                    output_from_model3 = st.session_state.model3_instance(f"<CodeToRefine>\n{output_from_model2}\n</CodeToRefine>\n<TaskGoal>Refine this code to meet Apex standards: raw output, setup instructions, peak quality.</TaskGoal>")
                    # output_from_model3 is raw text (setup + pure code)

                    # Call Model4 (Code Physician - fixes Model3's output)
                    thinking_placeholder.markdown(user_ack + " (Stage 4/5: Diagnosing and correcting...)")
                    output_from_model4 = st.session_state.model4_instance(f"<CodeToFix language='python'>\n{output_from_model3}\n</CodeToFix>\n<RequestDetails>Diagnose, fix, and verify this code. Adhere to any implicit library constraints. Output JSON report then corrected code block.</RequestDetails>")
                    # output_from_model4 is JSON report string + Markdown code block string

                    # Call Model5 (Iterative Refiner - further perfects Model4's output)
                    thinking_placeholder.markdown(user_ack + " (Stage 5/5: Final iterative perfection...)")
                    # Model5 expects markdown code block for <CodeToPerfect>
                    # We need to extract the code part from model4's output
                    code_to_perfect_match = re.search(r"```python\s*\n(.*?)\n```", output_from_model4, re.DOTALL)
                    if code_to_perfect_match:
                        code_to_perfect = code_to_perfect_match.group(1)
                        prompt_for_model5 = f"<CodeToPerfect language='python'>\n```python\n{code_to_perfect}\n```\n</CodeToPerfect>\n<TaskGoal>Iteratively perfect this code until it's 100% runnable and functionally complete. Output JSON log then final code block.</TaskGoal>\n<MaxIterations>5</MaxIterations>"
                        output_from_model5 = st.session_state.model5_instance(prompt_for_model5)
                        assistant_final_response_str = output_from_model5 # This is the final output to display
                    else:
                        assistant_final_response_str = "Error: Could not extract code from Model 4's output to feed into Model 5.\n\nModel 4 Output:\n" + output_from_model4


                    # Restore stdout and get any printed output from specialized models
                    sys.stdout = old_stdout
                    printed_during_specialized_models = captured_output.getvalue()
                    if printed_during_specialized_models:
                        # This might be a lot if models stream to stdout.
                        # You might choose to display only the final response_str
                        # or append this to a debug log.
                        print(f"DEBUG: Stdout from specialized models:\n{printed_during_specialized_models}")


            else: # Not code-related, simple response from Model1
                assistant_final_response_str = model1_output_json.get("response_for_user", "I'm not sure how to help with that. Could you try rephrasing?")
                thinking_placeholder.empty() # Clear "Thinking..."
                # Directly display simple chat
                # For simple chat, we don't need the complex parser here, just markdown
                st.markdown(assistant_final_response_str)


            # Display the final assembled response from the pipeline if it's a complex one
            if model1_output_json.get("is_code_related", False) and assistant_final_response_str:
                thinking_placeholder.empty() # Clear "Thinking..."
                # Use the robust parser for the final output of the pipeline
                parse_and_display_ai_response(assistant_final_response_str, st)


        except Exception as e:
            sys.stdout = old_stdout # Ensure stdout is restored on error
            thinking_placeholder.error(f"An error occurred in the AI pipeline: {e}")
            assistant_final_response_str = f"Sorry, I encountered an error: {e}"
            # Log full traceback to console for debugging
            import traceback
            traceback.print_exc()

    # Add final assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_final_response_str})
