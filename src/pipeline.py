import os
import time

import pydash as py_
import yaml
import random
import requests

from utils.interact import SmartContractInteractor
from bson.objectid import ObjectId
ROUND_STATUS = {
    "Ready": 0,
    "Training": 1,
    "TrainingFailed": 2,
    "Checking": 3,
    "Checked": 4,
    "Aggregating": 5,
    "Testing": 6,
    "End": 7,
    "ChoseAggregator": 8
}


class Pipeline(object):
    def __init__(self, provider, chain_id, caller, private_key, fl_contract_abi, storage_path):
        self.smc = SmartContractInteractor(provider, chain_id, caller, private_key)
        self.fl_contract_abi = fl_contract_abi
        self.storage_path = storage_path
        pass

    def encode_id(self, object_id: str):
        # from str to int
        integer_id = int(str(object_id), 16)
        return integer_id

    def decode_id(self, integer_id: int):
        # from int to str
        object_id = hex(integer_id)[2:]
        return object_id

    def __get_ss_info(self, ss_id):
        ss_info = self.smc.call(self.fl_contract_abi, "sessionById", ss_id)
        sessionId = py_.get(ss_info, 0)
        owner = py_.get(ss_info, 1)
        performanceReward = py_.get(ss_info, 2)
        baseReward = py_.get(ss_info, 3)
        maxRound = py_.get(ss_info, 4)
        currentRound = py_.get(ss_info, 5)
        maxTrainerInOneRound = py_.get(ss_info, 6)
        status = py_.get(ss_info, 7)
        resp = {
            "sessionId": sessionId,
            "owner": owner,
            "performanceReward": performanceReward,
            "baseReward": {
                "trainingReward": baseReward[0],
                "checkingReward": baseReward[1],
                "aggregatingReward": baseReward[2],
                "testingReward": baseReward[3]
            },
            "maxRound": maxRound,
            "currentRound": currentRound,
            "maxTrainerInOneRound": maxTrainerInOneRound,
            "status": status
        }
        return resp

    def __get_current_status(self, ss_id):
        ss_info = self.__get_ss_info(ss_id)
        return py_.get(ss_info, "status")

    def __get_round(self, ss_id):
        ss_info = self.__get_ss_info(ss_id)
        return py_.get(ss_info, "currentRound")

    def __waiting_stage(self, ss_id, expect_stages):
        if not isinstance(expect_stages, list):
            expect_stages_list = [expect_stages]
        else:
            expect_stages_list = expect_stages
        print(f"Waiting the stage {list(ROUND_STATUS.keys())[expect_stages]}")
        while True:
            time.sleep(3)
            stage = self.__get_current_status(ss_id)
            if stage in expect_stages_list:
                break
        print(f"The stage turned into {list(ROUND_STATUS.keys())[expect_stages]}")
        return

    def __call__(self):
        # 0: create network + upload to server
        global_model_id, param_id = self.__create_network()
        # 1: Create Session
        ss_id = self.__create_session(global_model_id, param_id)
        while True:
            self.__waiting_stage(ss_id, ROUND_STATUS["Checked"])
            # 2: select_candidate_aggregator
            self.__select_candidate_aggregator(ss_id)
            if self.__get_round(ss_id) == self.__get_ss_info(ss_id)["maxRound"] - 1:
                break
                self.__waiting_stage(ss_id, ROUND_STATUS["End"])
        return

    def __create_network(self):
        global_model_p = "/Users/hienhuynhdang/Documents/UIT/kltn/FLOwner/storage/64a9c49810a8cd45568b11a7.pt"
        param_id_p = "/Users/hienhuynhdang/Documents/UIT/kltn/FLOwner/storage/64a9c49810a8cd45568b11a8.pth"
        self.__upload_file(global_model_p)
        self.__upload_file(param_id_p)
        global_model_id = self.encode_id(os.path.basename(global_model_p).split(".pt")[0])
        param_id = self.encode_id(os.path.basename(param_id_p).split(".pth")[0])
        return global_model_id, param_id

    def __create_session(self, global_model_id, param_id):
        session_id = self.encode_id(str(ObjectId()))
        value_random_client_side = 1
        max_round = 3
        max_trainer_in_oneRound = 5
        exp_train = 3 * 86400
        exp_check = 3 * 86400
        exp_aggregate = 3 * 86400
        exp_test = 3 * 86400

        tx_receipt = self.smc.transact(
            self.fl_contract_abi,
            "createSession",
            session_id,
            value_random_client_side,
            max_round,
            max_trainer_in_oneRound,
            global_model_id,
            param_id,
            exp_train,
            exp_check,
            exp_aggregate,
            exp_test,
            value=int(0.1 * (10 ** 18))
        )
        assert tx_receipt["status"] != 0, "CreateSession failed"
        return session_id

    def __select_candidate_aggregator(self, ss_id):
        # FIXME: choose candidate
        candidates = self.smc.call(self.fl_contract_abi, "selectCandidateAggregator", ss_id)
        candidate_encode = random.randint(0, 4)
        tx_receipt = self.smc.transact(self.fl_contract_abi, "submitIndexCandidateAggregator", ss_id, candidate_encode)
        time.sleep(5)
        return bool(int(tx_receipt['status']))

    def __upload_file(self, path_):
        url = "http://54.251.217.42:7020/v1/api/fl/upload-file"
        files = {'file': open(path_, 'rb')}
        response = requests.request("POST", url, files=files)
        print(response.json())
