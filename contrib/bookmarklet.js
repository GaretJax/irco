// Run through http://chriszarate.github.io/bookmarkleter/
var vars = {};
var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {vars[key] = value;});
var command = 'irco-scrape ' + vars['SID'] + ' output/dir';
prompt('To download this search results run the following command in terminal:', command);

