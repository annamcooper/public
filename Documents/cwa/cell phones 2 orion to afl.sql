create table md_phones_2 as(
select
afl_affiliate_id
,"Cell" as cell
,firstname
,lastname
,afl_local
,state
,congressionaldistrict
,partisanscore
,"Source" as source
from afl_member_match_032018 a
left join orion_cells_oh_md_20180418 o on afl_affiliate_id::varchar = o."Member_ID"::varchar
where state = 'MD')