import ollama


SYSTEM_PROMPT = """You are an expert embedded systems and robotics engineer.
Generate clean, well-commented code.
Output ONLY the code — no explanations before or after.
Include brief inline comments explaining each section."""


def generate_code(robot: str, controller: str,
                    task: str, language: str = "Arduino C++") -> str:

    prompt = f"""Generate {language} code for the following:

Robot:      {robot}
Controller: {controller}
Task:       {task}

Requirements:
- Include all necessary library imports
- Add pin definitions as constants at the top
- Include setup() and loop() for Arduino, or main() for Python
- Add comments explaining each step
- Handle edge cases (limits, safety checks)

Output only the code."""

    resp = ollama.chat(
        model="phi3",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt}
        ]
    )
    return resp["message"]["content"]