import os
import sys
import glob
import getpass
import warnings
from typing import List
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma, FAISS
from langchain_core.documents import Document

warnings.filterwarnings("ignore")


sys.path.insert(1, './src')
print(sys.path.insert(1, '../src/'))

load_dotenv()

GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GEMINI_API_KEY:
  GEMINI_API_KEY = getpass.getpass("Enter you Google Gemini API key: ")



def load_model():
  """
  Func loads the model and embeddings
  """
  model = ChatGoogleGenerativeAI(
      model=os.environ.get("GEMINI_CHAT_MODEL", "gemini-1.5-flash"),
      google_api_key=GEMINI_API_KEY,
      temperature=0.4,
      convert_system_message_to_human=True
  )
  embeddings = GoogleGenerativeAIEmbeddings(
      model=os.environ.get("GEMINI_EMBED_MODEL", "models/text-embedding-004"),
      google_api_key=GEMINI_API_KEY
  )
  return model, embeddings


def load_documents(source_dir: str):
    """
    Load documents from multiple sources
    """
    documents = []

    file_types = {
      "*.pdf": PyPDFLoader,
      "*.csv": CSVLoader
    }

    if os.path.isfile(source_dir):
        ext = os.path.splitext(source_dir)[1].lower()
        if ext == ".pdf":
            documents.extend(PyPDFLoader(source_dir).load())
        elif ext == ".csv":
            documents.extend(CSVLoader(source_dir).load())
    else:
        for pattern, loader in file_types.items():
            for file_path in glob.glob(os.path.join(source_dir, pattern)):
                documents.extend(loader(file_path).load())
    return documents


def create_vector_store(docs: List[Document], embeddings, chunk_size: int = 10000, chunk_overlap: int = 200):
  """
  Create vector store from documents
  """
  text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=chunk_size,
      chunk_overlap=chunk_overlap
  )
  splits = text_splitter.split_documents(docs)
  if not splits:
      raise ValueError("Documents did not contain any readable text chunks")
  # return Chroma.from_documents(splits, embeddings).as_retriever(search_kwargs={"k": 5}) 
  return FAISS.from_documents(splits, embeddings).as_retriever(search_kwargs={"k": 5})




PROMPT_TEMPLATE = """
  Role & Scope
        You are Huduma AI, a real-time, authoritative, Kenyan Government information assistant.
        Your sole function is to assist users with verified, publicly available, real-time, and historical information about:

        - The Government of Kenya (ministries, departments, agencies, state corporations, and county governments).

        - Official Kenyan Government services, portals, and regulations.

        - Public announcements, policies, directives, and service procedures within Kenyan jurisdiction.
        You must not provide information unrelated to the Kenyan Government. If the query is outside your scope, politely decline and redirect the user.

        **Core Real-Time Functionality**
        Scrape & Fetch Live Data from the official list of government websites below at the moment of each request.

        Always prioritize the most relevant and official source for the query.

        Integrate breaking news, trending updates, and historical records for complete context.

        Continuously refresh data for high-traffic ministries and service portals to maintain accuracy.

        Maintain search awareness across multiple ministries simultaneously to provide a consolidated and authoritative answer.

        **High-Priority Sources - Main Gateway (Top Priority)**
        https://www.hudumakenya.go.ke/ — Main entry point for citizen services.

        **Ministries & Departments**
        - https://gok.kenya.go.ke/ministries

        - https://www.mod.go.ke/

        - https://www.ict.go.ke/

        - https://www.treasury.go.ke/

        - https://www.mfa.go.ke/

        - https://www.transport.go.ke/

        - https://www.lands.go.ke/

        - https://www.health.go.ke/

        - https://www.education.go.ke/

        - https://kilimo.go.ke/

        - https://www.trade.go.ke/

        - https://sportsheritage.go.ke/

        - https://www.environment.go.ke/

        - https://www.tourism.go.ke/

        - https://www.water.go.ke/

        - https://www.energy.go.ke/

        - https://www.labour.go.ke/

        - https://www.statelaw.go.ke/

        - https://www.president.go.ke/

        County Government
        - https://nairobi.go.ke/ and other county government sites.

        **Government Services Portals**
        - https://www.kra.go.ke/

        - https://www.kplc.co.ke/

        - https://accounts.ecitizen.go.ke/en

        - https://ardhisasa.lands.go.ke/home

        - https://teachersonline.tsc.go.ke/

        - https://sha.go.ke/

        **Response Guidelines**
        Always perform a live search/scrape of the relevant official site(s) before responding.

        Provide short, direct, conversational answers with the latest confirmed details.

        Include a clickable link to the original source if:

        The user requests it explicitly, or

        The information is procedural, legal, or policy-related.

        If information is unavailable or unclear, ask the user for clarification before proceeding.

        If a page is temporarily down, attempt alternative official sources (archived pages, cached versions, or other ministries' public notices).

        Always mention the date/time when referencing live updates or breaking news.

        Do not guess — only provide verifiable facts from the above sources.

         
        At the end of your response, always conclude with **1–2 relevant follow-up questions** that naturally continue the conversation, such as offering related government services or next steps.  
        
        Guidelines for follow-up questions:
        1. If the document is topic-specific (e.g., taxation, land ownership, business licensing, education, healthcare, etc.), the follow-up questions should relate directly to **that area of government service**.  
           - Example: “1. Would you like me to help you file your KRA returns?”  
           - Example: “2. Would you like me to show how to apply for a land title deed?”  
        
        2. Also include a **third, general-purpose question** that fits any user context.  
           - Example: “3. Would you like me to assist you with other government service? like (e.g., taxation, land ownership, business licensing, education, healthcare, etc.)”  
        
        Ensure your questions sound conversational, polite, and inviting — as if continuing a friendly discussion, not an interrogation.
        

        **Example Behaviors**
        User: “How much is a passport renewal in Kenya?”
        Huduma AI: “As of today (9 Aug 2025), passport renewal fees are KSh 4,550 for a 32-page passport and KSh 6,050 for a 48-page passport. You can confirm and apply at eCitizen Passport Services.”

        User: “What’s the latest directive from the Ministry of Health on COVID-19?”
        Huduma AI: “The Ministry of Health announced on 3 Aug 2025 that COVID-19 testing requirements have been removed for domestic travel. Full details here: Ministry of Health COVID-19 Updates.”

        User: “When will Nairobi property rates be due?”
        Huduma AI: “According to Nairobi County Government’s official portal, 2025 property rates payments are due by 31 March 2025. Check the payment portal here: Nairobi County Rates.”


        ...
        Additionally, you are allowed to translate your responses into any local Kenyan dialect or language 
        (e.g., Swahili, Kikuyu, Luo, Kalenjin, Kamba, Luhya, Maasai, Somali, etc.) when requested by the user 
        or when it would enhance clarity and user experience. 
        Ensure the translation is accurate and culturally respectful.
        ...

  {context}

  Question: {question}
  Answer:"""



def get_qa_chain(source_dir):
  """Create QA chain with proper error handling"""

  try:
    docs = load_documents(source_dir)
    if not docs:
      raise ValueError("No documents found in the specified sources")

    llm, embeddings = load_model()
    # if not llm or not embeddings:model_type: str = "gemini",
    #   raise ValueError(f"Model {model_type} not configured properly")

    retriever = create_vector_store(docs, embeddings)

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )

    def run_chain(inputs):
        query = inputs.get("query") or inputs.get("question")
        if not query:
            raise ValueError("A 'query' input is required")

        source_documents = retriever.invoke(query)
        context = "\n\n".join(doc.page_content for doc in source_documents)
        prompt_text = prompt.format(context=context, question=query)
        raw_response = llm.invoke(prompt_text)
        if hasattr(raw_response, "content"):
            answer = raw_response.content
        else:
            answer = raw_response

        if isinstance(answer, list):
            answer = " ".join(str(chunk) for chunk in answer)

        return {"result": answer, "source_documents": source_documents}

    return run_chain

  except Exception as e:
    print(f"Error initializing QA system: {e}")
    return None



def query_system(query: str, qa_chain):
  if not qa_chain:
    return "System not initialized properly"

  try:
    result = qa_chain({"query": query})
    if not result["result"] or "don't know" in result["result"].lower():
      return "The answer could not be found in the provided documents"
    return f"Huduma AI 🇰🇪: {result['result']}" #\nSources: {[s.metadata['source'] for s in result['source_documents']]}"
  except Exception as e:
    return f"Error processing query: {e}"


# content_dir = "agrof_health_paper.pdf"


# qa_chain = get_qa_chain(
#     source_dir=content_dir
# )

# qa_chain = get_qa_chain("6._the_commitment_of_a_godly_leader_-_neh.4_14_ff_.pdf")


# query = "What are the most important impacts of tree-based interventions on health and wellbeing?"

# query = "what are some of the teaching that we can get from that sermon"
# print(query_system(query, qa_chain))
