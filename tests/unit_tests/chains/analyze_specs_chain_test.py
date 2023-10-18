from meche_copilot.schemas import *
from meche_copilot.chains.read_design_chain import ReadDesignChain
from meche_copilot.chains.read_submittal_chain import ReadSubmittalChain
from meche_copilot.chains.analyze_specs_chain import AnalyzeSpecsChain
from meche_copilot.utils.config import load_config, find_config
from langchain.callbacks import StdOutCallbackHandler

config = SessionConfig.from_yaml(find_config('session-config.yaml'))
sess = Session.from_config(config=config)

# run read design chain
read_design_chain = ReadDesignChain()
eqs_with_design_data = read_design_chain({'equipments': sess.equipments})

# run read submittal chain
read_submittal_chain = ReadSubmittalChain()
eqs_with_submittal_data = read_submittal_chain({'equipments': eqs_with_design_data})

# run analyze specs chain
analyze_specs_chain = AnalyzeSpecsChain()

analyze_specs_chain.get_spec_results_for_eq_instance()

analyze_specs_chain.analyze_spec_results_for_eq_instance()

eqs_with_analysis = analyze_specs_chain({'equipments': eqs_with_submittal_data})
