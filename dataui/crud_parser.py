import os
import sys
import uitypes
import asyncio
from appPublic.jsonConfig import getConfig
from appPublic.folderUtils import ProgramPath
from sqlor.dbpools import DBPools
from appPublic.myTE import MyTemplateEngine
from ahserver.baseProcessor import TemplateProcessor

class CrudParser:
	def __init__(self, frontend, metadb=None):
		self.frontend = frontend
		self.metadb = metadb
		basepath = os.path.join(os.path.dirname(__file__), 'tmpl');
		paths = [basepath, os.path.join(basepath, self.frontend)]
		self.te = MyTemplateEngine(paths)
	
	def guess_uitype(self, field):
		if 'date' in field['name']:
			return 'date'
		length = field.get('len', 0)
		datatype = field['type']
		if datatype in ['int', 'long', 'integer']:
			return 'int'
		if datatype in ['float', 'double']:
			return 'float'
		if datatype == 'text':
			return 'text'
		if datatype == 'str' and length > 80:
			return 'text'
		return 'str'

	def set_field_width(self, field):
		factor = 20 * 0.7
		length = field.get('len', 15)
		datatype = field['type']
		if length > 80:
			length = 80
		if 'date' in field['name']:
			return 10 * factor
		return length * factor

	async def get_uiparams(self, metadata, name):
		if not metadata:
			return {}

		id = f'{self.database}.{self.table}.{field}'
		ui = await metadata.get_metadata_uiattr(id)
		if ui:
			return ui
		id = field
		ui = await metadata.get_metadata_uiattr(id)
		return ui

	async def render(self, cmd, opts):
		database = opts['database']
		table = opts['table']
		self.database = database
		self.table = table
		db = DBPools()
		metadata = None
		async with db.sqlorContext(database) as sor:
			info = await sor.I(table)
			dic = {
				"database":database,
				"table":table,
				"title":info['summary'][0]['title'],
				"dataurl":"test_url",
				"fields":await self.get_fields(metadata, info['fields'])
			}
			cmd_dic = opts.get(cmd)
			if cmd_dic:
				if cmd_dic.get('alter'):
					self.alter_fields(dic, cmd_dic['alter'])
				if cmd_dic.get('exclude'):
					self.exclude_fileds(dic, cmd_dic['exclude'])
				if cmd_dic.get('include'):
					self.include_fields(dic, cmd_dic['include'])

			tmpl = f'crud_{cmd}.tmpl'
			s = self.te.render(tmpl, dic)
			return s

	def alter_fields(dic, alters):
		for name, d in alters.items():
			for f in dic['fields']:
				if f['name'] == name:
					f.update(d)
					break
	
	def exclude_fields(dic, excludes):
		for name in excludes:
			fields = dic['fields'].copy()
			dic['fields'] = [ f for f in fields if f['name'] != name ]

	def include_fields(dic, include):
		dic['field'] += include

	async def get_fields(self, metadata, fields, mode='view'):
		"""
		this is fowr bricks frontend framework

		argument opts has the following attributes:
		opts = {
			database:
			table:
			filters:
			extend:
		}
		mode is one of ['view', 'input']

		return:
		 a json object cntains the fields info
		"""

		fields = [{
			"name":i['name'],
			"uitype":self.guess_uitype(i),
			"datatype":i['type'],
			"label":i.get('title'),
			"length":i['len'],
			"width":self.set_field_width(i),
			"dec":i.get('dec', None)
		} for i in fields ]
		
		for f in fields:
			ui = await self.get_uiparams(metadata, f)
			if ui:
				f.update(ui)

		if mode == 'view':
			for f in fields:
				f['readonly'] = True
		return fields

async def crud_render(cmd, crud_json_file):
	with codecs.open(crud_json_file) as f:
		d = json.load(f)
		cp = CrudParser(frontend='bricks')
		s = await cp.render(cmd, d)
		return s

async def main():
	cmd = sys.argv[2]
	jsonfile = sys.argv[1]
	s = await crud_render(cmd, jsonfile)
	print(s)

class BricksCRUDProcessor(TemplateProcessor):
	"""
	accept json data from frontend with such attributes:
	{
		database:
		table
	}
	"""
	@classmethod
	def isMe(self, name):
		return name == 'bricks_crud'

	async def run_pyscript(txt):
		lines = [ '\t' + l for l in txt.split('\n') ]
		txt = "async def myfunc(request, **ns):\n' + '\n'.join(lines)
		lenv = self.run_ns.copy()
		exec(txt, lenv, lenv)
		f = lenv['myfunc']
		return await f(request, **lenv)

	async def path_call(self, request, params={}):
		self.run_ns.update(params)
		txt = await super(CRUDProcessor, self).path_call(request, 
										params=self.run_ns)
		cmd = params_kw.get('command', 'browser')
		dic = json.loads(txt)
		database = dic['database']
		table = dic['table']
		cp = CrudParser(frontend='bricks')
		s = await cp.render(cmd, d)
		if cmd in [ "select", "insert", "update", "delete" ]:
			s = self.run_pyscript(s)
		return s

	async def datahandle(self, request):
		self.content = await self.path_call(request)

if __name__ == '__main__':
	import os
	import sys
	import json
	import codecs

	if len(sys.argv) > 3:
		print(f'{sys.argv[0]} jsonfile cmd')
		sys.exit(1)

	p = os.getcwd()
	config = getConfig(p, {
				'workdir':p,
				'programPath':ProgramPath()})
	DBPools(config.databases)
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
