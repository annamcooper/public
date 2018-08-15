import pandas as pd
import re
import numpy as np
import datetime
from pathlib import Path
import os
import sys
import codecs
import psycopg2
import hashlib
import logging

def begin():
	print(79*'-')

def end():
	print(79*'-')
	print('\n')

current_filename = os.path.basename(sys.argv[0])
current_filepath = Path(current_filename).absolute()

log = 'logfile.log'
log_filepath = Path(log).absolute()

logging.basicConfig(filename='{0}'.format(log), format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

begin()
print('RUNNING FILE: {0}...'.format(current_filepath))
logging.info('RUNNING FILE: {0}...'.format(current_filepath))
end()

begin()
print('LOG FILEPATH IS: {0}'.format(log_filepath))
logging.info('LOG FILEPATH IS: {0}'.format(log_filepath))
end()

project = 'njsw'
pu = 'p0201301'
file_type = 'dues'
filename = '1804-02test.txt'
dues_date_cycle = '201804_2'
cycle = dues_date_cycle[-1:]
year_month = pd.Period(dues_date_cycle[:-2], 'M')

begin()
dues_filepath = 'I:/!Data/NJSW/{0}/original_dues_files_copy/{1}'.format(pu, filename)
print('PROCESSING DUES FILE: {0}'.format(dues_filepath))
logging.info('PROCESSING DUES FILE: {0}'.format(dues_filepath))
end()

target_filepath = 'I:/!Data/NJSW/{0}/imports/{1}/01_dues_base/'.format(pu, dues_date_cycle)

date = datetime.date.today().strftime('%Y%m%d')
postgres_filename = '{0}_{1}_{2}_{3}_{4}_postgres.csv'.format(date, project, pu, file_type, dues_date_cycle)

begin()
with open(dues_filepath, 'rb') as file:
	line_count = 0
	for line in file:
		line_count += 1

print('THIS DUES FILE HAS {0} ROWS. CHECKING FOR NON-ASCII CHARACTERS...'.format(line_count))
logging.info('THIS DUES FILE HAS {0} ROWS. CHECKING FOR NON-ASCII CHARACTERS...'.format(line_count))

with codecs.open(dues_filepath, encoding='ascii') as file:
	count = 0
	for i in range(line_count):
		try:
			file.readline()
		except:
			count += 1
			num = i+1
			print('CHECK! LINE {0} HAS NON-ASCII CHARACTERS.'.format(num))
			logging.error('CHECK! LINE {0} HAS NON-ASCII CHARACTERS.'.format(num))
	if count != 0:
		print('\nEXITING PROGRAM...')
		logging.info('EXITING PROGRAM...')
		end()
		sys.exit()
	else:
		print('\nNO NON-ASCII CHARACTERS. CONTINUE...')
		logging.info('NO NON-ASCII CHARACTERS. CONTINUE...')
		end()

df = pd.read_table(dues_filepath, header=None, names=['uuid','key_type','filler1','auth_dept_code','loc_code','last_name','class','whitespace1','dues_rate','home_address','home_city','home_state','home_zip5','home_zip4','member_type','bu','job_title_code','paid_dues','biweekly_wage','filler3','gender','filler4','anniversary','increment_step','filler5','not_in_pay_status','filler6','misc_deduct'], na_values=[], keep_default_na=False, dtype=str)

df.misc_deduct = df.uuid.str[168:173]
df.filler6 = df.uuid.str[164:168]
df.not_in_pay_status = df.uuid.str[163:164]
df.filler5 = df.uuid.str[153:163]
df.increment_step = df.uuid.str[149:153]
df.anniversary = df.uuid.str[143:149]
df.filler4 = df.uuid.str[134:143]
df.gender = df.uuid.str[133:134]
df.filler3 = df.uuid.str[130:133]
df.biweekly_wage = df.uuid.str[123:130]
df.paid_dues = df.uuid.str[119:123]
df.job_title_code = df.uuid.str[114:119]
df.bu = df.uuid.str[113:114]
df.member_type = df.uuid.str[112:113]
df.home_zip4 = df.uuid.str[108:112]
df.home_zip5 = df.uuid.str[102:107]
df.home_city = df.uuid.str[77:102]
df.home_address = df.uuid.str[52:77]
df.dues_rate = df.uuid.str[48:52]
df.whitespace1 = df.uuid.str[40:48]
df['class'] = df.uuid.str[38:40]
df.last_name = df.uuid.str[18:38]
df.loc_code = df.uuid.str[16:18]
df.auth_dept_code = df.uuid.str[13:16]
df.filler1 = df.uuid.str[10:13]
df.key_type = df.uuid.str[9:10]
df.uuid = df.uuid.str[:9]
df.pu = pu[1:]
df['barg_unit'] = ''
df['branch'] = ''
df.time_period = year_month
df.cycle = cycle

begin()
print('CHECKING FOR AND, IF THERE, DELETING LAST BAD ROW...')
logging.info('CHECKING FOR AND, IF THERE, DELETING LAST BAD ROW...')
last_row = df[-1:]
last_row_social = last_row.uuid
last_row_social_first_letter = last_row_social.str[0]

for i in last_row_social_first_letter:
	if i == 'Z':
		print('\n--> BAD LAST ROW DELETED. CONTINUE...')
		logging.info('BAD LAST ROW DELETED. CONTINUE...')
		df = df[:-1]
	else:
		print("--> ERROR! THE LAST ROW'S SOCIAL DOES NOT BEGIN WITH 'Z'. CHECK WITH DUES TO SEE IF SOMETHING HAS CHANGED.")
		logging.error("THE LAST ROW'S SOCIAL DOES NOT BEGIN WITH 'Z'. CHECK WITH DUES TO SEE IF SOMETHING HAS CHANGED.")
		sys.exit()
end()

begin()
length = len(df.index)
print("THIS DUES FILE NOW CONTAINS {0} ROWS...".format(length))
logging.info("THIS DUES FILE NOW CONTAINS {0} ROWS...".format(length))

end()

begin()
print("STRIPPING ALL WHITESPACE...")
for column in df.columns:
	df[column] = df[column].str.strip()
end()

begin()
print("CONVERT ALL MULTIPLE SPACES TO ONE SPACE...")
pattern = re.compile(r' {2,}')
for column in df.columns:
	df[column] = df[column].str.replace(pattern, r' ')
end()

begin()
print("TURNING BLANKS INTO NaNs...")
df = df.apply(lambda x: x.str.strip()).replace('', np.nan)
end()

begin()
print("CHECKING IF THE 'UUID' COLUMN IS THE PRIMARY KEY...")
logging.info("CHECKING IF THE 'UUID' COLUMN IS THE PRIMARY KEY...")

begin()
print("SPLITTING 'LAST NAME' INTO 'FIRST NAME', ON LAST COMMA FROM END...")
df['last_name'], df['first_name'] = df['last_name'].str.rsplit(',', 1).str
end()

begin()
print("SPLITTING 'FIRST NAME' INTO 'MIDDLE NAME', ON LAST SPACE FROM END...")
df['first_name'], df['middle_name'] = df['first_name'].str.rsplit(' ', 1).str
end()

begin()
print("SPLITTING 'HOME CITY' INTO 'HOME STATE', ON LAST SPACE FROM END...")
df['home_city'], df['home_state'] = df['home_city'].str.rsplit(' ', 1).str
end()

begin()
print("PROPER-CASING 'LAST_NAME', 'FIRST_NAME', 'MIDDLE_NAME', 'HOME_ADDRESS' AND 'HOME_CITY'...")

proper = ['last_name', 'first_name', 'middle_name', 'home_address', 'home_city']

for column in proper:
	df[column] = df[column].str.title()
end()

begin()
print("CHANGING 'MISC_DEDUCT' TO INGTEGER...")
df.misc_deduct = df.misc_deduct.astype(int)

try:
	assert df.misc_deduct.dtype == 'int32'
	print('--> MISC DEDUCT IS INT32')
	logging.info('--> MISC DEDUCT IS INT32')
	end()
except:
	end()
	logging.error("MISC DEDUCT IS NOT INT32!")
	sys.exit('--> ERROR! MISC DEDUCT IS NOT INT32')

begin()
print("CHANGING 'DUES_RATE', 'PAID_DUES' AND 'BIWEEKLY_WAGE' TO FLOAT...")
floats = ['dues_rate', 'paid_dues', 'biweekly_wage']

for column in floats:
	df[column] = df[column].apply(lambda x:int(x)).apply(lambda x:float(x/100))
end()


begin()
print("ADDING 'BARG UNIT' AND 'BRANCH' COLUMNS")
logging.info("ADDING 'BARG UNIT' AND 'BRANCH' COLUMNS")
df.loc[df.bu == 'A', ['barg_unit', 'branch']] = 'Administrative and Clerical', 'Executive'
df.loc[df.bu == 'R', ['barg_unit', 'branch']] = 'Primary Level Supervisor', 'Executive'
df.loc[df.bu == 'P', ['barg_unit', 'branch']] = 'Professional', 'Executive'
df.loc[df.bu == 'S', ['barg_unit', 'branch']] = 'Secondary Level Supervisor', 'Executive'
df.loc[df.bu == 'G', ['barg_unit', 'branch']] = 'Judiciary', 'Judicial'
df.loc[df.bu == 'U', ['barg_unit', 'branch']] = 'Judiciary', 'Judicial'
df.loc[df.bu == '6', ['barg_unit', 'branch']] = 'Judiciary', 'Judicial'
df.loc[df.bu == '7', ['barg_unit', 'branch']] = 'Judiciary', 'Judicial'
end()

def check_columns(column, values):
	begin()
	print("CHECKING IF THE '{0}' COLUMN HAS THE EXPECTED VALUES...".format(column.upper()))
	logging.info("CHECKING IF THE '{0}' COLUMN HAS THE EXPECTED VALUES...".format(column.upper()))
	try:
		assert df[column].isin(values).all()
		print("THE '{0}' HAS THE EXPECTED VALUES. CONTINUE...".format(column.upper()))
		logging.info("THE '{0}' HAS THE EXPECTED VALUES. CONTINUE...".format(column.upper()))
		final = end()
	except:
		print('\n', df.loc[~df[column].isin(values), ['uuid', 'last_name', column]])
		print("\n--> ERROR! THE '{0}' COLUMN HAS AN UNEXPECTED VALUES. EXITING PROGRAM...".format(column.upper()))
		logging.error("THE '{0}' COLUMN HAS AN UNEXPECTED VALUES. EXITING PROGRAM...".format(column.upper()))
		end()
		final = sys.exit()
	return final

bu_values = ['&','6','7','A','G','P','R','S','U','V','X','Y']
class_values = ['RF', 'RP']

check_columns('bu', bu_values)
check_columns('class', class_values)

begin()
print("CHANGING ALL NaNs TO NoneType...")
df = df.where((pd.notnull(df)), None)
end()

begin()
print("CHECKING FOR COLUMNS WITH ANY NULLS...")
any_nulls = [i for i in df.columns if df[i].isnull().values.any()]
any_nulls = sorted(any_nulls)
print('\n'.join(any_nulls))
end()

begin()
print("CHECKING FOR COLUMNS WITH ALL NULLS...")
all_nulls = [i for i in df.columns if df[i].isnull().values.all()]
all_nulls = sorted(all_nulls)
print('\n'.join(all_nulls))
end()

df = df.reindex(columns=['pu','time_period','cycle','uuid','key_type','filler1','auth_dept_code','loc_code','last_name','first_name','middle_name','class','whitespace1','dues_rate','home_address','home_city','home_state','home_zip5','home_zip4','member_type','bu','job_title_code','paid_dues','biweekly_wage','filler3','gender','filler4','anniversary','increment_step','filler5','not_in_pay_status','filler6','misc_deduct'])

begin()
print("HASHING THE 'UUID' COLUMN...\n")
df.uuid = df.uuid.apply(lambda x: hashlib.md5(x.encode('utf-8')).hexdigest())

primary_key_check_nulls('uuid')
primary_key_check_repeats('uuid')
primary_key_exit('uuid')
