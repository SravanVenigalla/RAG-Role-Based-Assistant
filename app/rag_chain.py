from app.config import GROQ_API_KEY
from app.rag_pipeline import get_vector_store

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

def get_rag_chain(role: str, query: str):
    
    vector_store = get_vector_store()

    if role == "c-level":
        retriever = vector_store.as_retriever(search_kwargs={"k": 4})
    elif role == "general":
        retriever = vector_store.as_retriever(search_kwargs={
            "k": 4, "filter": {"role": "general"}})
    else:
        retriever = vector_store.as_retriever(search_kwargs={
            "k": 4, "filter": {"role": {"$in": [role, "general"]}}
        })

    llm = ChatGroq(model="llama-3.1-8b-instant")

    prompt = ChatPromptTemplate.from_template("""
    You are an intelligent role-based company assistant. 
    Your job is to answer user queries strictly based on the role assigned and the provided context. 
    Never reveal or use information outside the user's permitted role. 
    If the query requests information outside their access level, politely refuse.

    User Role: {role}
    User Query: {input}

    Context (from company documents, role-restricted):
    {context}

    Instructions:
    1. Use only the retrieved context to answer the query. 
    2. Always mention the source document(s) when giving an answer.
    3. If the query is outside the role's permissions, respond with:
    "Your role ({role}) does not have access to this information."
    4. If the context is insufficient, say: 
    "I could not find enough information in the available documents for your role."
    5. Keep the answer concise, clear, and professional.""")

    doc_chain = create_stuff_documents_chain(llm, prompt)
    
    chain = create_retrieval_chain(retriever, doc_chain)

    return chain.invoke({"input": query, "role": role})