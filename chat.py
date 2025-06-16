# Step 1: Import libraries
import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from huggingface_hub import login

# Step 2: Configure the page
st.set_page_config(page_title="AI Chat Assistant", page_icon=":robot_face:")
st.title("AI Chat Assistant")

# Step 3: Login to Hugging Face
HF_API_KEY = "your_huggingface_api"
if HF_API_KEY != "your_huggingface_api":
    login(HF_API_KEY)
else:
    st.warning("Please set your Hugging Face API key in the code.")

# Step 4: Initialize the session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Step 5: Load the model and tokenizer
@st.cache_resource
def load_model():
    model_name = "ibm-granite/granite-3.3-2b-instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=HF_API_KEY)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        token=HF_API_KEY,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else "cpu"
    )
    return model, tokenizer

# Step 6: Create a function to generate response
def generate_response(prompt, tokenizer, model):
    formatted_prompt = f"Human: {prompt}\nAssistant:"
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)
    if torch.cuda.is_available():
        inputs = {k: v.half() for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=512,
            num_return_sequences=1,
            do_sample=True,
            top_p=0.95,
            temperature=0.7
        )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.split("Assistant:")[-1].strip()

with st.spinner("Loading model..."):
    model, tokenizer = load_model()
st.success("Model loaded successfully.")

# Step 7: Create a function to handle the chatbot
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Please enter your query:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Processing your request..."):
        response = generate_response(prompt, tokenizer, model)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)