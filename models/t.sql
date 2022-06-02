


drop table if exists md_code_definition;
CREATE TABLE md_code_definition
(

  `code_name` VARCHAR(100)  comment '代码名称',
  `code_desc` VARCHAR(400)  comment '代码描述'


,primary key(code_name)


)
engine=innodb 
default charset=utf8 
comment '代码定义表'
;

CREATE UNIQUE INDEX md_code_definition_idx1 ON md_code_definition(code_name);


drop table if exists md_metadata;
CREATE TABLE md_metadata
(

  `id` VARCHAR(500)  comment '数据id',
  `ancestor` VARCHAR(500)  comment '祖先',
  `name` VARCHAR(100)  comment '数据名字',
  `title` VARCHAR(100)  comment '标题',
  `type` VARCHAR(30)  comment '数据类型',
  `length` int  comment '数据长度',
  `dec` int  comment '小数位',
  `nullable` CHAR(1)  comment '可否为空',
  `defaultvalue` CHAR(1)  comment '缺省值',
  `uiattr` VARCHAR(3000)  comment '界面属性'


,primary key(id)


)
engine=innodb 
default charset=utf8 
comment '元数据'
;

CREATE UNIQUE INDEX md_metadata_idx1 ON md_metadata(id);


drop table if exists md_code_keyvalue;
CREATE TABLE md_code_keyvalue
(

  `code_name` VARCHAR(100)  comment '代码名称',
  `code_key` VARCHAR(500)  comment '代码键',
  `level` int  comment '级别',
  `code_value` VARCHAR(200)  comment '代码值'


,primary key(code_name,code_key)


)
engine=innodb 
default charset=utf8 
comment '代码码值表'
;

CREATE UNIQUE INDEX md_code_keyvalue_idx1 ON md_code_keyvalue(code_name,code_key);
CREATE  INDEX md_code_keyvalue_idx2 ON md_code_keyvalue(code_name);
CREATE  INDEX md_code_keyvalue_idx3 ON md_code_keyvalue(code_name,code_key,level);
