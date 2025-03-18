from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from src.settings import DEFAULT_MODEL, AVAILABLE_MODELS
from langchain.tools import tool
import httpx

class LLMService:
    def __init__(self):
        self.models = {
            "explanation": OllamaLLM(model=DEFAULT_MODEL),
            "generation": OllamaLLM(model=AVAILABLE_MODELS[0]),
            "translation": OllamaLLM(model=DEFAULT_MODEL),
        }
    def select_model(self, task_type: str):
        return self.models.get(task_type, OllamaLLM(model=DEFAULT_MODEL))


    @tool
    def detect_language( code: str) -> str:
        """Detects the programming language of a given code snippet. """

        url = "http://ai.easv.dk:8989/tools/langrecog/"

        json_payload = {
            "codesnippet": code.strip(),
            "language": ""
        }
        try:
            response = httpx.post(url, json=json_payload, timeout=30)
            response.raise_for_status()

            print(f"API Response: {response.json()}")

            detected_language = response.json().get("language", "Unknown")  # Extract returned language
            return detected_language
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e}")
            print(f"Response content: {e.response.text}")
            return "Unknown"

        except httpx.TimeoutException:
            print("API request timed out! Try increasing timeout or checking VPN.")
            return "Unknown"


    def explain_code(self, code: str) -> dict:
        detected_language = self.detect_language(code)
        model = self.select_model("explanation")


        prompt = f"""
        Role: You are an expert software engineer.
        Context: The user provided a {detected_language} code snippet.
        Task: Explain what this code does in a simple, easy-to-understand way.
        Limitation: Keep the explanation concise.
        Audience: Developers of all levels.

        Code:
        ```{detected_language}
        {code}
        ```

        Explanation:
        """
        explanation = model.invoke(prompt)

        return {"language": detected_language, "explanation": str(explanation)}



    def generate_code(self, description: str, language: str) -> str:
        model = self.select_model("generation")


        prompt_template = PromptTemplate(
            input_variables=["language", "description"],
            template="""
            Role: You are an expert {language} programmer.
            Context: The user wants a {language} code snippet for the following functionality.
            Task: Generate a {language} code snippet that matches the user's request.
            Limitation: Provide only the code, no extra text.
            Audience: Developers.

            ### Examples:
            **Description**: Create a Python function to check if a number is even.
            **Python Code**:
            ```python
            def is_even(n):
                return n % 2 == 0
            ```

            **Description**: Create a JavaScript function to reverse a string.
            **JavaScript Code**:
            ```javascript
            function reverseString(str) {{
                return str.split("").reverse().join("");
            }}
            ```

            ### Now generate code for:
             {description}
             """
        )

        # Use LLMChain to process the request
        chain = prompt_template | model
        # Invoke the chain with the provided description and language
        generated_output = chain.invoke({"description": description, "language": language})

        if "```" in generated_output:
            generated_output = generated_output.split("```")[-2].strip()  # Extract code only

        return generated_output



    def translate_code(self, code: str, target_language: str) -> dict:
        model = self.select_model("translation")


        source_language = self.detect_language(code)

        if not isinstance(source_language, str) or source_language.strip() == "":
            source_language = "Unknown"

        if source_language == "Unknown":
            return {"error": "Unable to detect source language."}


        examples = """
        Here are some examples of how to translate code from one language to another:

        **Python to JavaScript Example:**
        **Python Code**:
        ```python
        def add(a, b):
            return a + b
        ```
        **JavaScript Code**:
        ```javascript
        function add(a, b) {{
            return a + b;
        }}
        ```

        **JavaScript to Python Example:**
        **JavaScript Code**:
        ```javascript
        function multiply(a, b) {{
            return a * b;
        }}
        ```
        **Python Code**:
        ```python
        def multiply(a, b):
            return a * b
        ```
        """

        prompt_template = PromptTemplate(
            input_variables=["source_language", "target_language", "code"],
            template=f"""
            You are a programming language translator.

            {examples}

            Now, please translate the following:

            **Source Language**: {{source_language}}
            **Target Language**: {{target_language}}

            **Code to Translate**:
            ```{{source_language}}
            {{code}}
            ```

            **{{target_language}} Code (ONLY return the translated code, no extra text)**:
            """
        )

        chain = prompt_template | model

        translated_code = chain.invoke({
            "source_language": source_language,
            "target_language": target_language,
            "code": code
        }).strip()

        if "```" in translated_code:
            parts = translated_code.split("```")
            for part in parts:
                if part.lower().startswith(target_language.lower()):
                    translated_code = part.split("\n", 1)[-1].strip()
                    break
            else:
                translated_code = parts[-2].strip()

        return {
            "source_language": source_language,
            "target_language": target_language,
            "translated_code": translated_code
        }