drop table if exists sexual_harassment_sample_targets_20180706;
create table sexual_harassment_sample_targets_20180706 as 
select
--variables that go into stratification (for readability)
age_bin
,sex_bin
,race_bin
--,q8split

--strata variable
,strata
,strata_id
,count(*) as pop_size
,sum(samp_weight)::float as weighted_pop_size

--edit 25000 for sample_size
,round(count(*)::float / sum(count(*)) over() * 250000) as sample_size

--not needed if no weighting
,round(sum(samp_weight)::float / sum(sum(samp_weight)) over () * 250000) as weighted_sample_size

from sexual_harassment_sample_polling_bins_weights_20180706
group by 1,2,3,4,5 order by 1,2,3,4,5;

--create final sample table
drop table if exists sexual_harassment_sample_final_20180706;
create table sexual_harassment_sample_final_20180706 as
select
	afl_affiliate_id
	, age_bin
	, race_bin
	, sex_bin
	, strata
	, strata_id
	--q8split
from (
select
          a.*
        , row_number() over (partition by a.strata order by random()) as n_size
        , sample_size
        , weighted_sample_size
from sexual_harassment_sample_polling_bins_20180621 a
left join sexual_harassment_sample_targets_20180706 b using (strata)) z
where n_size <= weighted_sample_size
order by random();

-------------PULL STRATA INFO FOR QUOTAS---------- 
select
  strata_id
, strata
, sum(sample_size) as  sample_size
, sum(weighted_sample_size) as weighted_sample_size
 from sexual_harassment_sample_targets_20180706
group by 1,2
order by strata_id;

---pull final sample to send
select
    p.afl_affiliate_id
  , p.firstname
  , p.lastname
  , p.personal_email
  , p.phone
  , s.strata
  , s.strata_id
  , afl_district_or_region
  , afl_local
  , p.addrline1
  , p.addrline2
  , p.city
  , p.state 
  , p.zip
from sexual_harassment_sample_population_depduped_20180621 p 
inner join sexual_harassment_sample_final_20180706 s on p.afl_affiliate_id::float = s.afl_affiliate_id::float
--exclude previously sampled
left join sh_sample1_20180622 f on p.afl_affiliate_id::int = f.afl_affiliate_id::int
where f.afl_affiliate_id is null

select * from sh_sample1_20180622 limit 10
