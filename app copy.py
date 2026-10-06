import os
import ast
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="AI Code Debugging and Learning Chatbot",
    page_icon="🤖",
    layout="wide"
)

client = None

if API_KEY:
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception:
        client = None


def check_python_syntax(code):
    try:
        ast.parse(code)
        return True, "No syntax errors found."
    except SyntaxError as e:
        return False, (
            f"Syntax Error: {e.msg}\n"
            f"Line: {e.lineno}\n"
            f"Column: {e.offset}"
        )
    except Exception as e:
        return False, str(e)


def detect_common_errors(code, language):
    errors = []

    if language == "Python":
        if "print " in code:
            errors.append("Use print() instead of Python 2 print syntax.")

        if "input(" in code:
            errors.append(
                "input() returns a string. Use int(input()) "
                "when an integer is required."
            )

    elif language in ["C", "C++"]:
        lines = code.splitlines()

        for i, line in enumerate(lines, 1):
            line = line.strip()

            if (
                line
                and not line.startswith("#")
                and not line.startswith("//")
                and not line.endswith((";", "{", "}"))
                and (
                    "=" in line
                    or line.startswith(("int ", "float ", "double ", "char "))
                )
            ):
                errors.append(
                    f"Possible missing semicolon near line {i}."
                )

    elif language == "Java":
        if "public class" not in code:
            errors.append("Java programs normally require a class declaration.")

        if "System.out.println" in code and "System.out.print" in code:
            pass

    return errors


def generate_ai_response(code, language, mode):
    if client is None:
        return (
            "Gemini API key is not configured.\n\n"
            "Add GEMINI_API_KEY to your .env file."
        )

    if mode == "debug":
        prompt = f"""
You are an expert programming teacher and debugging assistant.

Programming language: {language}

User code:
----------------
{code}
----------------

Analyze this code.

Provide:

1. Errors found
2. Explanation of each error
3. Complete corrected code
4. Explanation of the corrected code
5. Expected output
6. Important learning points

Use simple language for a beginner.
"""

    elif mode == "learn":
        prompt = f"""
You are a programming teacher.

Teach a beginner about this {language} program:

----------------
{code}
----------------

Explain:

1. What the program does
2. Variables
3. Functions
4. Keywords
5. Program flow
6. Expected output
7. Important concepts
8. Common mistakes
9. Three practice questions

Use simple language.
"""

    else:
        prompt = f"""
You are an AI programming assistant.

Language: {language}

Code:
----------------
{code}
----------------

Answer the user's programming question clearly and simply.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text

    except Exception as e:
        return f"AI Error: {e}"


st.title("🤖 AI Code Debugging and Learning Chatbot")

st.write(
    "Debug your code, understand errors, get corrected code, "
    "and learn programming concepts."
)

with st.sidebar:
    st.header("⚙️ Settings")

    language = st.selectbox(
        "Programming Language",
        ["Python", "Java", "C", "C++"]
    )

    st.divider()

    st.write("Features")
    st.write("🐞 AI Code Debugging")
    st.write("🔍 Syntax Checking")
    st.write("📚 Code Learning")
    st.write("✅ Corrected Code")
    st.write("💡 Programming Tips")


examples = {
    "Python": """def add(a, b)
    return a + b

print(add(10, 20))
""",

    "Java": """public class Main {
    public static void main(String[] args) {
        int a = 10
        int b = 20;
        System.out.println(a + b);
    }
}
""",

    "C": """#include <stdio.h>

int main() {
    int a = 10;
    int b = 20

    printf("%d", a + b);

    return 0;
}
""",

    "C++": """#include <iostream>
using namespace std;

int main() {
    int a = 10;
    int b = 20

    cout << a + b;

    return 0;
}
"""
}

st.subheader("💻 Enter Your Code")

code = st.text_area(
    "Code",
    value=examples[language],
    height=300,
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns(3)

with col1:
    debug = st.button(
        "🐞 Debug Code",
        use_container_width=True
    )

with col2:
    syntax = st.button(
        "🔍 Check Syntax",
        use_container_width=True
    )

with col3:
    learn = st.button(
        "📚 Learn Code",
        use_container_width=True
    )


if syntax:
    if not code.strip():
        st.warning("Please enter some code.")
    elif language == "Python":
        success, message = check_python_syntax(code)

        if success:
            st.success(message)
        else:
            st.error(message)
    else:
        errors = detect_common_errors(code, language)

        if errors:
            st.warning("Possible issues found:")

            for error in errors:
                st.write("•", error)
        else:
            st.success(
                "No obvious common syntax problems were detected."
            )


if debug:
    if not code.strip():
        st.warning("Please enter some code.")
    else:
        st.subheader("🔎 Code Analysis")

        if language == "Python":
            success, message = check_python_syntax(code)

            if success:
                st.success(message)
            else:
                st.error(message)

        errors = detect_common_errors(code, language)

        for error in errors:
            st.warning(error)

        st.subheader("🤖 AI Debugging Result")

        with st.spinner("AI is analyzing your code..."):
            result = generate_ai_response(
                code,
                language,
                "debug"
            )

        st.markdown(result)


if learn:
    if not code.strip():
        st.warning("Please enter some code.")
    else:
        st.subheader("📚 Learning Explanation")

        with st.spinner("Preparing explanation..."):
            result = generate_ai_response(
                code,
                language,
                "learn"
            )

        st.markdown(result)


st.divider()

st.subheader("💬 Ask the AI")

question = st.text_input(
    "Ask a programming question"
)

if st.button("Send Question"):
    if not question.strip():
        st.warning("Please enter a question.")
    elif client is None:
        st.error("Gemini API key is not configured.")
    else:
        prompt = f"""
You are a helpful programming teacher.

Programming language: {language}

User question:
{question}

Answer clearly and simply.
Give examples when useful.
"""

        with st.spinner("Thinking..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

                st.markdown(response.text)

            except Exception as e:
                st.error(f"Error: {e}")


st.caption(
    "AI Code Debugging and Learning Chatbot"
)