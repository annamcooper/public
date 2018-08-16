create table md_phones_3 as(
select
afl_affiliate_id
,cell
,firstname
,lastname
,afl_local as local
,state::varchar
,congressionaldistrict::varchar
,partisanscore::varchar
,source
from md_phones_2
union
select
null as afl_affiliate_id
,cell
,first
,last
,local
,"STATE"
,"CONGRESSIONAL_DISTRICT"::varchar
,partisanship::varchar
,source
from md_phones_1)