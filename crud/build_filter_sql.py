
def build_filters_sql(table, ns):
	"""
	
	"""
	sql = f"select * from {table} where 1=1"
	for k,v in ns.items():
		if isinstance(v, list):
			sql = "%s and %s in ${%s}$" % (sql, k, k)
		else:
			if v == '_all_':
				continue
			sql = "%s and %s = ${%s}$" % (sql, k, k)
	return sql

