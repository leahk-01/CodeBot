from fastapi import FastAPI
from langchain.agents import initialize_agent, AgentType
from src.models import CodeRequest, GenerateRequest, TranslateRequest, StylePreferences
from src.llm_service import LLMService
import json
import uvicorn
from langchain.tools import Tool

app = FastAPI()
llm = LLMService()

detect_language_tool = Tool.from_function(
    name="detect_language",
    func=llm.detect_language,
    description="Detects the programming language of a given code snippet."
)

tools = [detect_language_tool]

def initialize_dynamic_agent(task_type: str):
    selected_model = llm.select_model(task_type)  # Ensure correct model selection
    return initialize_agent(
        tools=tools,
        llm=selected_model,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )

@app.post("/explain_code")
def explain_code(request: CodeRequest):
    """Takes a code snippet and returns its explanation along with detected language."""
    code = request.code

    try:
        detected_language = llm.detect_language(code)

        if not isinstance(detected_language, str) or detected_language.strip() == "":
            detected_language = "Unknown"

    except Exception as e:
        print(f"Error detecting language: {e}")
        detected_language = "Unknown"

    explanation = llm.explain_code(code)

    return {"language": detected_language, "explanation": explanation["explanation"]}

@app.post("/generate_code")
def generate_code(request: GenerateRequest):
    """Generates a code snippet based on user description and language."""
    try:
        agent = initialize_dynamic_agent("generation")
        generated_code = agent.invoke(f"Generate a {request.language} code snippet for: {request.description}")

        return {"language": request.language, "generated_code": generated_code}
    except Exception as e:
        print(f"Error generating code: {e}")
        return {"error": "Code generation failed"}

@app.post("/translate_code")
def translate_code(request: TranslateRequest):
    """Takes a code snippet and translates it into a target language."""
    try:
        translated_result = llm.translate_code(request.code, request.target_language)

        if "error" in translated_result:
            return translated_result  # Return error if translation failed

        return {
            "input_language": translated_result["source_language"],
            "target_language": translated_result["target_language"],
            "translated_code": translated_result["translated_code"]
        }
    except Exception as e:
        print(f"Error translating code: {e}")
        return {"error": "Code translation failed"}

@app.post("/style_preferences")
def store_style_preferences(request: StylePreferences):
    """Stores user-defined code style preferences in a JSON file."""
    preferences = request.model_dump()

    with open("style_prefs.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(preferences, indent=4))
    return {"message": "Style preferences saved successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
