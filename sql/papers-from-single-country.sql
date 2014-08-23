with country_counted_publications as (
	select p.id, count(distinct country) as countries from publication as p
	join affiliated_author as a on a.publication_id = p.id
	join institution as i on a.institution_id = i.id
	-- Only include papers with well defined affiliations as we base our results on those as well
	-- and the results would be skewed otherwise
	where country is not null and has_ambiguous_affiliations = false
	group by p.id
), single_country_publications as (
	select p.id, p.year, i.country from country_counted_publications as s
	join publication as p on p.id = s.id
	join affiliated_author as a on a.publication_id = p.id
	join institution as i on a.institution_id = i.id
	where countries=1 and country is not null
	group by p.id, p.year, i.country
)
select count(*), year, country from single_country_publications
where country = 'Qatar' -- Replace with another country or remove the line altogether to get all the results at once.
group by year, country
order by country, year