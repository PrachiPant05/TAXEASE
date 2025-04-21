class SupportAgent:
    def answer_query(self, query: str) -> str:
        faqs = {
            "due date": "The tax filing due date is typically July 31st for individuals.",
            "pan card": "PAN (Permanent Account Number) is a unique identifier for taxpayers in India.",
            "section 80c": "Under Section 80C, you can claim deductions up to ₹1.5 lakh for investments like ELSS, PPF, LIC, etc.",
        }

        for keyword, answer in faqs.items():
            if keyword in query.lower():
                return answer

        return "Sorry, I couldn't find an answer. Please refer to the official tax portal or try rephrasing."
