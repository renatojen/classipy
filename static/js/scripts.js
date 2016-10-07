jQuery(document).ready(function($) {
   $(".clickable-row").click(function() {
      $("#img_url").val($(this).find("td:first").find("img:first").attr("src"));
      $("#bt_submit").trigger('click');        	
    });
});