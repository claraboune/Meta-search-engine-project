# loggin and monitoring
import logging
import logging.config
import yaml

import MetAPI.user_interface.main_interface as interface


def main():
    # try:
    interface.main()
    # except Exception as e:
    #     logging.error('Ohoh ... Something unexpected happend ...')
    #     logging.error(e, exc_info=True)




if __name__ == "__main__" :
    with open('./MetAPI/config_logger.yml', 'r') as f:
        log_cfg = yaml.safe_load(f.read())
        logging.config.dictConfig(log_cfg)
    logging.info("program starts")
    logging.debug("debug info only")

    main()

    logging.info("program ends")
