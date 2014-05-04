select country, count(*) as papers from (
	select distinct p.id, i.country
	from publication as p
	join affiliated_author as a on a.publication_id = p.id
	join institution as i on i.id = a.institution_id
) as s
group by country
order by papers desc
