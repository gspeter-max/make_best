import streamlit as st
import json
import re
import time
# Import your model classes from your model1.py
# Ensure model1.py is in the same directory or accessible via PYTHONPATH
from model1 import (
    make_model1,
    make_model2,
    make_model3, # This is your Apex Code Synthesizer as per your model1.py
    make_model4,
    make_model5
    # Add make_model_ml_optimizer if you have it defined in your model1.py
    # and model1 can route to it. For now, assuming the M1-M5 pipeline.
)

# --- Page Configuration ---
st.set_page_config(
    page_title="GenAI Super Coder (User's Backend)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS ---
st.markdown("""
    <style>
        body, .main { color: #E0E0E0; background-color: #0E1117; }
        .main > div:first-child { padding-bottom: 8rem !important; }
        .stChatMessage { border-radius: 12px; padding: 0.8rem 1.0rem; margin-bottom: 1rem;
                         border: 1px solid #303238; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                         word-wrap: break-word; overflow-wrap: break-word; }
        .stChatMessage[data-testid="stChatMessageContentUser"] {
            background-color: #2A3942; color: #FFFFFF; margin-left: auto;
            max-width: 70%; float: right; clear: both; }
        .stChatMessage[data-testid="stChatMessageContentUser"] p { color: #FFFFFF !important; }
        .stChatMessage[data-testid="stChatMessageContentAssistant"] {
            background-color: #2F3136; color: #DCDDDE; margin-right: auto;
            max-width: 85%; float: left; clear: both; }
        .stChatMessage[data-testid="stChatMessageContentAssistant"] p { color: #DCDDDE !important; }
        .stChatMessage[data-testid="stChatMessageContentAssistant"] .stCodeBlock,
        .stChatMessage[data-testid="stChatMessageContentAssistant"] .stJson {
             margin-top: 0.5rem; margin-bottom: 0.5rem; }
        .stCodeBlock { border-radius: 8px !important; border: 1px solid #40444B !important;
                       background-color: #1E1F22 !important; }
        .stCodeBlock pre { background-color: #1E1F22 !important; padding: 0.75rem !important; }
        .stCodeBlock pre code { color: #DCDDDE !important; background-color: transparent !important; }
        .stJson { border-radius: 8px; border: 1px solid #40444B; padding: 0.75rem;
                  background-color: #1E1F22 !important; color: #DCDDDE !important; }
        .stJson pre { color: #DCDDDE !important; background-color: transparent !important; }
        .main .stChatInputContainer { position: fixed; bottom: 0; left: 0; right: 0; width: 100%;
                                     background-color: #1A1B1E; padding: 0.6rem 1.2rem;
                                     border-top: 1px solid #303238; box-shadow: 0 -1px 5px rgba(0,0,0,0.15);
                                     z-index: 999; }
        .stTextInput > div > div > input { background-color: #2C2E33 !important; color: #E0E0E0 !important;
                                           border: 1px solid #40444B !important; border-radius: 8px !important;
                                           padding: 0.5rem 0.75rem !important; }
        .stTextInput > div > div > input::placeholder { color: #72767D !important; }
        .stChatInputContainer button { background-color: #4F545C !important; color: white !important;
                                      border-radius: 8px !important; border: none !important; }
        .stChatInputContainer button:hover { background-color: #5D6169 !important; }
        .thinking-placeholder p { font-style: italic; color: #8A8F98; padding: 0.5rem 0; }
    </style>
""", unsafe_allow_html=True)

# --- Model Initialization ---
if 'models_initialized_flag' not in st.session_state: st.session_state.models_initialized_flag = False
if not st.session_state.models_initialized_flag:
    with st.spinner("Initializing AI Cores... This might take a moment."):
        try:
            # These must match the class names in your model1.py
            st.session_state.model1_instance = make_model1()
            st.session_state.model2_instance = make_model2()
            st.session_state.model3_instance = make_model3() # Your Apex Synthesizer
            st.session_state.model4_instance = make_model4()
            st.session_state.model5_instance = make_model5()
            # If you add make_model_ml_optimizer to your model1.py, initialize it here too
            # st.session_state.model_ml_optimizer_instance = make_model_ml_optimizer()
            st.session_state.models_initialized_flag = True
            print("INFO (Streamlit): All AI models initialized successfully.")
        except RuntimeError as e:
            st.error(f"Fatal Error during AI Model Initialization: {e}")
            st.error("Ensure GOOGLE_API_KEY is in 'api_key.env' or set as environment variable.")
            st.session_state.models_initialized_flag = False
        except Exception as e:
            st.error(f"An unexpected fatal error during AI Model Initialization: {e}")
            import traceback; traceback.print_exc()
            st.session_state.models_initialized_flag = False

# --- Helper Function to Parse and Display AI's Multi-Part Response ---
def display_ai_parts_from_string(full_response_string, container_to_write_in, expected_model_output_style="unknown"):
    """
    Parses and displays structured AI responses based on expected style.
    Returns a list of dicts representing the parts for history storage.
    """
    if not full_response_string or not full_response_string.strip():
        return [{"type": "text", "data": "*AI provided no output or only whitespace for this part.*"}]

    displayed_parts_for_history = []
    remaining_text = full_response_string.strip()

    if expected_model_output_style in ["model4_style", "model5_style"]: # Expect JSON report then MD code
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", remaining_text, re.DOTALL)
        if json_match:
            try:
                json_data = json.loads(json_match.group(1))
                displayed_parts_for_history.append({"type": "json", "data": json_data})
                container_to_write_in.json(json_data)
                remaining_text = remaining_text.replace(json_match.group(0), "", 1).strip()
            except json.JSONDecodeError as e:
                container_to_write_in.warning(f"AI Warning: Could not parse JSON block: {e}.")

        code_match_md = re.search(r"```(\w*)\s*\n(.*?)\n```", remaining_text, re.DOTALL)
        if code_match_md:
            language = code_match_md.group(1).lower().strip() if code_match_md.group(1) else "plaintext"
            code_content = code_match_md.group(2).strip()
            displayed_parts_for_history.append({"type": "code", "data": {"language": language, "code": code_content}})
            container_to_write_in.code(code_content, language=language)
            remaining_text = remaining_text.replace(code_match_md.group(0), "", 1).strip()

    elif expected_model_output_style == "model2_or_3_raw_code_style": # Expect raw setup comments + raw code
        # This style is just text, possibly starting with comments
        lang_guess = "python" # Default for raw code
        if "function " in remaining_text and "{" in remaining_text and not remaining_text.strip().startswith("def "): lang_guess = "javascript"
        elif "public class" in remaining_text and "{" in remaining_text: lang_guess = "java"
        
        displayed_parts_for_history.append({"type": "code", "data": {"language": lang_guess, "code": remaining_text}})
        container_to_write_in.code(remaining_text, language=lang_guess)
        remaining_text = "" # Assume all was code

    # Display any text that remains as markdown (e.g., if parsing failed or it's simple text)
    if remaining_text.strip():
        displayed_parts_for_history.append({"type": "text", "data": remaining_text})
        container_to_write_in.markdown(remaining_text)
    
    if not displayed_parts_for_history and (full_response_string and full_response_string.strip()):
         displayed_parts_for_history.append({"type": "text", "data": full_response_string})
    return displayed_parts_for_history


# --- Streamlit UI Title ---
st.title("✨ GenAI Super Coder (User Backend Ver.) ✨")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content_parts": [{"type": "text", "data": "Hello! I'm your AI Super Coder. How can I assist you today?"}]}
    ]

for msg_data in st.session_state.messages:
    with st.chat_message(msg_data["role"]):
        if "content_parts" in msg_data:
            for part_idx, part in enumerate(msg_data["content_parts"]):
                if part_idx > 0 and msg_data["role"] == "assistant" and \
                   ( (part["type"] == "json" or part["type"] == "code") or \
                     (msg_data["content_parts"][part_idx-1]["type"] == "json" or \
                      msg_data["content_parts"][part_idx-1]["type"] == "code") ):
                    st.markdown("---") 
                if part["type"] == "text": st.markdown(part["data"])
                elif part["type"] == "json": st.json(part["data"])
                elif part["type"] == "code": st.code(part["data"]["code"], language=part["data"]["language"])
        elif "content" in msg_data: st.markdown(msg_data["content"])


if user_input := st.chat_input("Describe your coding task or ask a question..."):
    if not st.session_state.get("models_initialized_flag", False):
        st.error("AI Models are not ready. Please check startup messages or console logs.")
    else:
        st.session_state.messages.append({"role": "user", "content_parts": [{"type": "text", "data": user_input}]})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            current_assistant_turn_container = st.container()
            thinking_placeholder = current_assistant_turn_container.empty()
            thinking_placeholder.markdown("<p class='thinking-placeholder'>🧠 Orchestrating (Model 1)...</p>", unsafe_allow_html=True)

            accumulated_final_parts_for_history_this_turn = []

            try:
                # Model1's __call__ expects just the current prompt; it uses its internal chat_session
                # but we pass the UI history for its context construction if it's designed to use it.
                # YOUR model1.py __call__ takes user_prompt and optionally ui_chat_history_for_context.
                model1_raw_text_output = st.session_state.model1_instance(user_input, st.session_state.messages) # Pass UI history for context

                # Parse Model1's output (YOUR model1.py __call__ returns raw text, not dict)
                model1_output_json = None
                json_str_match_m1 = re.search(r"```json\s*(\{.*?\})\s*```", model1_raw_text_output, re.DOTALL)
                if json_str_match_m1:
                    try:
                        model1_output_json = json.loads(json_str_match_m1.group(1))
                    except json.JSONDecodeError as e:
                        current_assistant_turn_container.error(f"M1 JSON Error: {e}. Raw: {json_str_match_m1.group(1)}")
                else: # Try parsing as raw JSON if no markdown wrapper
                    try:
                        model1_output_json = json.loads(model1_raw_text_output.strip())
                    except json.JSONDecodeError as e:
                         current_assistant_turn_container.error(f"M1 Output Error: Not valid JSON. Raw: {model1_raw_text_output}")
                
                if not model1_output_json: # If parsing failed completely
                    model1_output_json = { # Fallback
                        "is_code_related": False,
                        "response_for_user": "I had trouble understanding the request structure from Model 1."
                    }


                is_code_related = model1_output_json.get("is_code_related", False)
                user_ack_from_model1 = model1_output_json.get("response_for_user", "") # Changed from user_facing_acknowledgement
                prompt_for_next = model1_output_json.get("prompt_for_model2", "") # Using your M1's key

                initial_ack_displayed_in_turn = False
                if user_ack_from_model1 and user_ack_from_model1.strip():
                    accumulated_final_parts_for_history_this_turn.append({"type": "text", "data": user_ack_from_model1})
                    current_assistant_turn_container.markdown(user_ack_from_model1)
                    initial_ack_displayed_in_turn = True
                    thinking_placeholder_text = user_ack_from_model1 if len(user_ack_from_model1.strip()) < 50 else "Processing..."
                    if is_code_related:
                        thinking_placeholder.markdown(f"<p class='thinking-placeholder'>{thinking_placeholder_text} Engaging specialized AI pipeline...</p>", unsafe_allow_html=True)
                    else:
                        thinking_placeholder.empty()

                if is_code_related and prompt_for_next and prompt_for_next.strip():
                    if initial_ack_displayed_in_turn: current_assistant_turn_container.markdown("---")
                    
                    # --- EXECUTE YOUR FIXED M2->M3->M4->M5 PIPELINE ---
                    pipeline_output_accumulator = []
                    pipeline_stream_display_area = current_assistant_turn_container.empty()
                    
                    current_data_for_next_model = prompt_for_next

                    # Stage 2: Model 2
                    thinking_placeholder.markdown("<p class='thinking-placeholder'>Pipeline Stage: Generating Code (Model 2)...</p>", unsafe_allow_html=True)
                    temp_accumulator_m2 = []
                    for chunk in st.session_state.model2_instance(current_data_for_next_model):
                        temp_accumulator_m2.append(chunk)
                        pipeline_stream_display_area.markdown("".join(temp_accumulator_m2) + " ▌")
                    current_data_for_next_model = "".join(temp_accumulator_m2) # Output of M2
                    pipeline_stream_display_area.empty() # Clear for next stage's stream

                    # Stage 3: Model 3 (Apex - refines M2 output)
                    thinking_placeholder.markdown("<p class='thinking-placeholder'>Pipeline Stage: Refining Code (Model 3)...</p>", unsafe_allow_html=True)
                    prompt_for_m3 = f"<CodeToRefine language='python'>\n{current_data_for_next_model}\n</CodeToRefine>\n<TaskGoal>Refine this code to Apex standards: raw output, setup instructions, peak quality.</TaskGoal>"
                    temp_accumulator_m3 = []
                    for chunk in st.session_state.model3_instance(prompt_for_m3):
                        temp_accumulator_m3.append(chunk)
                        pipeline_stream_display_area.markdown("".join(temp_accumulator_m3) + " ▌")
                    current_data_for_next_model = "".join(temp_accumulator_m3) # Output of M3
                    pipeline_stream_display_area.empty()

                    # Stage 4: Model 4 (Physician - takes M3 output)
                    thinking_placeholder.markdown("<p class='thinking-placeholder'>Pipeline Stage: Diagnosing & Correcting (Model 4)...</p>", unsafe_allow_html=True)
                    prompt_for_m4 = f"<CodeToFix language='python'>\n{current_data_for_next_model}\n</CodeToFix>\n<RequestDetails>Diagnose, fix, and verify this code. Adhere to any implicit library constraints. Output JSON report then corrected code block.</RequestDetails>"
                    temp_accumulator_m4 = []
                    for chunk in st.session_state.model4_instance(prompt_for_m4):
                        temp_accumulator_m4.append(chunk)
                        pipeline_stream_display_area.markdown("".join(temp_accumulator_m4) + " ▌")
                    current_data_for_next_model = "".join(temp_accumulator_m4) # Output of M4 (JSON + MD Code)
                    pipeline_stream_display_area.empty()

                    # Stage 5: Model 5 (Iterative Refiner - takes code part of M4 output)
                    thinking_placeholder.markdown("<p class='thinking-placeholder'>Pipeline Stage: Iteratively Perfecting (Model 5)...</p>", unsafe_allow_html=True)
                    code_to_perfect_match_m5 = re.search(r"```python\s*\n(.*?)\n```", current_data_for_next_model, re.DOTALL)
                    if code_to_perfect_match_m5:
                        code_for_m5 = code_to_perfect_match_m5.group(1).strip()
                        prompt_for_m5 = f"<CodeToPerfect language='python'>\n```python\n{code_for_m5}\n```\n</CodeToPerfect>\n<TaskGoal>Iteratively perfect this code until it's 100% runnable and functionally complete. Output JSON log then final code block.</TaskGoal>\n<MaxIterations>5</MaxIterations>" # MaxIterations can be configurable
                        temp_accumulator_m5 = []
                        for chunk in st.session_state.model5_instance(prompt_for_m5):
                            temp_accumulator_m5.append(chunk)
                            pipeline_stream_display_area.markdown("".join(temp_accumulator_m5) + " ▌")
                        final_pipeline_output_string = "".join(temp_accumulator_m5) # Output of M5
                    else:
                        final_pipeline_output_string = "Error: Could not extract code from Model 4 to feed Model 5.\nShowing Model 4 output instead:\n" + current_data_for_next_model
                    
                    pipeline_stream_display_area.empty()
                    thinking_placeholder.empty()
                        
                    # Parse and display the FINAL output of the pipeline (from Model 5 or Model 4 if M5 had issues)
                    # Model 4 and 5 output style is JSON then MD code block
                    parsed_pipeline_parts = display_ai_parts_from_string(final_pipeline_output_string, current_assistant_turn_container, expected_model_output_style="model4_style") # or model5_style
                    accumulated_final_parts_for_history_this_turn.extend(parsed_pipeline_parts)

                elif not is_code_related and not user_ack_from_model1.strip():
                    fallback_msg = "I'm ready to assist. What can I do for you?"
                    current_assistant_turn_container.markdown(fallback_msg)
                    accumulated_final_parts_for_history_this_turn.append({"type": "text", "data": fallback_msg})
                
                if not (is_code_related and prompt_for_next and prompt_for_next.strip()): # If it was a simple chat
                    thinking_placeholder.empty()


            except Exception as e:
                thinking_placeholder.empty()
                error_msg = f"An unexpected error occurred processing your request: {e}"
                current_assistant_turn_container.error(error_msg)
                accumulated_final_parts_for_history_this_turn.append({"type": "text", "data": f"Sorry, I encountered an error: {e}"})
                import traceback; traceback.print_exc()

        # Add final assistant response parts to session state for durable display
        if accumulated_final_parts_for_history_this_turn:
            st.session_state.messages.append({"role": "assistant", "content_parts": accumulated_final_parts_for_history_this_turn})
        # If M1 only gave an ack for a non-code task, and nothing else was added.
        elif not accumulated_final_parts_for_history_this_turn and user_ack_from_model1 and not is_code_related:
             st.session_state.messages.append({"role": "assistant", "content_parts": [{"type": "text", "data": user_ack_from_model1}]})
