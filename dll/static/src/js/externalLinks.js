import $ from 'jquery'

$('a').each(function() {
    if (this.hostname && this.hostname !== location.hostname) {
        $(this).not(':has(img)').attr("rel","external noopener noreferrer");
    }
})
