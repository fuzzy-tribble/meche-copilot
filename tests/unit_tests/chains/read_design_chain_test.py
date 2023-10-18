from meche_copilot.schemas import *
from meche_copilot.chains.read_design_chain import ReadDesignChain
from meche_copilot.utils.config import load_config, find_config
from langchain.callbacks import StdOutCallbackHandler

config = SessionConfig.from_yaml(find_config('session-config.yaml'))
sess = Session.from_config(config=config)

chain = ReadDesignChain()

# chain.read_design_drawings(scoped_eq=sess.equipments)

chain.read_design_schedules(scoped_eq=sess.equipments, show_your_work=True)

res = chain(scoped_eq=sess.equipments)