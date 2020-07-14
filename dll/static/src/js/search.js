import $ from 'jquery'
import debounce from 'lodash/debounce'
var autocomplete = require('autocomplete.js');

var source = function(query, callback) {
	$.get({
		url: '/suche?q=' + query,
		success: function (data, textStatus, jqXHR) {
			callback(data)
		}
	})
}
var debouncedSource = debounce(source, 500)
autocomplete('#autoComplete', { hint: false }, [
	{
		source: debouncedSource,
		displayKey: 'title',
	}
]).on('autocomplete:selected', function(event, suggestion, dataset, context) {
	document.location = suggestion.url
});
