-- Selects the number of papers with corresponding author in a given country
-- grouped by that country and by year.

select i.country, p.year, count(*) as papers
from publication as p
join affiliated_author as a on a.publication_id = p.id
join institution as i on a.institution_id = i.id
where a.is_corresponding = 1  -- There is only one corresponding author per publication.
                              -- We don't need to select distinct publications only.
                              -- `1` works on SQLite only, Postgres requires `true` here.
group by i.country, p.year
order by i.country, p.year;
