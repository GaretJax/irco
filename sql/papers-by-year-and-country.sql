-- Selects the number of papers with at least one author in a given country
-- grouped by that country and by year.

select i.country, p.year, count(distinct p.id) as papers
from publication as p
join affiliated_author as a on a.publication_id = p.id
join institution as i on a.institution_id = i.id
where i.country = 'Kuwait'
group by i.country, p.year
order by i.country, p.year;
