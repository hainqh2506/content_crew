from crewai import LLM
import os
from dotenv import load_dotenv
load_dotenv()


TOGETHER_AI_API_KEY = os.getenv("TOGETHER_AI_API_KEY")
togetherai_llm = LLM(
    model="together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo",
    temperature=0.7,        # Higher for more creative outputs
    timeout=120,           # Seconds to wait for response
    #max_tokens=4000,       # Maximum length of response
    top_p=0.9,            # Nucleus sampling parameter
    api_key=TOGETHER_AI_API_KEY
    
    
    # frequency_penalty=0.1, # Reduce repetition
    # presence_penalty=0.1,  # Encourage topic diversity
    # response_format={"type": "json"},  # For structured outputs
    # seed=42               # For reproducible results
)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")    
gemini_llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7,        # Higher for more creative outputs
    timeout=120,           # Seconds to wait for response
    api_key=GEMINI_API_KEY,
    
)

gg_embedder={
"provider": "google",
"config": {
    "model": "models/text-embedding-004",
    "api_key": GEMINI_API_KEY,
}
}
