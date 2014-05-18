select py.country, py.year, count(*) as papers from (
	select distinct p.id, p.year, i.country
	from publication as p
	join affiliated_author as a on a.publication_id = p.id
	join institution as i on a.institution_id = i.id
) as py
group by py.year, py.country
order by py.country, py.year;
