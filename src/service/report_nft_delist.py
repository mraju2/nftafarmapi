from pymongo.errors import DuplicateKeyError, ExecutionTimeout
from settings import USE_MONGO
from service.service_base import ServiceBase
import traceback
from service.asset import Asset
from service.report import Report

class ReportNftDelist(ServiceBase):
    def get_update_asset(self,data):
        try:
            report,report_status=Report().get_one_assetId(data['assetId'])
            reportId,reportId_status=Report().get_one(data['reportId'])
            if report_status !=200:
                 self.logger.error(f"assetId {data['assetId']}")
                 return report,report_status
            if reportId_status !=200:
                self.logger.error(f"assetId {data['reportId']} not found")
                return reportId,reportId_status
            response = Asset().update_one(data['assetId'], {'listed': data['listed']})
            return response     
        except Exception:
            self.logger.error(f"Failure in list_asset method for {data['assetId']} Exception : {traceback.format_exc()}")
            return {
                "error": f"Something went wrong with the process"
            }, 503    
            

