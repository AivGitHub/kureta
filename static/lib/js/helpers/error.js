$(document).ready(function() {
  $('#nav-secret-item').hover(function() {
    var span_list = $(this).find('span');

    span_list.each(function(elem){
      $(this).toggleClass('d-none');
      $(this).toggleClass('d-block');
    });
  },
  function() {
    var span_list = $(this).find('span');

    span_list.each(function(elem){
      $(this).toggleClass('d-none');
      $(this).toggleClass('d-block');
    });
  }
  );
});
