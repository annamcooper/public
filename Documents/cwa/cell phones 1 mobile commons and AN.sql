create table md_phones_1 as(
select 
"COL0_PHONE_NUMBER" as cell
,"FIRST_NAME" as first
,"LAST_NAME" as last
,"COL33_CWALOCAL" as local
,"STATE"
,"CONGRESSIONAL_DISTRICT"
,"PARTISANSHIP_MODEL" as partisanship
,"Source" as source
from mobile_commons_20180418
where "STATE"= 'MD'
union 
select
"COL12_CELL_PHONE"
,"FIRST_NAME"
,"LAST_NAME"
,"COL9_CWA_LOCAL"
,"STATE"
,"PARTISANSHIP_MODEL"
,"CONGRESSIONAL_DISTRICT"
,source
from action_network_20180418
where "STATE" ='MD'
)