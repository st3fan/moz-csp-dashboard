# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/

FIND_FIRST_SITE_QUERY = "select hostname from sites order by hostname limit 1"

DIRECTIVE_QUERY = "select id,directive from directives where id = %s"

ALL_SITES_QUERY = """
select id,hostname from sites order by hostname
"""

TIMELINE_VIOLATIONS_FOR_HOST_QUERY = """
with filled_dates as (
  select day, 0 as blank_count from
    generate_series(date_trunc('day', now() - interval '28 days')::timestamptz, current_date::timestamptz, '1 day')
      as day
),
report_counts as (
  select date_trunc('day', r.created) as day, count(*) as reports
    from reports r, sites s where r.siteid = s.id and s.hostname = %s
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
    from reports r, sites s, directives d where r.siteid = s.id and s.hostname = %s and r.violateddirectiveid = d.id and d.id = %s
  group by date_trunc('day', r.created)
)
select filled_dates.day, coalesce(report_counts.reports, filled_dates.blank_count) as reports
  from filled_dates
    left outer join report_counts on report_counts.day = filled_dates.day
  order by filled_dates.day;
"""



TOP_VIOLATIONS_QUERY = """
select distinct d.directive, d.id, count(d.directive)
from reports r, sites s, directives d
where r.siteid = s.id and s.hostname = %s and r.violateddirectiveid = d.id
group by d.directive, d.id
order by count(d.directive) desc
"""

TOP_VIOLATIONS_FOR_DOCUMENT_QUERY = """
select distinct r.violateddirectiveid, dir.directive, count(*)
from reports r, documents d, directives dir
where r.documentid = d.id and d.id = %s and r.violateddirectiveid = dir.id
group by r.violateddirectiveid, dir.directive
order by count(*) desc
"""

TOP_BLOCKERS_FOR_SITE_QUERY = """
select distinct b.uri, count(b.uri)
from reports r, blockers b, sites s
where r.siteid = s.id and s.hostname = %s and r.blockerid = b.id
group by b.uri
order by count(b.uri) desc
"""

TOP_BLOCKERS_FOR_DOCUMENT_QUERY = """
select distinct b.uri, count(b.uri)
from reports r, blockers b, documents d
where r.documentid = d.id and d.id = %s and r.blockerid = b.id
group by b.uri
order by count(b.uri) desc
"""

TOP_PAGES_QUERY = """
select distinct d.id, d.uri, count(r.documentid)
from reports r, documents d, sites s
where r.siteid = s.id and s.hostname = %s and r.documentid = d.id
group by d.id, d.uri order by count(r.documentid) desc
"""

TOP_DOCUMENTS_FOR_DIRECTIVE_QUERY = """
select distinct d.id, d.uri, count(r.documentid)
from reports r, documents d, sites s
where r.siteid = s.id and s.hostname = %s and r.documentid = d.id and r.violateddirectiveid = %s
group by d.id, d.uri order by count(r.documentid) desc
"""

USERAGENTS_FOR_SITE_QUERY = """
select distinct ua.id, ua.useragent, count(r.clientuseragent)
from reports r, useragents ua, sites s
where r.siteid = s.id and s.hostname = %s and r.clientuseragent = ua.id
group by ua.id, ua.useragent
order by count(r.clientuseragent) desc
"""

USERAGENTS_FOR_DIRECTIVE_QUERY = """
select distinct ua.id, ua.useragent, count(r.clientuseragent)
from reports r, useragents ua, sites s
where r.siteid = s.id and s.hostname = %s and r.clientuseragent = ua.id and r.violateddirectiveid = %s
group by ua.id, ua.useragent
order by count(r.clientuseragent) desc
"""

FULL_REPORTS_FOR_SITE_DIRECTIVE_DOCUMENT_QUERY = """
select distinct
  doc.uri as document_uri,
  blo.uri as blocked_uri,
  dir.directive as violated_directive,
  pol.policy as original_policy,
  r.scriptsource as script_source,
  r.scriptsample as script_sample
from
  documents doc,
  blockers blo,
  directives dir,
  sites s,
  policies pol,
  reports r
where
  r.siteid = s.id and s.hostname = %s
    and
  r.violateddirectiveid = dir.id and dir.id = %s
    and
  r.documentid = doc.id and doc.id = %s
    and
  r.blockerid = blo.id
    and
  r.originalpolicyid = pol.id
group by
  doc.uri, blo.uri, dir.directive, pol.policy, r.scriptsource, r.scriptsample
"""
