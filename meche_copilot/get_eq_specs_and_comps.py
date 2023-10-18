import pandas as pd
from loguru import logger
from meche_copilot.schemas import ScopedEquipment
from meche_copilot.chains.lookup_specs_chain import get_spec_retrieval_chain

def get_ws_specs(ws: dict) -> dict:
    # TODO - get (SPEC, PAGE) for each spec in the ws using specA ref docs
    # TODO - get (SPEC, PAGE) for each spec in the ws using specB ref docs
    return ws

def validate_ws_specs(ws: dict) -> dict:
    # TODO - run validate specs by using mupdf to each for spec on page for each char in ws and put FOUND or NOT FOUND in the validation column
    return ws

def compare_ws_specs(ws: dict) -> dict:
    # TODO - run compare specs chain
    return ws

def parse_ws_specs_results(ws: dict, eq: ScopedEquipment) -> ScopedEquipment:
    # TODO - turn the dict into Equipment
    return eq


def get_eq_specs_and_comps(eq: ScopedEquipment) -> ScopedEquipment:
    eq_specs_ws = {}
    eq_specs_ws['spec description'] = eq.char_descs

    for i, inst in enumerate(eq.instances):
        char_results = {key: "(SPEC, PAGE)" for key in eq.char_descs.keys()}
        eq_specs_ws[inst.inst_name] = char_results
    df = pd.DataFrame(eq_specs_ws)
    logger.debug(f"eq_type: {eq.eq_type}")
    logger.debug(f'specs_worksheet:\n{df.to_markdown()}')
    
    try:
        # GET SPECS, VALIDATE SPECS, COMPARE SPECS
        logger.info(f'Getting specs for {eq.eq_type}')
        eq_specs_ws_res = get_ws_specs(eq_specs_ws, eq.eq_type)
        if eq_specs_ws_res is not None:
            logger.info(f'Validating specs for {eq.eq_type}')
            eq_specs_ws_res = validate_ws_specs(eq_specs_ws_res)
            if eq_specs_ws_res is not None:
                logger.info(f'Comparing specs for {eq.eq_type}')
                eq_specs_ws_res = compare_ws_specs(eq_specs_ws_res)
                if eq_specs_ws_res is not None:
                    logger.info(f'Parsing specs results for {eq.eq_type}')
                    eq = parse_ws_specs_results(eq_specs_ws_res, eq)
            else:
                logger.warning(f"Couldn't validate specs for {eq.eq_type}. Returning results with NO VALIDATIONS")
                eq = parse_ws_specs_results(eq_specs_ws_res, eq)
        else:
            logger.warning(f"Couldn't get specs for {eq.eq_type}. Returning original eq object")
            return eq

    except Exception as e:
        logger.error(f"Couldn't fillout specs worksheet for {eq.eq_type}: {e}", exc_info=True)
        raise e