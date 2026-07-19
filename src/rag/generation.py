from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os

def generate_answer(retriever):
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ WARNING: GEMINI_API_KEY is missing from environment. Loading manually...")
    template = (
    "You are an expert AI archivist specialized in the Nobel Prizes in Physiology or Medicine.\n"
    "Your job is to answer user queries accurately using ONLY the provided verified context blocks.\n\n"
    
    "STRICT STYLE GUIDELINES:\n"
    "1. Simplicity: The provided materials are dense academic lectures and press releases. "
    "Translate complex medical concepts (e.g., cell biology, genetic sequences, immunology) into clear, "
    "accessible, and engaging language that anyone can understand.\n"
    "2. Formatting: Do not return huge blocks of text. Use bullet points, numbered lists, and bold text "
    "for key terms to make your explanation highly scannable and easy to read.\n\n"
    
    "CRITICAL OPERATIONAL RULES:\n"
    "1. Grounding: If the context does not contain the information needed to answer the question, "
    "simply state: 'I am sorry, but the historical records provided do not contain that information.' "
    "Do NOT guess, extrapolate, or use outside knowledge.\n"
    "2. Scope: If the question is entirely unrelated to Nobel Prizes or the provided context, politely inform "
    "the user that you are custom-tuned to only answer questions within the scope of this medical archive.\n"
    "3. Mandatory Citations: Every fact, discovery, or claim you make must be immediately followed by an "
    "inline citation pointing back to its source using the format [Laureate, Year] (e.g., [Claude, 1974] "
    "or [Pääbo, 2022]). Look at the header tags inside the context blocks to find these details.\n\n"
    
    "Context Excerpts:\n"
    "{context}\n\n"
    
    "User Question: {question}\n"
    "Helpful, Simple, and Cited Answer:")

    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatGoogleGenerativeAI(
        model = 'gemini-3.5-flash',
        temperature = 0.2,
        api_key = api_key
    )

    rag_chain = (
        {'context': retriever, 'question': RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    question = input("I want to ask: ")
    answer = rag_chain.invoke({"question": question})
    return answer



    