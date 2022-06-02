

"""
table info:
md_metadata {
	id,
	ancestor,
	name,
	title,
	type,
	length,
	dec,
	nullable,
	default,
	uiattr

"""
from traceback import print_exc
import codecs
import ujson as json
from sqlor.dbpools import DBPools
from sqlor.filter import DBFilter
from ahserver.baseProcessor import TemplateProcessor
from .metadata import Metadata

class CRUDEngine:
	def __init__(self, processor,  crud_dic:dict):
		self.processor = processor
		self.database = crud_dic['database']
		self.table = crud_dic['table']
		self.db = DBPools()
		self.crud_title = ''
		self.crud_dic = crud_dic
		self.metadata = Metadata()
		self.cmds = {
			'browser':self.build_browser,
			'browser_data':self.build_browser_data,
			'filter':self.build_filter_form,
			'add':self.build_new_data_form,
			'edit':self.build_edit_data_form,
			'delete':self.build_delete_data,
			"new_data":self.build_new_data,
			"edit_data":self.build_edit_data,
			"delete_data":self.build_delete_data
		}

	def is_legal_cmd(self, cmd:str) -> bool:
		return cmd in self.cmds.keys()

	def defaultcmd(self):
		return 'browser'

	async def render(self):
		cmd = self.get_cmd()
		return await self.dispatch(cmd)

	async def dispatch(self, cmd:str):
		f = self.cmds.get(cmd)
		if f:
			return await f()
		return await self.build_crud()

	async def get_uiattr(self, field:str) -> dict:
		if not self.metadata:
			return {}

		id = f'{self.database}.{self.table}.{field}'
		ui = await self.metadata.get_metadata_uiattr(id)
		if ui:
			return ui
		id = field
		ui = await self.metadata.get_metadata_uiattr(id)
		return ui

	def get_cmd(self):
		path_parts = self.processor.path.split('/')
		cmd = ''
		cmd = path_parts[-2]
		if not self.is_legal_cmd(cmd):
			cmd = ''
		return cmd

	def cmdid(self, cmd):
		crud_id = self.crud_dic.get('crud_id', '')
		if cmd == '':
			return f'{crud_id}_{self.database}_{self.table}'
		return f'{crud_id}_{self.database}_{self.table}_{cmd}'

	def cmdurl(self, cmd):
		p = self._cmdurl(cmd)
		return self._env('entire_url')(p)

	def _cmdurl(self, cmd):
		if cmd != '' and not self.is_legal_cmd(cmd):
			return
		path_parts = self.processor.path.split('/')
		ocmd = self.get_cmd()
		if ocmd == cmd:
			return
		
		if self.is_legal_cmd(path_parts[-2]):
			if cmd == '':
				del path_parts[-2]
				return '/'.join(path_parts)
			path_parts[-2] = cmd
			return '/'.join(path_parts)

		path_parts.insert(-1, cmd)
		return '/'.join(path_parts)
		
	def build_menu_dic(self):
		return {
			"widgettype":"Menu",
			"options":{
				"single_expand":True,
				"idField":"id",
				"textField":"label",
				"bgcolor":[0.2,0.2,0.2,1],
				"target":f"root." + self.cmdid(''),
				"data":[
					{
						"id":"browser",
						"label":"Browser",
						"url":self.cmdurl('browser')
					},
					{
						"id":"filter",
						"label":"Filter",
						"url":self.cmdurl('filter')
					},
					{
						"id":"add",
						"label":"Add",
						"url":self.cmdurl('add')
					},
					{
						"id":"edit",
						"label":"Edit",
						"url":self.cmdurl('edit')
					},
					{
						"id":"delete",
						"label":"delete",
						"url":self.cmdurl('delete')
					}
				]
			}
		}

	async def build_crud(self):
		kw = {
				"bar_size":2,
				"bar_at":"top",
				"singlepage":False
		}
		kw.update(self.crud_dic.get('options', {}))
		# kw['left_menu'] = self.build_menu_dic()
		crud_id = self.crud_dic.get('crud_id', '')
		return {
			"id":self.cmdid(''),
			"widgettype":"PagePanel",
			"options":kw,
			"subwidgets":[
				{
					"widgettype":"urlwidget",
					"options":{
						"params":{
						},
						"url":self.cmdurl('browser')
					}
				}
			]
		}

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
		factor = 0.7
		length = field.get('len', 15)
		datatype = field['type']
		if length > 80:
			length = 80
		if 'date' in field['name']:
			return 10 * factor
		return length * factor

	async def get_fields(self):
		fields = []
		async with self.db.sqlorContext(self.database) as sor:
			info = await sor.I(self.table)
			if not info:
				return []
			self.crud_title = info['summary'][0]['title']
			fields = [{
				"name":i['name'],
				"uitype":self.guess_uitype(i),
				"datatype":i['type'],
				"label":i.get('title'),
				"length":i['len'],
				"width":self.set_field_width(i),
				"dec":i['dec']
			} for i in info['fields'] ]
			for f in fields:
				ui = await self.get_uiattr(f['name'])
				if ui:
					f.update(ui)

			return fields

	async def build_new_data_form(self) -> dict:
		"""
		build new data form dic client application needed to
		constructs a add data form widget
		"""
		fields = await self.get_fields()
		opts = {
			"cols":1,
			"labelwidth":0.3,
			"inputheight":1.5,
			"toolbar_at":"top",
			"fields":fields
		}
		print('crud_dic add=', self.crud_dic['actions']['add'])
		nopts = self.crud_dic['actions']['add'].get('options',{})
		opts.update(nopts)
		print(nopts, opts)
		d = {
			"widgettype":"Form",
			"options":opts,
			"title_widget":{
				"widgettype":"Text",
				"options":{
					"otext":self.crud_title,
					"i18n":True
				}
			},
			"binds":[
				{
					"wid":"self",
					"event":"on_submit",
					"actiontype":"multiple",
					"actions":[
						{
							"actiontype":"urlwidget",
							"datawidget":"self",
							"options":{
								"url":self.cmdurl('new_data')
							}
						},
						{
							"actiontype":"script",
							"target":'root.' + self.cmdid(''),
							"script":"self.pop(None)"
						}
					]
				}
			]
		}
		d = self.replace_crud_binds(d, 'add')
		return d

	async def build_new_data(self, *args):
		ns = await self._env('request2ns')()
		db = DBPools()
		async with db.sqlorContext(self.database) as sor:
			await sor.C(self.table, ns)
		return self.message('data added')
		
	async def build_edit_data(self, *args):
		ns = await self._env('request2ns')()
		db = DBPools()
		async with db.sqlorContext(self.database) as sor:
			await sor.U(self.table, ns)
		return self.message('date modified')

	async def build_edit_data_form(self) ->dict:
		"""
		build modify data form dic client application needed to 
		constructs a modify data form widget
		"""
		fields = await self.get_fields()
		ns = await self._env('request2ns')()
		db = DBPools()
		async with db.sqlorContext(self.database) as sor:
			info = await sor.I(self.table)
			primary = info['summary'][0]['primary']
			ns1 = {k:v for k, v in ns.items() if k in primary}
			d = await sor.R(self.table, ns1)
			if len(d) > 0:
				for f in fields:
					f['value'] = d[0][f['name']]

		opts = {
			"cols":1,
			"labelwidth":0.3,
			"inputheight":1.5,
			"toolbar_at":"top",
			"fields":fields
		}
		opts.update(self.crud_dic['actions']['edit'].get('options',{}))
		d = {
			"widgettype":"Form",
			"options":opts,
			"binds":[
				{
					"wid":"self",
					"event":"on_submit",
					"actiontype":"multiple",
					"actions":[
						{
							"actiontype":"urlwidget",
							"datawidget":"self",
							"target":'root.' + self.cmdid(''),
							"options":{
								"url":self.cmdurl('edit_data')
							}
						}
					]
				}
			]
		}
		d = self.replace_crud_binds(d, 'edit')
		return d
		
	async def build_delete_data(self) -> dict:
		ns = await self._env('request2ns')()
		db = DBPools()
		async with db.sqlorContext(self.database) as sor:
			await sor.D(self.table, ns)
		return self.message('data deleted')

	async def build_filter_form(self) -> dict:
		"""
		build filter form dic client application needed  
		to construct filter form widget
		"""
		table_fields = await self.get_fields()
		name_fields = {i['name']:i for i in table_fields }
		tf_names = name_fields.keys()
		filters = self.crud_dic['actions']['filter'].get('filters', None)
		alter_fields = self.crud_dic['actions']['filter'].get('alter_fields', [])
		dbf = DBFilter(filters)
		variables = dbf.get_variables()
		fields = []
		for v, f in variables.items():
			field = name_fields[f]
			field['name'] = v
			fields.append(field)

		for af in alter_fields:
			for f in fields:
				if f['name'] == af['name']:
					f.update(af)

		opts = {
				"cols":1,
				"labelwidth":0.3,
				"inputheight":1.5,
				"toolbar_at":"top",
				"fields":fields
		}
		opts.update(self.crud_dic['actions']['filter'].get('options',{}))
		d = {
			"widgettype":"Form",
			"options":opts,
			"title_widget":{
				"widgettype":"Text",
				"options":{
					"otext":self.crud_title,
					"i18n":True
				}
			},
			"binds":[
				{
					"wid":"self",
					"event":"on_submit",
					"actiontype":"multiple",
					"actions":[
						{
							"actiontype":"script",
							"datawidget":"self",
							"target":'root.' + self.cmdid('browser'),
							"script":"self.loadData(**kwargs)"
						},
						{
							"actiontype":"script",
							"target":'root.' + self.cmdid(''),
							"script":"self.pop(None)"
						}
					]
				}
			]
		}
		d = self.replace_crud_binds(d, 'filter')
		return d
	
	def _env(self, fname):
		return self.processor.run_ns.get(fname, None)

	def user_params_path(self, user):
		request = self._env('request')
		fname = request.path.split('/')[-1]
		fparts = fname.split('.')
		fparts.insert(-1, user)
		path = f'{fname}.{user}'
		fnames = request.path.split('/')
		fnames[-1] = path
		path =  '/'.join(fnames)
		return path
		
	def save_default_params(self, ns):
		user = self._env('user')
		if not user:
			return
		path = self.user_params_path(user)
		url = self._env('entire_url')(path)
		path = self.processor.resource.url2file(url)
		print('realpath=', path)
		with codecs.open(path, 'w', 'utf-8') as f:
			json.dump(ns,f)



	async def get_default_params(self, user):
		try:
			path = self.user_params_path(user)
			url = self._env('entire_url')(path)
			path = self.processor.resource.url2file(url)
			print('realpath=', path, 'url=', url)
			with codecs.open(path, 'r', 'utf-8') as f:
				dic = json.load(f)
				return dic
		except Exception as e:
			print_exc()
			print('get_default_params():', e)
		return {}
		
	async def build_browser_data(self):
		ns = await self._env('request2ns')()
		filters = self.crud_dic['actions']['filter'].get('filters',None)
		async with self.db.sqlorContext(self.database) as sor:
			r = await sor.R(self.table, ns, filters=filters)
			d = [ i.to_dict() for i in r['rows'] ]
			r['rows'] = d
			return r

	async def build_browser(self) -> dict:
		"""
		build data browser dic client application needed to 
		constructs a browser widget
		"""
		entire_url = self._env('entire_url')
		crud_id = self.crud_dic.get('crud_id','')
		table_fields = await self.get_fields()
		actions = self.crud_dic.get('actions')
		exclude_fields = actions['browser'].get('exclude_fields', [])
		extend_fields = actions['browser'].get('extend_fields', [])
		fields = [ f for f in table_fields if f['name'] not in exclude_fields ]
		fields += extend_fields
		if actions['browser'].get('checkbox'):
			checkbox = {
				'name':'_checkbox',
				'uitype':'checkbox',
				'width':1,
				'freeze':True,
				'label':''
			}
			fields.insert(0, checkbox)

		user = self._env('user')
		params = {}
		dic = {}
		if user:
			dic = await self.get_default_params(user)
		if dic == {}:
			dic = await self.get_default_params('default')
		params.update(dic)
		ns = await self._env('request2ns')()
		if ns != {}:
			self.save_user_params(ns)

		params.update(ns)
		d = {
			"id":self.cmdid('browser'),
			"widgettype":"DataGrid",
			"options":{
				"row_height":2,
				"header_css":"header_css",
				"toolbar":{
					"target":f"root.{self.cmdid('')}",
					"executable":True,
					"img_size_c":1,
					"text_size_c":1,
					"toolbar_orient":"H",
					"tool_orient":"horizontal",
					"css_on":"selected",
					"css_off":"normal",
					"tools":[
						{
							"name":"filter",
							"source_on":entire_url('/imgs/crud_filter.png'),
							"source_off":entire_url('/imgs/crud_filter.png'),
							"label":"filter",
							"url":self.cmdurl('filter')
						},
						{
							"name":"add",
							"source_on":entire_url('/imgs/crud_add.png'),
							"source_off":entire_url('/imgs/crud_add.png'),
							"label":"add",
							"url":self.cmdurl('add')
						},
						{
							"name":"edit",
							"source_on":entire_url('/imgs/crud_edit.png'),
							"source_off":entire_url('/imgs/crud_edit.png'),
							"label":"edit",
							"datawidget":f"root.{self.cmdid('browser')}",
							"datamethod":'get_selected_data',
							"url":self.cmdurl('edit')
						},
						{
							"name":"delete",
							"source_on":entire_url('/imgs/crud_del.png'),
							"source_off":entire_url('/imgs/crud_del.png'),
							"label":"delete",
							"datawidget":f"root.{self.cmdid('browser')}",
							"datamethod":'get_selected_data',
							"conform":{
								"size_hint":[0.6,0.6],
								"title":"删除记录",
								"message":"要删除选中的记录码？"
							},
							"url":self.cmdurl('delete')
						}
					]
				},
				"tailer":{
					"info":[
						"total_cnt",
						"curpage"
					]
				},
				"body_css":"body_css",
				"row_normal_css":"normal_css",
				"row_selected_css":"selected_css",
				"dataloader":{
					"page_rows":60,
					"dataurl":self.cmdurl('browser_data'),
					"params":params
				},
				"fields":fields
			},
			"title_widget":{
				"widgettype":"Text",
				"options":{
					"otext":self.crud_title,
					"i18n":True
				}
			}
		}
		d = self.replace_crud_binds(d, 'browser')
		print('browser():return d=', d)
		return d

	def replace_crud_binds(self, dic, cmd):
		binds = self.crud_dic['actions'][cmd].get('binds')
		if binds:
			dic['binds'] = binds
		return dic

	def error(self, errmsg, title=None):
		return {
			'widgettype':'Error',
			'options':{
				'title':title,
				'message':errmsg
			}
		}

	def message(self,  msg, title=None):
		return {
			'widgettype':'Message',
			'options':{
				'title':title,
				'message':msg
			}
		}

class CRUDProcessor(TemplateProcessor):
	@classmethod
	def isMe(self, name):
		return name == 'crud'

	async def path_call(self, request, params={}):
		txt = await super(CRUDProcessor, self).path_call(request, params=params)
		dic = json.loads(txt)
		database = dic['database']
		table = dic['table']
		crud = CRUDEngine(self, dic)
		return await crud.render()

	async def datahandle(self, request):
		self.content = await self.path_call(request)

