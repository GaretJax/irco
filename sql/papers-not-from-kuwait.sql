select p.id, p.title
from publication as p
where p.id not in (
	select distinct p.id
	from publication as p
	join affiliated_author as a on a.publication_id = p.id
	join institution as i on i.id = a.institution_id
	where i.country = 'Kuwait'
)
