from meche_copilot.schemas import *
from meche_copilot.chains.read_submittal_chain import ReadSubmittalChain
from meche_copilot.utils.config import load_config, find_config
from langchain.callbacks import StdOutCallbackHandler

config = SessionConfig.from_yaml(find_config('session-config.yaml'))
sess = Session.from_config(config=config)

chain = ReadSubmittalChain()

chain.read_submittal_data(scoped_eq=sess.equipments, show_your_work=True)

pump_eq = sess.equipments[0]
pump_eq.instances[0].design_uid = 'P-1A'

chain.read_submittal_data(scoped_eq=[pump_eq], show_your_work=True)

res = chain(scoped_eq=sess.equipments)

