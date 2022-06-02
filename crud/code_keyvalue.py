
"""
## 实现方法
代码以一组数据表形式存储在数据库中， 按照配置，代码表可以存在独立的数据库中也可以存储在业务数据库中
多级代码，代码键值以“.“字符分割，可形成多级代码

其中
	代码定义表定义每个代码的名称
	代码码值表存储各个代码键值和码值

## 数据结构
代码定义表
md_code_definition
{
	code_name,
	code_desc
}

代码码值表
md_code_keyvalue
{
	code_name,
	code_key,
	level,
	code_value
}

"""

from sqlor.dbpools import DBPools

class CodeKeyValue:
	def __init__(self, database):
		self.database = database
		self.db = DBPools()

	async def new_code(self, code_name:str, code_desc):
		"""
		新建一个代码
		"""
		with self.db.sqlorContext(self.database) as sor:
			await sor.C('md_code_definition',
					code_name=code_name,
					code_desc=code_desc)

	async def add_kv(self, code_name:str, code_key:str, code_value:str):
		"""
		新增一个代码
		code_name:代码名称
		code_key:代码键值
		code_value:代码键值
		"""
		level = len(code_key.split('.'))
		with self.db.sqlorContext(self.database) as sor:
			await sor.C('md_code_keyvalue', 
					code_name=code_name,
					code_key=code_key, 
					level=level,
					code_value=code_value)

	async def delete_kv(self, code_name:str, code_key:str):
		"""
		删除一个代码
		code_name:
		code_key:
		"""
		with self.db.sqlorContext(self.database) as sor:
			await sor.D('md_code_keyvalue', 
					code_name=code_name,
					code_key=code_key)

	async def modify_kv(self, code_name:str, code_key:str, code_value:str):
		"""
		修改一个代码值
		code_name:代码名称
		code_key:代码键值
		code_value:新代码键值
		"""

		level = len(code_key.split('.'))
		with self.db.sqlorContext(self.database) as sor:
			await sor.U('md_code_keyvalue', 
				code_name=code_name,
				code_key=code_key,
				level=level,
				code_value=code_value)

	async def get_code_value(self, code_name:str, code_key:str) -> str:
		"""
		得到代码码值
		code_name:代码名称
		code_key:代码键值
		返回值:字符串，如果没找到返回None

		"""
		with self.db.sqlorContext(self.database) as sor:
			r = await sor.R('md_code_keyvalue',
					code_name=code_name,
					code_key=code_key)
			if len(r)>0:
				return r[0]['code_value']
			return None

	async def get_code_list(self, code_name:str, code_key_part:str=None) -> list:
		"""
		得到代码名称的代码列表，如果code_key_part不为空，则获得级联的下级代码的字典
		code_name:代码名称
		code_key:代码键值
		返回值:字符串，如果没找到返回None
		"""
		filter = ''
		ns = {
			'code_name':code_name
		}
		if code_key_part is not None:
			level = len(code_key_part.split('.')) + 1
			ns['level'] = level
			ns['parts'] = code_key_parts + '%'
			filter = ' and level=${level}$ and code_key like ${parts}$'
		sql = '''select * from md_code_keyvalue 
		where code_name=${code_name}$ ''' + filter
		with self.db.sqlorContext(self.database) as sor:
			r = await sor.sqlExe(sql, ns) 
			return r

	def sql_completion(self, sql, codes):
		"""
		sql代码补全，补全每个代码的码值
		sql:原始sql代码
		codes:需要补全的代码数组，每个codes中的code有以下格式：
			{
				code_keyfield,    	sql中键值字段
				code_valuefield,	补充的键值字段
				code_name,			代码名称
			}
		返回值:补全的SQL代码
		局限：补全的sql没有做有效性分析，不能保证能够执行。比如code_keyfield在原始sql的结果字段中不存在，代码库和原始sql的目标数据库不是同一个数据库。

		"""
		i = 0
		dbp = DBPools()
		dbname = dbp.get_dbname(self.database)
		for c in codes:
			sql = '''select a{i}.*, b{i}.code_value as {c['code_valuefield']}
			from ({sql}) as a{i}, {dbname}.code_keyvalue as b{i}
			where a{i}.{c['code_keyfield'] = b{i}.code_key
				and b{i}.code_name = '{c["code_name"]}'
				'''
			i += 1
		return sql
