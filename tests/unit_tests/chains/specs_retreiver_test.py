from meche_copilot.chains.helpers.specs_retriever import SpecsRetriever
from meche_copilot.esd_toolkit.schemas import Session, SessionConfig
from meche_copilot.utils.config import load_config, find_config

# config_box = load_config(find_config('config.yaml'))
# config = SessionConfig(**config_box)

config = SessionConfig.from_yaml(find_config('config.yaml'))
sess = Session.from_config(config=config)


# fan eq
eq = sess.equipments[2]

specs_retriever_A = SpecsRetriever(doc_retriever=sess.config.doc_retriever, source=eq.sourceA)
relavent_docs = specs_retriever_A.get_relevant_documents(
    query="", 
    refresh_source_docs=False
)

specs_retriever_B = SpecsRetriever(doc_retriever=sess.config.doc_retriever, source=eq.sourceB)
relavent_docs = specs_retriever_B.get_relevant_documents(
    query="", 
    refresh_relavent_docs=True
)