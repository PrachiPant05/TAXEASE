from enum import Enum
import os

LLM_PROVIDER = "ollama"

if LLM_PROVIDER == "ollama":
    from langchain_community.llms import Ollama
    llm = Ollama(model="mistral")
else:
    from langchain_community.llms import HuggingFaceHub
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    llm = HuggingFaceHub(
        repo_id="mistralai/Mistral-7B-Instruct-v0.1",
        model_kwargs={"temperature": 0.5, "max_new_tokens": 300}
    )

from tax_agents.document_agent import DocumentAgent
from tax_agents.extraction_agent import ExtractionAgent
from tax_agents.tax_calc_agent import TaxCalcAgent
from tax_agents.report_agent import ReportAgent
from tax_agents.support_agent import SupportAgent


class AgentType(Enum):
    DOCUMENT = "document"
    EXTRACTION = "extraction"
    TAX_CALC = "tax_calc"
    REPORT = "report"
    SUPPORT = "support"


class AssistantAgent:
    def __init__(self):
        self.llm = llm
        self.agents = {
            AgentType.DOCUMENT: DocumentAgent(),
            AgentType.EXTRACTION: ExtractionAgent(),
            AgentType.TAX_CALC: TaxCalcAgent(),
            AgentType.REPORT: ReportAgent(),
            AgentType.SUPPORT: SupportAgent()
        }
        self.current_agent = AgentType.SUPPORT

    def classify_intent(self, user_input: str) -> AgentType:
        prompt = f"""
        Classify this user query into one of the following types:
        - document: for uploading or processing documents
        - extraction: for extracting tax-related information
        - tax_calc: for calculating tax liability
        - report: for generating reports or summaries
        - support: for general FAQs or help

        Query: "{user_input}"
        Respond with only the category keyword.
        """
        response = self.llm.invoke(prompt).strip().lower()

        for agent in AgentType:
            if agent.value == response:
                return agent

        return AgentType.SUPPORT

    def process_input(self, user_input: str) -> str:
        selected_agent = self.classify_intent(user_input)
        self.current_agent = selected_agent
        return self.agents[selected_agent].process_input(user_input)
