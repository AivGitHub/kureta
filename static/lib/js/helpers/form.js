$(document).ready(function() {
  $('.fa-eye-toggle').on('click', function(event){
    var parent = $(this).parent();
    var input = parent.children('input');
    var farSpan = $(this).children('span');

    if (farSpan.hasClass('fa-eye')) {
      farSpan.removeClass('fa-eye');
      farSpan.addClass('fa-eye-slash');
      input.attr('type', 'password');
    } else {
      farSpan.removeClass('fa-eye-slash');
      farSpan.addClass('fa-eye');
      input.attr('type', 'text');
    }
  });
});
