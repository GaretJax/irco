-- Returns a table with the number of papers with any kuwaiti author,
-- the number of papers with a kuwaiti corresponding author and their ratio,
-- grouped by year.

select an.year, co.papers as corr_papers, an.papers as any_papers, (co.papers + 0.0) / an.papers as fraction
from (
	select i.country, p.year, count(distinct p.id) as papers
	from publication as p
	join affiliated_author as a on a.publication_id = p.id
	join institution as i on a.institution_id = i.id
	group by i.country, p.year
	order by i.country, p.year
) as an
join (
	select i.country, p.year, count(distinct p.id) as papers
	from publication as p
	join affiliated_author as a on a.publication_id = p.id
	join institution as i on a.institution_id = i.id
	where a.is_corresponding = 1
	group by i.country, p.year
	order by i.country, p.year
) as co
on an.country = co.country and an.year = co.year
where an.country = 'Kuwait'
order by an.country, an.year;
