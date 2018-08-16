select
null as afl_affiliate_id
,"DWID" as dwid
,"COL12_CELL_PHONE"::varchar as cell
,"COL2_EMAIL" as email
,"FIRST_NAME" as first
,"LAST_NAME" as last
,"COL9_CWA_LOCAL" as local
,"REGISTRATION_ADDRESS_LINE_1" as addr_1
,"REGISTRATION_ADDRESS_LINE_2" as addr_2
,"REGISTRATION_ADDRESS_CITY" as city
,"REGISTRATION_ADDRESS_STATE" as state
,"REGISTRATION_ADDRESS_ZIP"::varchar as zip
,"COUNTY_NAME" as county
,"CONGRESSIONAL_DISTRICT"::varchar as congressional_district
,"STATE" as state
,"PARTISANSHIP_MODEL"::varchar as partisanship
,"BEST_PHONE"::varchar as catalist_phone
,null as member_type
,source
from action_network_20180418
union
select
afl_affiliate_id
,null as dwid
,"Cell"::varchar as cell
,personal_email
,firstname
,lastname
,afl_local
,regaddrline1
,regaddrline2
,regaddrcity
,regaddrstate
,regaddrzip::varchar
,countyname
,congressionaldistrict::varchar
,state
,partisanscore::varchar
,phone::varchar
,'regular' as member_type
,'orion' as source
from afl_member_match_032018 a
left join orion_no_cell o on afl_affiliate_id::varchar = o."Member_ID"::varchar
where state = 'MD'
and "Member_ID" is not null
union
select
afl_affiliate_id
,null as cell
,
,firstname
,lastname
,afl_local
,regaddrline1
,regaddrline2
,regaddrcity
,regaddrstate
,regaddrzip::varchar
,countyname
,congressionaldistrict::varchar
,state
,partisanscore::varchar
,phone::varchar
,'retiree' as member_type
,'orion' as source
from afl_member_match_032018 a
left join orion_md_retirees_no_cell x on afl_affiliate_id::varchar = x."ID"::varchar
where state = 'MD'