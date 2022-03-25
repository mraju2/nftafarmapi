""" Service Base """
import abc
import logging

from util.db_util import DBUtil
from util.utils import snake_case
from settings import BLOCK_CHAIN


class ServiceBase(abc.ABC):
    """ Abstract ServiceBase class """

    def __init__(self):
        self.class_name = type(self).__name__
        self.logger = logging.getLogger(self.class_name)
        # self.logger.setLevel(logging.INFO)
        # consoleHandler=logging.StreamHandler()
        # consoleHandler.setLevel(logging.INFO)
        # formatter=logging.Formatter('%(asctime)s-%(name)s-%(levelname)s:%(message)s',datefmt='%m/%d/%y %I:%M:%S %p')
        # consoleHandler.setFormatter(formatter)
        # self.logger.addHandler(consoleHandler)
        self.collection_name = snake_case(self.class_name)
        self.table_name = snake_case(self.class_name)
        if self.class_name not in ["Profile", "Subscription","ProfileFollows"] and BLOCK_CHAIN != "BNB":
            self.collection = DBUtil().get_collection(f"{self.collection_name}_{BLOCK_CHAIN.lower()}")
        else:
            self.collection = DBUtil().get_collection(self.collection_name)