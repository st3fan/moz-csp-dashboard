# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/

FIND_FIRST_SITE_QUERY = "select hostname from site order by hostname limit 1"

DIRECTIVE_QUERY = "select id,value from violateddirective where id = %s"

ALL_SITES_QUERY = """
select id,hostname from site order by hostname
"""

TIMELINE_VIOLATIONS_FOR_HOST_QUERY = """
with filled_dates as (
  select day, 0 as blank_count from
    generate_series(date_trunc('day', now() - interval '28 days')::timestamptz, current_date::timestamptz, '1 day')
      as day
),
report_counts as (
  select date_trunc('day', r.created) as day, count(*) as reports
    from report r, site s where r.siteid = s.id and s.hostname = %s
  group by date_trunc('day', r.created)
)
select filled_dates.day, coalesce(report_counts.reports, filled_dates.blank_count) as reports
  from filled_dates
    left outer join report_counts on report_counts.day = filled_dates.day
  order by filled_dates.day;
"""

TIMELINE_VIOLATIONS_FOR_DIRECTIVE_QUERY = """
with filled_dates as (
  select day, 0 as blank_count from
    generate_series(date_trunc('day', now() - interval '28 days')::timestamptz, current_date::timestamptz, '1 day')
      as day
),
report_counts as (
  select date_trunc('day', r.created) as day, count(*) as reports
    from report r, site s, directives d where r.siteid = s.id and s.hostname = %s and r.violateddirectiveid = d.id and d.id = %s
  group by date_trunc('day', r.created)
)
select filled_dates.day, coalesce(report_counts.reports, filled_dates.blank_count) as reports
  from filled_dates
    left outer join report_counts on report_counts.day = filled_dates.day
  order by filled_dates.day;
"""



TOP_VIOLATIONS_QUERY = """
select distinct vd.value, vd.id, count(vd.value)
from report r, site s, ViolatedDirective vd
where r.siteid = s.id and s.hostname = %s and r.violateddirectiveid = vd.id
group by vd.value, vd.id
order by count(vd.value) desc
"""

TOP_VIOLATIONS_FOR_DOCUMENT_QUERY = """
select distinct r.violateddirectiveid, vd.value, count(*)
from report r, documenturi du, violateddirective vd
where r.documenturiid = du.id and du.id = %s and r.violateddirectiveid = vd.id
group by r.violateddirectiveid, vd.value
order by count(*) desc
"""

TOP_BLOCKERS_FOR_SITE_QUERY = """
select distinct bu.value, count(bu.value)
from report r, blockeduri bu, site s
where r.siteid = s.id and s.hostname = %s and r.blockeduriid = bu.id
group by bu.value
order by count(bu.value) desc
"""

TOP_BLOCKERS_FOR_DOCUMENT_QUERY = """
select distinct bu.value, count(bu.value)
from report r, blockeduri bu, documenturi du
where r.documenturiid = du.id and du.id = %s and r.blockeduriid = bu.id
group by bu.value
order by count(bu.value) desc
"""

TOP_PAGES_QUERY = """
select distinct du.id, du.value, count(r.documenturiid)
from report r, documenturi du, site s
where r.siteid = s.id and s.hostname = %s and r.documenturiid = du.id
group by du.id, du.value order by count(r.documenturiid) desc
"""

TOP_DOCUMENTS_FOR_DIRECTIVE_QUERY = """
select distinct du.id, du.value, count(r.documenturiid)
from report r, documenturi du, site s
where r.siteid = s.id and s.hostname = %s and r.documenturiid = du.id and r.violateddirectiveid = %s
group by du.id, du.value order by count(r.documenturiid) desc
"""

USERAGENTS_FOR_SITE_QUERY = """
select distinct ua.id, ua.value, count(r.useragentid)
from report r, useragent ua, site s
where r.siteid = s.id and s.hostname = %s and r.useragentid = ua.id
group by ua.id, ua.value
order by count(r.useragentid) desc
"""

USERAGENTS_FOR_DIRECTIVE_QUERY = """
select distinct ua.id, ua.value, count(r.useragentid)
from report r, useragent ua, site s
where r.siteid = s.id and s.hostname = %s and r.useragentid = ua.id and r.violateddirectiveid = %s
group by ua.id, ua.value
order by count(r.useragentid) desc
"""

BAD_FULL_REPORTS_FOR_SITE_DIRECTIVE_DOCUMENT_QUERY = """
select distinct
  du.value as document_uri,
  bu.value as blocked_uri,
  vd.value as violated_directive,
  op.value as original_policy,
  sso.value as script_source,
  ssa.value as script_sample
from
  documenturi du,
  blockeduri bu,
  violateddirective vd,
  site s,
  originalpolicy op,
  scriptsource sso,
  scriptsample ssa,
  report r
where
  r.siteid = s.id and s.hostname = %s
    and
  r.violateddirectiveid = vd.id and vd.id = %s
    and
  r.documenturiid = du.id and du.id = %s
    and
  r.blockeduriid = bu.id
    and
  r.originalpolicyid = op.id
    and
  r.scriptsourceid = sso.id
    and
  r.scriptsampleid = ssa.id
group by
  du.value, bu.value, vd.value, op.value, sso.value, ssa.value
"""



FULL_REPORTS_FOR_SITE_DIRECTIVE_DOCUMENT_QUERY = """
select distinct
  du.value as document_uri,
  bu.value as blocked_uri,
  vd.value as violated_directive,
  op.value as original_policy
from
  documenturi du,
  blockeduri bu,
  violateddirective vd,
  site s,
  originalpolicy op,
  report r
where
  r.siteid = s.id and s.hostname = %s
    and
  r.violateddirectiveid = vd.id and vd.id = %s
    and
  r.documenturiid = du.id and du.id = %s
    and
  r.blockeduriid = bu.id
    and
  r.originalpolicyid = op.id
group by
  du.value, bu.value, vd.value, op.value
"""
