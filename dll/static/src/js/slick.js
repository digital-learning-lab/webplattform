import $ from 'jquery';


$('.js-slick-wrapper').slick({
    infinite: true,
    slidesToShow: 3,
    slidesToScroll: 3,
    dots: true,
    autoplay: true,
    responsive: [
        {
            breakpoint: 1490,
            settings: {
                slidesToShow: 2,
                slidesToScroll: 2,
            }
        },
        {
            breakpoint: 920,
            settings: {
                slidesToShow: 1,
                slidesToScroll: 1,
            }
        }
    ]
})
$('.js-testimonials').slick({
    infinite: true,
    slidesToShow: 1,
    slidesToScroll: 1,
    dots: true,
    autoplay: true,
})

