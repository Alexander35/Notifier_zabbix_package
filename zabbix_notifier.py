from general_server_client import GeneralClient, GeneralMachine
from protobuf_asset import msg_pb2
from pyzabbix import ZabbixAPI
import json
import argparse

class ZabbixNotifier(GeneralClient):
	"""send info from zabbix"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		try:
			self.zapi = ZabbixAPI(
					url=self.get_config('ZABBIX','Url'), 
					user=self.get_config('ZABBIX','User'), 
					password=self.get_config('ZABBIX','Password')
				)
			self.Request_list = json.load(open('requests.json'))
		except Exception  as exc:
			self.logger.error('Unable to init a Notifier {}'.format(exc))	
			quit(1)	

	def search_reqest(self, req, num):
		self.logger.info('Perform a request {}'.format( self.Request_list[req][num]))
		return self.Request_list[req][num]	

	def request(self, req, num):
		result = self.zapi.do_request(
				req, 
				self.search_reqest(req, num)
			)
		self.logger.info('request result \n{}\n'.format(result))
		MSG = self.prepare_msg(result, '{} [{}]'.format(req, num))
		self.send(MSG)

	def prepare_msg(self, raw_data, request):
		Msg = msg_pb2.Msg()
		Msg.title = request
		Msg.text = json.dumps(raw_data['result'], indent=4)
		Msg.tagline = '#Zabbix'
		return Msg.SerializeToString()
		
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--config", dest="conf", help="configuration file name", default="config.ini")
	parser.add_argument("-l", "--log", dest="log", help="log file name", default="ZabbixNotifier")
	parser.add_argument("task", default=None)
	parser.add_argument("number", type=int, default=None)
	args = parser.parse_args()
	ZN = ZabbixNotifier(ConfigName=args.conf, LoggerName=args.log)
	ZN.request(args.task, args.number)

if __name__ == '__main__':
	main()