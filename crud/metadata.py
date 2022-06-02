
import ujson as json
from appPublic.jsonConfig import getConfig
from sqlor.dbpools import DBPools
from ahserver.serverenv import ServerEnv

def getMetaDatabase():
	config = getConfig()
	if config.metadatabase:
		return config.databases[config.metadatabase].get('dbname')
	return None

env = ServerEnv()
env.getMetaDatabase = getMetaDatabase

class Metadata:
	"""
	store meta data in a md_metadata table
	metadata table info:
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
	def __init__(self):
		self.database = getMetaDatabase()
		self.table = 'md_metadata'
		self.db = DBPools()

	async def get_metadata(self, id:str):
		async with self.db.sqlorContext(self.database) as sor:
			x = await sor.R(self.table, {'id':id})
			if len(x) > 0:
				b = {k:v for k,v in x[0].items() \
							if v is not None and k!='ancestor' }
				if len(b.keys()) == len(x[0].keys()) - 1:
					return b
				if x[0].get('ancestor') is None:
					return b
				x = await self.get_metadata(self,x[0].get('ancestor'))
				return x.update(b)
			return None

	async def get_metadata_uiattr(self, id:str):
		async with self.db.sqlorContext(self.database) as sor:
			x = await sor.R(self.table, {'id':id})
			if len(x) > 0:
				ui_attr = x[0].get('ui_attr', None)
				if not ui_attr:
					id = x[0].get('ancestor', None)
					if not id:
						return None
					return await self.get_metadata_uiattr(id)
				return json.loads(ui_attr)
			return None

