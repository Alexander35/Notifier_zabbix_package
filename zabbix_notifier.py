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

	def search_reqest(self, req, req_name):
		result = [js_res for js_res in self.Request_list[req] if 'req_name' in js_res if js_res['req_name'] == req_name]
		if result == []:
			self.logger.error('Can not find the {}'.format(req_name))
			quit(0)
		del result[0]['req_name']
		return result[0]

	def request(self, req, req_name):
		result = self.zapi.do_request(
				req, 
				self.search_reqest(req, req_name)
			)
		self.logger.info('request result \n{}\n'.format(result))
		MSG = self.prepare_msg(result, '{} [{}]'.format(req, req_name))
		self.send(MSG)

	def prepare_msg(self, raw_data, request):
		# nothing to send
		if raw_data['result'] == []:
			quit(0) 
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
	parser.add_argument("req_name", default=None)
	args = parser.parse_args()
	ZN = ZabbixNotifier(ConfigName=args.conf, LoggerName=args.log)
	ZN.request(args.task, args.req_name)

if __name__ == '__main__':
	main()