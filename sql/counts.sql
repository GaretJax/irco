-- Number of publications (any country)
select count(*) from publication;

-- Number of publications not from Kuwait
select count(*) from publication as p where p.id not in (
	select distinct p.id
	from publication as p
	join affiliated_author as a on a.publication_id = p.id
	join institution as i on i.id = a.institution_id
	where i.country = 'Kuwait'
)

-- Number of publications from kuwait
select count(*) from (
	select distinct p.id
	from publication as p
	join affiliated_author as a on a.publication_id = p.id
	join institution as i on i.id = a.institution_id
	where i.country = 'Kuwait'
) as pubs;
