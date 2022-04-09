$(document).ready(function() {
  try {
    var idUsername = $('#id_username');
    if (idUsername.val().includes('@')) {
      idUsername.next().addClass('d-none');
    }
  } catch {}

  $('.input-field').on('click', function(event) {
    $(this).find('input').focus();
  })

  $('.fa-eye-toggle').on('click', function(event) {
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

  $('#id_username').on('input', function() {
    var val = $(this).val();
    var parentServer = $(this).next();

    if (val.includes('@')) {
      parentServer.addClass('d-none');
    } else {
      parentServer.removeClass('d-none');
    }
  });
});
