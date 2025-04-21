import requests

class MistralLLM:
    def __init__(self, host="http://localhost:11434", model="mistral"):
        self.host = host
        self.model = model

    def query_mistral(self, prompt):
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except Exception as e:
            print(f"❌ Error calling Mistral via Ollama: {e}")
            return "Error generating response"
